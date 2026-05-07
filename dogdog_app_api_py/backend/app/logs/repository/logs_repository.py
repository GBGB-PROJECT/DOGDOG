from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from db.models import CompanionPetFood, CompanionPetLogNumeric

class LogsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feeding_logs(self, pet_id: int, target_date: Optional[date] = None, start_date: Optional[date] = None, end_date: Optional[date] = None):
        """[조회] 사료 급여 기록 (단일 날짜 또는 기간)"""
        query = self.db.query(CompanionPetFood).filter(
            CompanionPetFood.pet_id == pet_id,
            CompanionPetFood.active == True
        )
        if start_date and end_date:
            query = query.filter(CompanionPetFood.feeding_date.between(start_date, end_date))
        elif target_date:
            query = query.filter(CompanionPetFood.feeding_date == target_date)
        return query.all()

    def get_numeric_logs(self, pet_id: int, target_date: Optional[date] = None, start_date: Optional[date] = None, end_date: Optional[date] = None):
        """[조회] 수치형 로그 기록 (단일 날짜 또는 기간)"""
        from sqlalchemy import cast, Date
        query = self.db.query(CompanionPetLogNumeric).filter(
            CompanionPetLogNumeric.pet_id == pet_id,
            CompanionPetLogNumeric.active == True
        )
        if start_date and end_date:
            query = query.filter(cast(CompanionPetLogNumeric.log_date, Date).between(start_date, end_date))
        elif target_date:
            query = query.filter(cast(CompanionPetLogNumeric.log_date, Date) == target_date)
        return query.all()
