from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date, timedelta

from db.db import get_db
from app.pets.schemas import PetRegisterRequest, PetRegisterResponse
from app.pets.service.pet_service import PetService
from app.pets.service.pet_info_service import PetService as PetInfoService
from app.auth.security import get_current_user

from app.pets.repository.petFood_repository import end_pet_food
from app.pets.service.petFood_service import create_pet_food, update_pet_food
from app.pets.repository.petFoodDetail_repository import get_current_pet_food_detail, get_pet_by_id

router = APIRouter(prefix="/api/v1/pets", tags=["Pets"])

# 반려견 최초 등록 ------------------------------------------------------------------
@router.post("", response_model=PetRegisterResponse, status_code=201)
def register_pet(
    request: PetRegisterRequest,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    service = PetService(db)
    result = service.register_pet(customer_id, request)
    return JSONResponse(status_code=201, content=result)


# 급여사료 등록 ------------------------------------------------------------------
class PetFoodCreateRequest(BaseModel):
    customer_id: int | None = Field(default=None, description="임시용 고객 ID")
    product_id: int = Field(..., description="상품 ID")
    total_weight: int = Field(..., gt=0, description="남은 급여 가능량(g)")
    # left_intake: int = Field(..., ge=0, description="남은 급여 가능량(g)")

@router.post("/{pet_id}/pet_food")
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
        db.commit()
        db.refresh(result)

        return {
            "success": True,
            "message": "급여 사료가 등록되었습니다.",
            "data": result
        }

    except ValueError as e:
        db.rollback()
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
        db.rollback()
        print("급여 사료 등록 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_FOOD_CREATE_FAILED",
                "message": "사료 정보 저장에 실패했습니다."
            }
        )
    
# 급여사료 수정 ------------------------------------------------------------------
class PetFoodUpdateRequest(BaseModel):
    product_id: int = Field(..., description="새로 급여할 상품 ID")
    effective_date: date = Field(..., description="새 사료 급여 시작일")
    total_weight: int = Field(..., gt=0, description="현재 남은 사료량(g)")


@router.patch("/pets/{pet_id}/pet_food")
def patch_pet_food(
    customer_id: int,
    pet_id: int,
    body: PetFoodUpdateRequest,
    db: Session = Depends(get_db),
):
# def patch_pet_food(
#     pet_id: int,
#     body: PetFoodUpdateRequest,
#     db: Session = Depends(get_db),
#     customer_id: int = Depends(get_current_user),
# ):
    try:
        result = update_pet_food(
            db=db,
            customer_id=customer_id,
            pet_id=pet_id,
            product_id=body.product_id,
            effective_date=body.effective_date,
            total_weight=body.total_weight,
        )

        db.commit()

        return {
            "success": True,
            "message": "급여사료 정보가 수정되었습니다.",
            "data": result,
        }

    except ValueError as e:
        db.rollback()
        error_code = str(e)

        error_map = {
            "INVALID_PET_ID": (400, "유효하지 않은 반려견 ID입니다."),
            "INVALID_PRODUCT_ID": (400, "유효하지 않은 상품 ID입니다."),
            "INVALID_EFFECTIVE_DATE": (400, "유효하지 않은 수정 기준일입니다."),
            "INVALID_TOTAL_WEIGHT": (400, "유효하지 않은 사료 잔여량입니다."),
            "FORBIDDEN": (403, "해당 반려견에 대한 권한이 없습니다."),
            "PET_NOT_FOUND": (404, "반려견이 존재하지 않습니다."),
            "PRODUCT_NOT_FOUND": (404, "상품이 존재하지 않거나 비활성 상태입니다."),
            "PET_FOOD_NOT_FOUND": (404, "기존 급여사료 정보가 존재하지 않습니다."),
        }

        status_code, message = error_map.get(
            error_code,
            (400, "잘못된 요청입니다."),
        )

        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error_code": error_code,
                "message": message,
            },
        )

    except Exception as e:
        db.rollback()
        print("급여사료 수정 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )