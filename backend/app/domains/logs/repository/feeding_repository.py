from sqlalchemy.orm import Session
from ..models import CustomerFood, PetProductFeeding, FeedingLog

class FeedingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory(self, customer_id: int):
        # 사료 잔량 정보를 가져오며 수정 권한 획득(잠금)
        return self.db.query(CustomerFood).filter_by(customer_id=customer_id).with_for_update().first()

    def get_active_feeding_info(self, pet_id: int):
        # 현재 활성화된 사료의 칼로리 정보 조회
        return self.db.query(PetProductFeeding).filter_by(pet_id=pet_id, is_feeding_check=True).first()

    def add_log(self, log: FeedingLog):
        self.db.add(log)

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)