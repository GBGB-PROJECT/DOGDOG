from datetime import datetime

from sqlalchemy.orm import Session
from db.models import CompanionPetLogNumeric


class PetLogRepository:
    """배변 기록(pet_log_numeric) 데이터 접근 계층입니다."""

    def __init__(self, db: Session):
        self.db = db

    def get_log_by_id(self, pet_log_numeric_id: int):
        """활성 상태인 배변 로그를 ID로 단건 조회합니다.

        Args:
            pet_log_numeric_id: 배변 로그 PK

        Returns:
            CompanionPetLogNumeric 또는 None
        """
        return (
            self.db.query(CompanionPetLogNumeric)
            .filter(
                CompanionPetLogNumeric.pet_log_numeric_id == pet_log_numeric_id,
                CompanionPetLogNumeric.active == True,
            )
            .first()
        )

    def check_duplicate(
        self, pet_id: int, log_date: datetime, category: str = "poop"
    ) -> bool:
        """동일 pet_id·log_date·category 조합의 중복 기록 존재 여부를 확인합니다.

        Args:
            pet_id: 대상 반려견 ID
            log_date: 기록 시간
            category: 로그 카테고리

        Returns:
            중복 존재 시 True
        """
        exists = (
            self.db.query(CompanionPetLogNumeric)
            .filter(
                CompanionPetLogNumeric.pet_id == pet_id,
                CompanionPetLogNumeric.log_date == log_date,
                CompanionPetLogNumeric.category == category,
                CompanionPetLogNumeric.active == True,
            )
            .first()
        )
        return exists is not None

    def add_log(self, log: CompanionPetLogNumeric):
        """새 배변 로그를 세션에 추가합니다."""
        self.db.add(log)
        self.db.flush()  # DB에서 생성된 ID를 즉시 가져옴

    def delete_log(self, log: CompanionPetLogNumeric):
        """Soft Delete: active 상태를 False로 변경합니다."""
        log.active = False

    def commit(self):
        self.db.commit()

    def refresh(self, obj):
        self.db.refresh(obj)
