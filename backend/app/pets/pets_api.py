from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from database.db import get_db
from backend.app.domains.pets.repository.petFood_repository import end_pet_food
from backend.app.domains.pets.petFood_service import create_pet_food
from backend.app.domains.pets.repository.petFoodDetail_repository import get_current_pet_food_detail, get_pet_by_id
# from backend.app.core.auth import get_current_customer_id  # 가정: 토큰에서 customer_id 추출
from datetime import date, timedelta

router = APIRouter(tags=["pets"])

# 급여사료 등록 ------------------------------------------------------------------
class PetFoodCreateRequest(BaseModel):
    customer_id: int | None = Field(default=None, description="임시용 고객 ID")
    product_id: int = Field(..., description="상품 ID")
    total_weight: int = Field(..., gt=0, description="남은 급여 가능량(g)")
    # left_intake: int = Field(..., ge=0, description="남은 급여 가능량(g)")

@router.post("/pets/{pet_id}/pet_food")
def register_pet_food(
    pet_id: int,
    body: PetFoodCreateRequest,
    db: Session = Depends(get_db),
    # customer_id: int = Depends(get_current_customer_id)
):
    """
    로그인한 사용자의 반려견에게 현재 급여 중인 사료를 등록한다.
    기존 활성 사료가 있으면 종료 처리 후 새 사료를 등록한다.
    """
    try:
        customer_id = body.customer_id  # 토큰 받기전 임시
        product_id = body.product_id
        total_weight = body.total_weight

        result = create_pet_food(
            db=db,
            customer_id=customer_id,
            pet_id=pet_id,
            product_id=product_id,
            total_weight=total_weight,
        )

        return {
            "success": True,
            "message": "급여 사료가 등록되었습니다.",
            "data": result
        }

    except ValueError as e:
        error_code = str(e)

        error_map = {
            "PRODUCT_ID_REQUIRED": (400, "상품 ID는 필수입니다."),
            "TOTAL_WEIGHT_REQUIRED": (400, "총 무게는 필수입니다."),
            # "LEFT_INTAKE_REQUIRED": (400, "사료 잔여량은 필수입니다."),
            "INVALID_TOTAL_WEIGHT": (422, "총 무게는 0보다 커야 합니다."),
            "HIGH_TOTAL_WEIGHT": (422, f"잔여량은 상품 총무게보다 작거나 같아야합니다."),
            # "INVALID_LEFT_INTAKE": (422, "사료 잔여량은 0 이상이어야 합니다."),
            "PET_NOT_FOUND": (404, "존재하지 않는 반려견입니다."),
            "PRODUCT_NOT_FOUND": (404, "존재하지 않는 사료입니다."),
            "FORBIDDEN_PET_ACCESS": (403, "해당 반려견에 대한 권한이 없습니다."),
            "PRODUCT_CALORIES_NOT_FOUND": (404, "상품 칼로리 정보가 없습니다."),
            "EXIST_PET_FOOD": (409, "기존의 상품과 같은 상품입니다.")
        }

        status_code, message = error_map.get(
            error_code,
            (400, "잘못된 요청입니다.")
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error_code": error_code,
                "message": message
            }
        )

    except Exception as e:
        print("급여 사료 등록 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_FOOD_CREATE_FAILED",
                "message": "사료 정보 저장에 실패했습니다."
            }
        )

