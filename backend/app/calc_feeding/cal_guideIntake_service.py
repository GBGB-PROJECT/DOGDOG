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
from app.calc_feeding.repository.guideIntake_repository import get_guide_intake, get_one_gram_calories

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
        daily_total_kcal=recommend_kcal,
        commit=commit,
    )

    # 추가: 제품 칼로리 조회 및 계산
    one_gram_calories = get_one_gram_calories(db=db, pet_id=pet_id)
    kcal_per_kg = 0
    daily_total_kcal = 0
    
    if one_gram_calories:
        kcal_per_kg = float(one_gram_calories) * 1000
        daily_total_kcal = float(recommendation.guide_intake) * float(one_gram_calories)

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
        "kcal_per_kg": int(kcal_per_kg),
        "daily_total_kcal": round(daily_total_kcal, 1),
    }
def get_one_time_feeding_amount_service(db: Session, pet_id: int):
    """
    1회 권장 급여량 계산 서비스
    """
    # 1. 권장 급여량 조회 (Feeding Guide)
    guide = get_guide_intake(db, pet_id)
    if not guide:
        raise HTTPException(
            status_code=404,
            detail={
                "success": False,
                "error_code": "FEEDING_GUIDE_NOT_FOUND",
                "message": "저장된 권장 급여량 정보가 없습니다. 먼저 AI 추천을 실행해 주세요."
            }
        )

    # 2. 급여 횟수 조회 (Pet)
    feeding_count = get_feeding_count(db, pet_id)
    
    # 방어 로직: feeding_count가 없거나 0인 경우 기본값 1 적용 또는 에러 처리
    if feeding_count is None or feeding_count <= 0:
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_code": "INVALID_FEEDING_COUNT",
                "message": "반려견의 하루 급여 횟수 설정이 올바르지 않습니다. (현재: 0 또는 None)"
            }
        )

    # 3. 1회 급여량 계산
    one_time_intake = round(guide.guide_intake / feeding_count, 2)

    return {
        "pet_id": pet_id,
        "guide_intake": guide.guide_intake,
        "feeding_count": feeding_count,
        "one_time_intake": one_time_intake
    }

def get_feeding_guide_summary_service(db: Session, pet_id: int):
    """
    대시보드 등 타 도메인에서 참조하기 위한 권장 급여 요약 정보를 반환합니다.
    사료 정보와 독립적인 목표 칼로리(daily_total_kcal)를 포함합니다.
    """
    guide = get_guide_intake(db, pet_id)
    if not guide:
        return None
        
    one_gram_calories = get_one_gram_calories(db, pet_id)
    daily_total_kcal = 0
    if one_gram_calories:
        daily_total_kcal = float(guide.guide_intake) * float(one_gram_calories)
        
    return {
        "pet_id": pet_id,
        "guide_intake": guide.guide_intake,
        "daily_total_kcal": daily_total_kcal,
        "guide_date": guide.guide_date
    }
