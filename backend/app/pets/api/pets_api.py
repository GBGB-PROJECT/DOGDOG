from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import date, timedelta

from db.db import get_db
from app.pets.schemas import PetRegisterRequest, PetRegisterResponse
from app.pets.service.pet_service import PetService
from app.pets.service.pet_info_service import PetService as PetInfoService
from dependencies import get_current_user, check_pet_owner

from app.pets.repository.petFood_repository import end_pet_food
from app.pets.service.petFood_service import create_pet_food, update_pet_food
from app.pets.repository.petFoodDetail_repository import (
    get_current_pet_food_detail,
    get_pet_by_id,
)
from app.pets.service.petFood_service import read_recommended_foods

router = APIRouter(prefix="/api/v1/pets", tags=["Pets"])


# 1. 반려견 최초 등록 --------------------------------------------------------------
@router.post("", response_model=PetRegisterResponse, status_code=201)
def register_pet(
    request: PetRegisterRequest,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = PetService(db)
    result = service.register_pet(customer_id, request)
    return JSONResponse(status_code=201, content=result)


# 2. 급여사료 등록 -----------------------------------------------------------------
class PetFoodCreateRequest(BaseModel):
    product_id: int = Field(..., description="상품 ID")
    total_weight: int = Field(..., gt=0, description="남은 급여 가능량(g)")


@router.post("/{pet_id}/pet_food")
def register_pet_food(
    pet_id: int,
    body: PetFoodCreateRequest,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    """
    로그인한 사용자의 반려견에게 현재 급여 중인 사료를 등록한다.
    기존 활성 사료가 있으면 종료 처리 후 새 사료를 등록한다.
    """
    try:
        result = create_pet_food(
            db=db,
            customer_id=customer_id,
            pet_id=pet_id,
            product_id=body.product_id,
            total_weight=body.total_weight,
        )

        # db.commit()
        # db.refresh(result)

        return {
            "success": True,
            "message": "급여 사료가 등록되었습니다.",
            "data": jsonable_encoder(result),  # 🔥 500 에러 방지용 안전 직렬화
        }

    except ValueError as e:
        db.rollback()
        error_code = str(e)
        error_map = {
            "PRODUCT_ID_REQUIRED": (400, "상품 ID는 필수입니다."),
            "TOTAL_WEIGHT_REQUIRED": (400, "총 무게는 필수입니다."),
            "INVALID_TOTAL_WEIGHT": (422, "총 무게는 0보다 커야 합니다."),
            "HIGH_TOTAL_WEIGHT": (422, "잔여량은 상품 총무게보다 작거나 같아야합니다."),
            "PET_NOT_FOUND": (404, "존재하지 않는 반려견입니다."),
            "PRODUCT_NOT_FOUND": (404, "존재하지 않는 사료입니다."),
            "FORBIDDEN_PET_ACCESS": (403, "해당 반려견에 대한 권한이 없습니다."),
            "PRODUCT_CALORIES_NOT_FOUND": (404, "상품 칼로리 정보가 없습니다."),
            "EXIST_PET_FOOD": (409, "기존의 상품과 같은 상품입니다."),
        }
        status_code, message = error_map.get(error_code, (400, "잘못된 요청입니다."))
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "error_code": error_code, "message": message},
        )

    except Exception as e:
        db.rollback()
        print("급여 사료 등록 실패:", e)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_FOOD_CREATE_FAILED",
                "message": "사료 정보 저장에 실패했습니다.",
            },
        )


# 3. 급여사료 수정 -----------------------------------------------------------------
class PetFoodUpdateRequest(BaseModel):
    product_id: int = Field(..., description="새로 급여할 상품 ID")
    effective_date: date = Field(..., description="새 사료 급여 시작일")
    total_weight: int = Field(..., gt=0, description="현재 남은 사료량(g)")


