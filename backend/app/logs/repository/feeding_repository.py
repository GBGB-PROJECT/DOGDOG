from sqlalchemy.orm import Session, joinedload
from sqlalchemy import text, func
from db.models import (
    CompanionButler,
    CompanionCustomerFood,
    CompanionPetProductFeeding,
    CompanionPetFood,
    OpdProduct,
    CompanionFeedingGuide,
)


class FeedingRepository:
    def __init__(self, db: Session):
        self.db = db


    def check_active_feeding_exists(
        self, pet_id: int
    ) -> bool:  # 반려동물 매칭 사료 확인
        """해당 반려동물에게 매칭된 사료(pet_product_feeding)가 있는지 확인합니다."""
        exists = (
            self.db.query(CompanionPetProductFeeding)
            .filter(
                CompanionPetProductFeeding.pet_id == pet_id,
                CompanionPetProductFeeding.is_feeding_check,
            )
            .first()
        )
        return exists is not None

    def get_inventory(self, pet_id: int):  # 급여 중 사료 잔여량 조회
        """사료 잔량 및 재고 정보를 조회합니다. (비관적 락 적용)"""
        return (
            self.db.query(CompanionCustomerFood)
            .filter_by(pet_id=pet_id)
            .with_for_update()
            .first()
        )

    def get_active_feeding_info(self, pet_id: int):  # 급여중 사료 정보 조회(cal, type)
        """현재 활성화된 사료의 영양 및 타입 정보를 조회합니다."""
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

    def get_daily_stats(self, pet_id: int, target_date):
        """특정 날짜의 급여량(amount) 합계와 칼로리(calories) 합계를 조회합니다."""
        result = (
            self.db.query(
                func.sum(CompanionPetFood.amount).label("total_amount"),
                func.sum(CompanionPetFood.calories).label("total_calories"),
            )
            .filter(
                CompanionPetFood.pet_id == pet_id,
                CompanionPetFood.feeding_date == target_date,
            )
            .first()
        )
        return {"total_amount": result.total_amount or 0, "total_calories": result.total_calories or 0}

    def get_target_calories(self, pet_id: int):
        """가장 최신의 추천 섭취량(guide_intake)을 조회합니다."""
        guide = (
            self.db.query(CompanionFeedingGuide)
            .filter(CompanionFeedingGuide.pet_id == pet_id)
            .order_by(CompanionFeedingGuide.guide_date.desc())
            .first()
        )
        # guide_intake가 없으면 0을 반환. (칼로리 산출은 사료 g당 칼로리와 곱해야 함)
        return guide.guide_intake if guide and guide.guide_intake else 0

    def add_log(self, log: CompanionPetFood):
        self.db.add(log)

    def delete_log(self, log: CompanionPetFood):
        self.db.delete(log)

    def get_log_by_id_and_date(self, pet_food_id: int, feeding_date):
        """파티션 키(날짜)와 ID를 조합하여 정확한 단건 식별"""
        return (
            self.db.query(CompanionPetFood)
            .filter_by(pet_food_id=pet_food_id, feeding_date=feeding_date)
            .first()
        )

    def get_logs_by_pet_and_range(
        self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0
    ):
        """복합 검색 조건으로 급여 히스토리 조회"""
        query = self.db.query(CompanionPetFood).filter_by(pet_id=pet_id)
        if start_date:
            query = query.filter(CompanionPetFood.feeding_date >= start_date)
        if end_date:
            query = query.filter(CompanionPetFood.feeding_date <= end_date)

        return (
            query.order_by(
                CompanionPetFood.feeding_date.desc(),
                CompanionPetFood.last_update.desc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)
