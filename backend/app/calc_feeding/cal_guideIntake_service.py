from datetime import date
from math import pow

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.calc_feeding.repository.cal_guideIntake_repository import (
    get_cal_features,
    get_adult_stand_m,
    get_feeding_count,
    create_feeding_recommendation,
)

# from app.ai.inference.predictor import predict_recommend_g
from app.ai.recommend import predict_recommend_g

# 생일 -> 개월수
def calculate_age_months(birth_day: date) -> int:
    today = date.today()
    months = (today.year - birth_day.year) * 12 + (today.month - birth_day.month)

    # day 차이까지 반영하고 싶으면 추가 가능
    if today.day < birth_day.day:
        months -= 1

    return max(months, 0)


# 계절 변수 정의
def get_season_value() -> int:
    """
    season 값을 아직 DB에서 안 받으므로 임시 고정값.
    추후 날짜 기준 계산 또는 별도 로직으로 교체.
    예: 봄=1, 여름=2, 가을=3, 겨울=4
    """
    month = date.today().month

    if month in [3, 4, 5]:
        return 1
    elif month in [6, 7, 8]:
        return 2
    elif month in [9, 10, 11]:
        return 3
    else:
        return 4


# poop로그가 없을때 default = 3(정상)
def normalize_fcs(fcs: int | None) -> int:
    """
    poop 로그가 없을 때 기본값 처리
    """
    if fcs is None:
        return 3
    return int(fcs)

def build_adjustment_reason(adjustment_rate: float) -> str:
    if adjustment_rate > 0:
        return "반려견 상태를 반영해 권장 급여량을 소폭 증량했습니다."
    elif adjustment_rate < 0:
        return "반려견 상태를 반영해 권장 급여량을 소폭 감량했습니다."
    return "기본 급여량 기준으로 권장 급여량을 산정했습니다."

# AI 권장 급여량 계산
def create_feeding_recommendation_service(db: Session, pet_id: int, commit: bool = True):
    if pet_id <= 0:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "PET_ID_REQUIRED",
                "message": "반려견 ID는 필수입니다."
            }
        )

    cal_features = get_cal_features(db=db, pet_id=pet_id)
    if cal_features is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "PET_OR_FEEDING_DATA_NOT_FOUND",
                "message": "급여 추천 계산에 필요한 반려견 또는 급여 데이터가 없습니다."
            }
        )

    adult_stand_m = get_adult_stand_m(db=db, pet_id=pet_id)
    if adult_stand_m is None:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "ADULT_STANDARD_NOT_FOUND",
                "message": "성견 기준 월 정보를 찾을 수 없습니다."
            }
        )

    feeding_count = get_feeding_count(db=db, pet_id=pet_id)
    if feeding_count is None or feeding_count <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_FEEDING_COUNT",
                "message": "급여 횟수는 1 이상이어야 합니다."
            }
        )

    if cal_features["weight"] is None or float(cal_features["weight"]) <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_WEIGHT",
                "message": "몸무게는 0보다 커야 합니다."
            }
        )

    if cal_features["food_kcal"] is None or float(cal_features["food_kcal"]) <= 0:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "FOOD_KCAL_NOT_FOUND",
                "message": "사료 칼로리 정보가 없습니다."
            }
        )

    age = calculate_age_months(cal_features["birth_day"])
    neutered = int(bool(cal_features["is_neutered"]))
    weight = float(cal_features["weight"])
    bcs = int(cal_features["bcs"])
    activity_level = int(cal_features["daily_walks"])
    season = get_season_value()
    fcs = normalize_fcs(cal_features["fcs"])
    food_kcal = float(cal_features["food_kcal"])

    try:
        guide_feeding = predict_recommend_g(
            age=age,
            neutered=neutered,
            weight=weight,
            bcs=bcs,
            activity_level=activity_level,
            season=season,
            fcs=fcs,
            adult_stand_m=int(adult_stand_m),
            food_kcal=food_kcal,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "AI_ADJUSTMENT_FAILED",
                "message": f"AI 급여 보정에 실패했습니다. {str(e)}"
            }
        )
    
    '''
    {
        'base_g': 76.04, 
        'adjustment_ratio': 1.018, 
        'recommend_g': 77.41, 
        'recommend_kcal': 310.02, 
        'goal_weight': 6.82
    }
    '''

    try:
        base_daily_food_g = round(float(guide_feeding["base_g"]), 2)
        adjusted_daily_food_g = round(float(guide_feeding["recommend_g"]), 2)
        recommend_kcal = round(float(guide_feeding["recommend_kcal"]), 2)
        goal_weight = round(float(guide_feeding["goal_weight"]), 2)
        adjustment_ratio = float(guide_feeding["adjustment_ratio"])
    except KeyError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "AI_RESPONSE_INVALID",
                "message": f"AI 응답 형식이 올바르지 않습니다. 누락된 키: {str(e)}"
            }
        )

    base_per_meal_g = round(base_daily_food_g / feeding_count, 2)
    adjusted_per_meal_g = round(adjusted_daily_food_g / feeding_count, 2)

    adjustment_rate = round((adjustment_ratio - 1) * 100, 1)
    adjustment_reason = build_adjustment_reason(adjustment_rate)

    # DB에 등록
    recommendation = create_feeding_recommendation(
        db=db,
        pet_id=pet_id,
        base_intake=base_daily_food_g,
        guide_intake=adjusted_daily_food_g,
        commit=commit,
    )

    return {
        "pet_id": pet_id,
        "base_intake": recommendation.base_intake,
        "guide_intake": recommendation.guide_intake,
        "guide_date": recommendation.guide_date.isoformat() if recommendation.guide_date else None,
        "feeding_count": feeding_count,
        "base_per_meal_g": round(base_daily_food_g / feeding_count, 2),
        "guide_per_meal_g": round(adjusted_daily_food_g / feeding_count, 2),
        "adjustment_ratio": adjustment_ratio,
        "adjustment_rate": round((adjustment_ratio - 1) * 100, 1),
        "adjustment_reason": build_adjustment_reason(adjustment_ratio),
        "recommend_kcal": round(recommend_kcal, 2),
        "goal_weight": round(goal_weight, 2),
    }