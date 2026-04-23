from sqlalchemy.orm import Session
from datetime import date
from typing import Optional
from db.models import CompanionPetFood, CompanionPetLogNumeric

class LogsRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_feeding_logs_by_date(self, pet_id: int, target_date: date):
        return (
            self.db.query(CompanionPetFood)
            .filter(
                CompanionPetFood.pet_id == pet_id,
                CompanionPetFood.feeding_date == target_date,
                CompanionPetFood.active == True,
            )
            .all()
        )

    def get_numeric_logs_by_date(self, pet_id: int, target_date: date):
        from sqlalchemy import cast, Date
        return (
            self.db.query(CompanionPetLogNumeric)
            .filter(
                CompanionPetLogNumeric.pet_id == pet_id,
                CompanionPetLogNumeric.active == True,
                cast(CompanionPetLogNumeric.log_date, Date) == target_date
            )
            .all()
        )
