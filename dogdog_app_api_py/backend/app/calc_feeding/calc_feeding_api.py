from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from backend.app.calc_feeding.repository.guideIntake_repository import get_guide_intake, get_feeding_count, get_one_gram_calories
from backend.dependencies import get_pet_by_id, check_pet_owner, get_current_user
from backend.app.calc_feeding.cal_guideIntake_service import (
    create_feeding_recommendation_service,
    get_one_time_feeding_amount_service,
)
from backend.app.calc_feeding.schemas import (
    CalcFeedingRecommendationResponse,
    GuideIntakeResponse,
    OneTimeFeedingResponse,
)

router = APIRouter(prefix="/api/v1/calc_feeding", tags=["Calc Feeding"])

# 등록
@router.post("/{pet_id}/guide", response_model=CalcFeedingRecommendationResponse, status_code=201)
def create_feeding_recommendation_api(
    pet_id: int,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    result = create_feeding_recommendation_service(
        db=db,
        pet_id=pet_id,
    )

    return JSONResponse(
        status_code=201,
        content={
            "success": True,
            "message": "권장 급여량이 생성되었습니다.",
            "data": result
        }
    )
'''
"data": {
    "pet_id": result["pet_id"],
    "base_intake": result["base_intake"],
    "guide_intake": result["guide_intake"],
    "guide_date": result["guide_date"].isoformat() if result["guide_date"] else None,
    "feeding_count": result["feeding_count"],
    "base_per_meal_g": result["base_per_meal_g"],
    "guide_per_meal_g": result["guide_per_meal_g"],
    "adjustment_ratio": result["adjustment_ratio"],
    "adjustment_rate": result["adjustment_rate"],
    "adjustment_reason": result["adjustment_reason"],
    "recommend_kcal": result["recommend_kcal"],
    "goal_weight": result["goal_weight"],
}
'''

# 조회
@router.get("/{pet_id}/guide", response_model=GuideIntakeResponse)
def read_guide_intake(
        pet_id: int,
        customer_id: int = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
    try:
        # 유효하지 않은 반려견id인 경우
        if pet_id <= 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_PET_ID",
                    "message": "유효한 반려견 ID가 필요합니다."
                }
            )
        
        # 존재하지 않는 반려견일때
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
        
        # 반려견 권한 확인
        if not check_pet_owner(db, pet_id, customer_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
            )

        # 추천 테이블 조회
        guide = get_guide_intake(db=db, pet_id=pet_id)

        # 권장급여량이 없는 경우
        if guide is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "FEEDING_RECOMMENDATION_NOT_FOUND",
                    "message": "저장된 권장 급여량 정보가 없습니다."
                }
            )

        # 하루 먹이는 횟수(feeding_count)
        feeding_count = get_feeding_count(db=db, pet_id=pet_id)

        adjusted_per_meal = guide.guide_intake/feeding_count

        # 제품 칼로리 조회 및 계산 로직 추가
        one_gram_calories = get_one_gram_calories(db=db, pet_id=pet_id)
        kcal_per_kg = 0
        daily_total_kcal = 0
        
        if one_gram_calories:
            kcal_per_kg = float(one_gram_calories) * 1000
            daily_total_kcal = float(guide.guide_intake) * float(one_gram_calories)

        data = {
                "pet_id": guide.pet_id,
                "base_daily_food_g": float(guide.base_intake),
                "adjusted_daily_food_g": float(guide.guide_intake),
                "adjusted_per_meal_g": f"{adjusted_per_meal:.1f}",
                "feeding_count": feeding_count,
                "recommended_at": guide.guide_date,
                "kcal_per_kg": int(kcal_per_kg),
                "daily_total_kcal": round(daily_total_kcal, 1)
            }

        return {
            "success": True,
            "message": "권장 급여량을 조회했습니다.",
            "data": data
        }

    except Exception as e:
        print("권장 급여량 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "GUIDE_INTAKE_READ_FAILED",
                "message": "권장 급여량 조회에 실패했습니다."
            }
        )

# 1회 권장 급여량 조회
@router.get("/{pet_id}/one-time", response_model=OneTimeFeedingResponse)
def get_one_time_feeding_amount(
    pet_id: int,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    [1회 권장 급여량 조회] 일일 권장 급여량을 급여 횟수로 나누어 반환합니다.
    """
    # 1. 권한 확인
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    # 2. 서비스 호출
    result = get_one_time_feeding_amount_service(db, pet_id)

    return {
        "success": True,
        "message": "1회 권장 급여량을 조회했습니다.",
        "data": result
    }
    