@router.patch("/{pet_id}/pet_food")  # 🔥 URL 중복 오류 수정 (/pets 제거)
def patch_pet_food(
    pet_id: int,
    body: PetFoodUpdateRequest,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    try:
        result = update_pet_food(
            db=db,
            customer_id=customer_id,
            pet_id=pet_id,
            product_id=body.product_id,
            effective_date=body.effective_date,
            total_weight=body.total_weight,
        )

        # 수정 API는 개별 트랜잭션이므로 커밋 유지
        db.commit()

        return {
            "success": True,
            "message": "급여사료 정보가 수정되었습니다.",
            "data": jsonable_encoder(result),  # 🔥 안전 직렬화
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
        status_code, message = error_map.get(error_code, (400, "잘못된 요청입니다."))
        return JSONResponse(
            status_code=status_code,
            content={"success": False, "error_code": error_code, "message": message},
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


# 4. 급여사료 상세조회 --------------------------------------------------------------
@router.get("/{pet_id}/pet_food")
def read_current_pet_food_detail(
    pet_id: int,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    try:
        if not check_pet_owner(db, pet_id, customer_id):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error_code": "FORBIDDEN_PET_ACCESS",
                    "message": "해당 반려견에 대한 권한이 없습니다.",
                },
            )

        pet_food = get_current_pet_food_detail(db=db, pet_id=pet_id)

        if pet_food is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "CURRENT_FEEDING_PRODUCT_NOT_FOUND",
                    "message": "현재 급여 중인 사료 정보가 없습니다.",
                },
            )

        total_weight = pet_food.total_weight or 0
        total_intake = pet_food.total_intake or 0
        product_weight = pet_food.product_weight

        left_weight = total_weight - total_intake
        if left_weight < 0:
            left_weight = 0

        feeding_count = pet_food.feeding_count
        left_food_count = pet_food.left_food_count

        expected_left_days = None
        expected_last_day = None

        if (
            left_food_count is not None
            and feeding_count is not None
            and feeding_count > 0
        ):
            expected_left_days = left_food_count / feeding_count
            expected_last_day = date.today() + timedelta(
                days=int(expected_left_days) - 1
            )

        return {
            "success": True,
            "message": "현재 급여 중인 사료 정보를 조회했습니다.",
            "data": {
                "pet_id": pet_food.pet_id,
                "product_id": pet_food.product_id,
                "product_thumbnail": pet_food.thumbnail,
                "product_brand": pet_food.brand,
                "product_name": pet_food.product_name,
                "total_weight": total_weight,
                "product_weight": product_weight,
                "left_weight": left_weight,
                "is_feeding_check": pet_food.is_feeding_check,
                "expected_left_days": expected_left_days,
                "expected_last_day": expected_last_day,
            },
        }

    except ValueError as e:
        if str(e) == "PET_NOT_FOUND":
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_NOT_FOUND",
                    "message": "존재하지 않는 반려견입니다.",
                },
            )
        return JSONResponse(
            status_code=400,
            content={"success": False, "error_code": "BAD_REQUEST", "message": str(e)},
        )

    except Exception as e:
        print(f"급여 사료 상세 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_PRODUCT_FEEDING_READ_FAILED",
                "message": "급여 사료 정보 조회에 실패했습니다.",
            },
        )


# 5. 급여사료 삭제 ------------------------------------------------------------------
@router.delete("/{pet_id}/pet_food")
def remove_pet_food(
    pet_id: int,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    try:
        pet = get_pet_by_id(db=db, pet_id=pet_id)
        if pet is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_NOT_FOUND",
                    "message": "존재하지 않는 반려견입니다.",
                },
            )

        if not check_pet_owner(db, pet_id, customer_id):
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error_code": "FORBIDDEN_PET_ACCESS",
                    "message": "해당 반려견에 대한 권한이 없습니다.",
                },
            )

        deactivate_pet_food = end_pet_food(db, pet_id)
        db.commit()

        if deactivate_pet_food is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "PET_PRODUCT_FEEDING_NOT_FOUND",
                    "message": "삭제할 급여 사료 정보가 없습니다.",
                },
            )

        return {
            "success": True,
            "message": "급여 사료 정보가 삭제되었습니다.",
            "data": {
                "pet_id": deactivate_pet_food.pet_id,
                "is_feeding_check": deactivate_pet_food.is_feeding_check,
                "feeding_false_date": str(deactivate_pet_food.feeding_false_date),
            },
        }

    except Exception as e:
        db.rollback()
        print(f"급여 사료 삭제 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_PRODUCT_FEEDING_DELETE_FAILED",
                "message": "급여 사료 정보 삭제에 실패했습니다.",
            },
        )


# 6. 반려견 정보 리스트 조회 ------------------------------------------------------
@router.get("")
async def get_pet_info(
    customer_id: int = Depends(get_current_user), db: Session = Depends(get_db)
):
    try:
        results = PetInfoService.get_pet_list_with_profile(db, customer_id)

        if not results:
            raise HTTPException(
                status_code=404, detail="해당 고객의 반려동물이 없습니다."
            )

        return {
            "status": "success",
            "message": "고객 반려동물 추출 완료",
            "data": jsonable_encoder(results),  # 🔥 여기서도 안전 변환!
        }

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"반려견 목록 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_INFO_READ_FAILED",
                "message": "반려견 목록 조회에 실패했습니다.",
            },
        )
    
# 추천 사료 조회 --------------------------------------------------------------------------
@router.get("/{pet_id}/recommended-foods")
def get_recommended_pet_foods(
    customer_id: int,
    pet_id: int,
    db: Session = Depends(get_db),
    # customer_id: int = Depends(get_current_user),
):
    try:
        result = read_recommended_foods(
            db=db,
            customer_id=customer_id,
            pet_id=pet_id,
        )

        return {
            "success": True,
            "data": result,
        }

    except ValueError as e:
        error_code = str(e)

        error_map = {
            "INVALID_PET_ID": (400, "유효하지 않은 반려견 ID입니다."),
            "FORBIDDEN": (403, "해당 반려견에 대한 접근 권한이 없습니다."),
            "PET_NOT_FOUND": (404, "반려견이 존재하지 않습니다."),
            "CURRENT_FOOD_NOT_FOUND": (404, "현재 급여 중인 사료가 없습니다."),
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
        print("추천사료 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )
