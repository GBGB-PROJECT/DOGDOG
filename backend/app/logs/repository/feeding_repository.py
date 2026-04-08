from sqlalchemy.orm import Session
from sqlalchemy import text
from db.models import CompanionCustomerFood, CompanionPetProductFeeding, CompanionPetFood

class FeedingRepository:
    def __init__(self, db: Session):
        self.db = db

    def switch_schema(self, schema_name: str):
        """스키마 검색 경로를 변경하여 운영(public) 또는 연습장(dog_5)을 선택합니다."""
        self.db.execute(text(f"SET search_path TO {schema_name}, public;"))
        self.db.commit() # 설정 반영을 위해 커밋

    def get_inventory(self, pet_id: int):
        # 사료 잔량 및 재고 정보 조회 (CompanionCustomerFood의 PK는 pet_id임)
        return self.db.query(CompanionCustomerFood).filter_by(pet_id=pet_id).with_for_update().first()

    def get_active_feeding_info(self, pet_id: int):
        # 현재 활성화된 사료의 영양 정보 조회
        return self.db.query(CompanionPetProductFeeding).filter_by(pet_id=pet_id, is_feeding_check=True).first()

    def add_log(self, log: CompanionPetFood):
        self.db.add(log)

    def delete_log(self, log: CompanionPetFood):
        self.db.delete(log)

    def get_log_by_id_and_date(self, pet_food_id: int, feeding_date):
        # 파티션 키(날짜)와 ID를 조합하여 정확한 단건 식별
        return self.db.query(CompanionPetFood).filter_by(pet_food_id=pet_food_id, feeding_date=feeding_date).first()

    def get_logs_by_pet_and_range(self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0):
        # 복합 검색 조건으로 급여 히스토리 조회
        query = self.db.query(CompanionPetFood).filter_by(pet_id=pet_id)
        if start_date:
            query = query.filter(CompanionPetFood.feeding_date >= start_date)
        if end_date:
            query = query.filter(CompanionPetFood.feeding_date <= end_date)
        
        return query.order_by(CompanionPetFood.feeding_date.desc(), CompanionPetFood.last_update.desc()).offset(offset).limit(limit).all()

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()

    def refresh(self, obj):
        self.db.refresh(obj)