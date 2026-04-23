from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import date
from db.models import (
    CompanionCustomerFood,
    CompanionPetProductFeeding,
    CompanionPetFood,
    OpdProduct,
    CompanionFeedingGuide,
)

class DashboardRepository:
    """홈 화면 대시보드 구성을 위한 데이터 접근 계층입니다."""

    def __init__(self, db: Session):
        self.db = db

    def get_daily_feeding_stats(self, pet_id: int, target_date: date):
        """특정 날짜의 사료 급여량과 칼로리 합계를 조회합니다."""
        result = (
            self.db.query(
                func.sum(CompanionPetFood.amount).label("total_amount"),
                func.sum(CompanionPetFood.calories).label("total_calories"),
            )
            .filter(
                CompanionPetFood.pet_id == pet_id,
                CompanionPetFood.feeding_date == target_date,
                CompanionPetFood.active == True,
            )
            .first()
        )
        return {
            "total_amount": result.total_amount or 0,
            "total_calories": result.total_calories or 0
        }

    def get_target_calories(self, pet_id: int):
        """최신 추천 섭취량(guide_intake)을 조회합니다."""
        guide = (
            self.db.query(CompanionFeedingGuide)
            .filter(CompanionFeedingGuide.pet_id == pet_id)
            .order_by(CompanionFeedingGuide.guide_date.desc())
            .first()
        )
        return guide.guide_intake if guide and guide.guide_intake else 0

    def get_active_feeding_info(self, pet_id: int):
        """현재 급여 중인 사료 정보(g당 칼로리 등)를 조회합니다."""
        return (
            self.db.query(CompanionPetProductFeeding)
            .options(
                joinedload(CompanionPetProductFeeding.product).joinedload(
                    OpdProduct.product_detail
                )
            )
            .filter_by(pet_id=pet_id, is_feeding_check=True)
            .first()
        )

    def get_food_inventory_gauge(self, pet_id: int):
        """사료 재고율 게이지를 위한 잔여량 및 제품 정보를 조회합니다."""
        result = (
            self.db.query(CompanionCustomerFood, OpdProduct)
            .join(
                CompanionPetProductFeeding,
                CompanionCustomerFood.pet_id == CompanionPetProductFeeding.pet_id,
            )
            .join(
                OpdProduct,
                CompanionPetProductFeeding.product_id == OpdProduct.product_id,
            )
            .filter(
                CompanionCustomerFood.pet_id == pet_id,
                CompanionPetProductFeeding.is_feeding_check == True,
            )
            .first()
        )
        return result