# 급여사료 상세조회 --------------------------------------------------------------    
@router.get("/pets/{pet_id}/pet_food")
def read_current_pet_food_detail(
    pet_id: int,
    db: Session = Depends(get_db)
):
    try:
        # 명세서 기준: pet_id 필수
        # if pet_id is None:
        #     return JSONResponse(
        #         status_code=400,
        #         content={
        #             "success": False,
        #             "error_code": "PET_ID_REQUIRED",
        #             "message": "반려견 ID는 필수입니다."
        #         }
        #     )

        pet_food = get_current_pet_food_detail(db=db, pet_id=pet_id)

        if pet_food is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "CURRENT_FEEDING_PRODUCT_NOT_FOUND",
                    "message": "현재 급여 중인 사료 정보가 없습니다."
                }
            )

        total_weight = pet_food.total_weight or 0  # 급여중인 사료의 첫 잔여량 or 사료 총량
        total_intake = pet_food.total_intake or 0  # 누적 급여량
        product_weight = pet_food.product_weight  # 실제 급여 사료 총량 
        left_food_count = pet_food.left_food_count

        left_weight = total_weight - total_intake

        # 음수(-) 방지
        if left_weight < 0:
            left_weight = 0

        feeding_count = pet_food.feeding_count  # 반려견 급여횟수
        left_food_count = pet_food.left_food_count  # 예상급여잔여 횟수

        expected_left_days = None
        expected_last_day = None
        # left_day = left_food_count/feeding_count
        # last_day = date.today() + left_day -1

        if left_food_count is not None and feeding_count > 0:
            expected_left_days = left_food_count / feeding_count
            expected_last_day = (
                date.today() + timedelta(days=int(expected_left_days) - 1)
            )
            # .isoformat()
        return {
            "success": True,
            "message": "현재 급여 중인 사료 정보를 조회했습니다.",
            "data": {
                "pet_id": pet_food.pet_id,
                "product_id": pet_food.product_id,
                "product_name": pet_food.product_name,

                "total_weight": total_weight,
                "product_weight": product_weight,
                "left_weight": left_weight,

                "is_feeding_check": pet_food.is_feeding_check,

                "expected_left_days": expected_left_days,
                "expected_last_day": expected_last_day
            }
        }
    
    except ValueError as e:
        if str(e) == "PET_NOT_FOUND":
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_NOT_FOUND",
                    "message": "존재하지 않는 반려견입니다."
                }
            )

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error_code": "BAD_REQUEST",
                "message": str(e)
            }
        )


    except Exception as e:
        print(f"급여 사료 상세 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_PRODUCT_FEEDING_READ_FAILED",
                "message": "급여 사료 정보 조회에 실패했습니다."
            }
        )
    
# 급여사료 삭제 ------------------------------------------------------------------
@router.delete("/pets/{pet_id}/pet_food")
def remove_pet_food(
    pet_id: int,
    db: Session = Depends(get_db)
):
    try:
        # 1. 반려견 존재 확인
        pet = get_pet_by_id(db=db, pet_id=pet_id)
        if pet is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_NOT_FOUND",
                    "message": "존재하지 않는 반려견입니다."
                }
            )

        # 2. 권한 확인
        # TODO:
        # 현재 로그인한 사용자가 해당 pet의 보호자인지 확인하는 로직 추가
        # 예:
        # current_user = Depends(get_current_user)
        # if not check_pet_permission(db, current_user.customer_id, pet_id):
        #     return JSONResponse(
        #         status_code=403,
        #         content={
        #             "success": False,
        #             "error_code": "FORBIDDEN_PET_ACCESS",
        #             "message": "해당 반려견에 대한 권한이 없습니다."
        #         }
        #     )

        # 3. 현재 급여 사료 삭제(논리 삭제)
        # active_food = get_active_pet_food(db=db, pet_id=pet_id)
        # deleted_pet_food = deactivate_pet_food(
        #     db=db,
        #     pet_food=active_food,
        #     feeding_false_date=date.today()
        # )        
        # # = deactivate_pet_food(db=db, pet_id=pet_id)

        deactivate_pet_food = end_pet_food(db, pet_id)
        db.commit()

        if deactivate_pet_food is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_PRODUCT_FEEDING_NOT_FOUND",
                    "message": "삭제할 급여 사료 정보가 없습니다."
                }
            )

        # 4. 성공 응답
        return {
            "success": True,
            "message": "급여 사료 정보가 삭제되었습니다.",
            "data": {
                "pet_id": deactivate_pet_food.pet_id,
                "is_feeding_check": deactivate_pet_food.is_feeding_check,
                "feeding_false_date": str(deactivate_pet_food.feeding_false_date)
            }
        }

    except Exception as e:
        print(f"급여 사료 삭제 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_PRODUCT_FEEDING_DELETE_FAILED",
                "message": "급여 사료 정보 삭제에 실패했습니다."
            }
        )
