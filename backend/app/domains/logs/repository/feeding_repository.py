from sqlalchemy.orm import Session
from ..models import CustomerFood, PetProductFeeding, FeedingLog

class FeedingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory(self, customer_id: int):
        """사료 잔량 정보를 가져오며 수정 권한 획득(잠금)"""
        return self.db.query(CustomerFood).filter_by(customer_id=customer_id).with_for_update().first()

    def get_active_feeding_info(self, pet_id: int):
        """현재 활성화된 사료의 칼로리 정보 조회"""
        return self.db.query(PetProductFeeding).filter_by(pet_id=pet_id, is_feeding_check=True).first()

    def get_pet_owner_id(self, pet_id: int) -> int:
        """반려견의 소유주(customer_id)를 확인합니다. (임시 110 반환)"""
        # return self.db.execute("SELECT customer_id FROM pet WHERE pet_id = :pet_id", {"pet_id": pet_id}).scalar()
        return 110

    def add_log(self, log: FeedingLog):
        self.db.add(log)

    def delete_log(self, log: FeedingLog):
        self.db.delete(log)

    def get_log_by_id_and_date(self, pet_food_id: int, feeding_date) -> FeedingLog:
        """파티셔닝된 테이블 조회를 위해 고유 ID와 날짜를 함께 사용합니다."""
        return self.db.query(FeedingLog).filter_by(pet_food_id=pet_food_id, feeding_date=feeding_date).first()

    def get_logs_by_pet_and_range(self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0):
        """특정 기간 내 급여 기록을 조회합니다."""
        query = self.db.query(FeedingLog).filter_by(pet_id=pet_id)
        if start_date:
            query = query.filter(FeedingLog.feeding_date >= start_date)
        if end_date:
            query = query.filter(FeedingLog.feeding_date <= end_date)
        
        return query.order_by(FeedingLog.feeding_date.desc(), FeedingLog.last_update.desc()).offset(offset).limit(limit).all()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)