from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from backend.app.calc_feeding.guideIntake_repository import get_guide_intake, get_feeding_count

router = APIRouter(tags=["calc_feeding"])

@router.get("/pets/{pet_id}/cal_feeding/guide")
def read_guide_intake(
        pet_id: int,
        db: Session = Depends(get_db)
    ):
    try:
        # 추천 테이블 조회
        guide = get_guide_intake(db=db, pet_id=pet_id)
        # pet_id, base_intake, guide_intake, guide_date

        # 하루 먹이는 횟수(feeding_count)
        feeding_count = get_feeding_count(db=db, pet_id=pet_id)

        adjusted_per_meal = guide.guide_intake/feeding_count

        data = {
                "pet_id":guide.pet_id,

                "base_daily_food_g": guide.base_intake,
                # "base_per_meal_g":guide.base_intake,

                "adjusted_daily_food_g":guide.guide_intake,
                "adjusted_per_meal_g":f"{adjusted_per_meal:.1f}",

                "recommended_at":guide.guide_date
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
                "error_code": "PRODUCT_LIST_READ_FAILED",
                "message": "권장 급여량 조회에 실패했습니다."
            }
        )
    