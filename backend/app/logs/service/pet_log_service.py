from datetime import datetime
from decimal import Decimal

from db.models import CompanionPetLogNumeric


class PetLogService:
    """배변 기록 비즈니스 로직을 담당합니다."""

    def __init__(self, repository):
        self.repo = repository

    def _validate_log_date(self, log_date: datetime):
        """미래 시간 입력을 차단합니다.

        Args:
            log_date: 검증 대상 일시

        Raises:
            ValueError: 미래 시간인 경우
        """
        if log_date.replace(tzinfo=None) > datetime.now():
            raise ValueError(
                f"미래 시간({log_date.strftime('%Y-%m-%d %H:%M:%S')})으로 "
                f"기록을 등록할 수 없습니다."
            )

    def _validate_log_status(self, log_status: float):
        """배변 점수 범위를 검증합니다 (1.0 ~ 7.0).

        Args:
            log_status: 배변 점수

        Raises:
            ValueError: 범위를 벗어난 경우
        """
        if not (1.0 <= float(log_status) <= 7.0):
            raise ValueError(
                f"배변 점수는 1.0~7.0 사이여야 합니다. (입력값: {log_status})"
            )

    def register_poop_log(
        self,
        customer_id: int,
        pet_id: int,
        log_status: float,
        log_date: datetime,
        memo: str = None,
    ) -> tuple:
        """배변 기록을 등록합니다.

        Args:
            customer_id: 보호자 ID
            pet_id: 대상 반려견 ID
            log_status: 배변 점수 (1.0~7.0)
            log_date: 실제 발생 일시
            memo: 메모 (선택)

        Returns:
            (CompanionPetLogNumeric, is_duplicate: bool) 튜플
        """
        self._validate_log_date(log_date)
        self._validate_log_status(log_status)

        # 중복 체크 (경고용, 비차단)
        is_duplicate = self.repo.check_duplicate(pet_id, log_date)

        log = CompanionPetLogNumeric(
            pet_id=pet_id,
            customer_id=customer_id,
            category="poop",
            log_status=Decimal(str(log_status)),
            log_date=log_date,
            memo=memo,
        )
        self.repo.add_log(log)
        self.repo.commit()
        self.repo.refresh(log)

        return log, is_duplicate

    def get_poop_log(self, pet_log_numeric_id: int):
        """배변 기록을 단건 조회합니다.

        Args:
            pet_log_numeric_id: 배변 로그 PK

        Returns:
            CompanionPetLogNumeric 또는 None
        """
        return self.repo.get_log_by_id(pet_log_numeric_id)

    def update_poop_log(
        self,
        pet_log_numeric_id: int,
        update_data: dict,
    ) -> CompanionPetLogNumeric:
        """배변 기록을 수정합니다. (log_status, log_date, memo만 수정 가능)

        Args:
            pet_log_numeric_id: 대상 로그 PK
            update_data: 수정할 필드-값 딕셔너리

        Returns:
            수정된 CompanionPetLogNumeric 객체

        Raises:
            ValueError: 로그를 찾을 수 없거나, 입력값이 유효하지 않은 경우
        """
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("요청하신 배변 기록을 찾을 수 없습니다.")

        if "log_status" in update_data:
            self._validate_log_status(update_data["log_status"])
            log.log_status = Decimal(str(update_data["log_status"]))

        if "log_date" in update_data:
            self._validate_log_date(update_data["log_date"])
            log.log_date = update_data["log_date"]

        if "memo" in update_data:
            log.memo = update_data["memo"]

        # last_update 수동 갱신 (모델에 onupdate 미설정)
        log.last_update = datetime.now()

        self.repo.commit()
        self.repo.refresh(log)

        return log

    def delete_poop_log(self, pet_log_numeric_id: int) -> bool:
        """배변 기록을 논리 삭제(Soft Delete)합니다.

        Args:
            pet_log_numeric_id: 대상 로그 PK

        Returns:
            삭제 성공 여부

        Raises:
            ValueError: 로그를 찾을 수 없는 경우
        """
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("요청하신 배변 기록을 찾을 수 없습니다.")

        self.repo.delete_log(log)
        self.repo.commit()

        return True

    def sync_pet_latest_status(self, pet_id: int, category: str):
        """지정된 카테고리의 가장 최신 기록을 찾아 메인 pet 테이블 값에 오버라이딩(동기화)합니다."""
        from db.models import CompanionPet

        latest_log = (
            self.repo.db.query(CompanionPetLogNumeric)
            .filter(
                CompanionPetLogNumeric.pet_id == pet_id,
                CompanionPetLogNumeric.category == category,
                CompanionPetLogNumeric.active == True,
            )
            .order_by(
                CompanionPetLogNumeric.log_date.desc(),
                CompanionPetLogNumeric.pet_log_numeric_id.desc(),
            )
            .first()
        )

        pet = (
            self.repo.db.query(CompanionPet)
            .filter(CompanionPet.pet_id == pet_id)
            .first()
        )
        if not pet:
            return

        if category == "weight":
            pet.weight = latest_log.log_status if latest_log else None
        elif category == "bcs":
            pet.bcs = int(latest_log.log_status) if latest_log else None
        self.repo.db.flush()

    def register_weight_bcs(
        self, customer_id: int, pet_id: int, request_data: dict
    ) -> list:
        """체중 및 BCS 기록을 분리하여 일괄 등록하고 동기화합니다."""
        inserted_logs = []
        log_date = request_data.get("log_date")
        memo = request_data.get("memo")

        weight = request_data.get("weight")
        if weight is not None:
            self._validate_log_date(log_date)
            if weight <= 0 or weight >= 200:
                raise ValueError("체중은 0 초과 200 미만이어야 합니다.")
            log_weight = CompanionPetLogNumeric(
                pet_id=pet_id,
                customer_id=customer_id,
                category="weight",
                log_status=Decimal(str(weight)),
                log_date=log_date,
                memo=memo,
            )
            self.repo.add_log(log_weight)
            inserted_logs.append(log_weight)
            self.repo.db.flush()

        bcs = request_data.get("bcs")
        if bcs is not None:
            self._validate_log_date(log_date)
            if not (1 <= bcs <= 9):
                raise ValueError("BCS 점수는 1~9 사이의 정수여야 합니다.")
            log_bcs = CompanionPetLogNumeric(
                pet_id=pet_id,
                customer_id=customer_id,
                category="bcs",
                log_status=Decimal(str(bcs)),
                log_date=log_date,
                memo=memo,
            )
            self.repo.add_log(log_bcs)
            inserted_logs.append(log_bcs)
            self.repo.db.flush()

        if not inserted_logs:
            raise ValueError("등록할 체중 또는 BCS 데이터가 없습니다.")

        for log in inserted_logs:
            self.sync_pet_latest_status(pet_id, log.category)

        self.repo.commit()
        for log in inserted_logs:
            self.repo.refresh(log)

        return inserted_logs

    def update_weight_bcs(self, pet_log_numeric_id: int, update_data: dict) -> list:
        """단일 기록의 수치 또는 날짜를 수정하고 재동기화합니다."""
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("요청하신 기록을 찾을 수 없습니다.")

        if log.category not in ["weight", "bcs"]:
            raise ValueError("해당 API는 체중이나 BCS 기록만 수정할 수 있습니다.")

        if "log_status" in update_data and update_data["log_status"] is not None:
            log_status = update_data["log_status"]
            if log.category == "weight":
                if log_status <= 0 or log_status >= 200:
                    raise ValueError("체중은 0 초과 200 미만이어야 합니다.")
            elif log.category == "bcs":
                if not (1 <= log_status <= 9):
                    raise ValueError("BCS 점수는 1~9 사이의 정수여야 합니다.")
            log.log_status = Decimal(str(log_status))

        if "log_date" in update_data and update_data["log_date"] is not None:
            self._validate_log_date(update_data["log_date"])
            log.log_date = update_data["log_date"]

        log.last_update = datetime.now()
        self.repo.db.flush()

        self.sync_pet_latest_status(log.pet_id, log.category)
        self.repo.commit()
        self.repo.refresh(log)

        return [log]

    def delete_weight_bcs(self, pet_log_numeric_id: int) -> bool:
        """기록을 논리 삭제하고 이전 데이터로 Fallback(롤백)합니다."""
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("요청하신 기록을 찾을 수 없습니다.")

        if log.category not in ["weight", "bcs"]:
            raise ValueError("해당 API는 체중이나 BCS 기록만 삭제할 수 있습니다.")

        self.repo.delete_log(log)
        self.repo.db.flush()

        self.sync_pet_latest_status(log.pet_id, log.category)
        self.repo.commit()

        return True
