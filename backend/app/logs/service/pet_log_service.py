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

    def _trigger_recalculation(self, pet_id: int):
        """기록 변경 후 권장 급여량을 재계산합니다. (로그만 남기고 메인 로직에는 영향 없음)"""
        from app.calc_feeding.cal_guideIntake_service import create_feeding_recommendation_service
        try:
            # 트랜잭션 독립성 및 안전성을 위해 별도 커밋(commit=True) 사용
            create_feeding_recommendation_service(db=self.repo.db, pet_id=pet_id, commit=True)
            print(f"[PetLogService] Feeding guide successfully recalculated for pet {pet_id}")
        except Exception as e:
            # 재계산 실패가 메인 기록 저장에 영향을 주지 않도록 예외를 삼킴
            print(f"[PetLogService] Feeding guide recalculation failed for pet {pet_id}: {e}")

    def register_poop_log(
        self,
        customer_id: int,
        pet_id: int,
        log_status: float,
        log_date: datetime,
        memo: str = None,
    ) -> tuple:
        """배변 기록을 등록합니다."""
        self._validate_log_date(log_date)
        self._validate_log_status(log_status)

        # 중복 체크 (경고용, 비차단)
        is_duplicate = self.repo.check_duplicate(pet_id, log_date, category="poop")

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

        # 권장 급여량 재계산 트리거
        self._trigger_recalculation(pet_id)

        return log, is_duplicate

    def get_poop_log(self, pet_log_numeric_id: int):
        """배변 기록을 단건 조회합니다."""
        return self.repo.get_log_by_id(pet_log_numeric_id)

    def update_poop_log(
        self,
        pet_log_numeric_id: int,
        update_data: dict,
    ) -> CompanionPetLogNumeric:
        """배변 기록을 수정합니다."""
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

        # last_update 수동 갱신
        log.last_update = datetime.now()

        self.repo.commit()
        self.repo.refresh(log)

        # 권장 급여량 재계산 트리거
        self._trigger_recalculation(log.pet_id)

        return log

    def delete_poop_log(self, pet_log_numeric_id: int) -> bool:
        """배변 기록을 논리 삭제(Soft Delete)합니다."""
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("요청하신 배변 기록을 찾을 수 없습니다.")

        pet_id = log.pet_id
        self.repo.delete_log(log)
        self.repo.commit()

        # 권장 급여량 재계산 트리거
        self._trigger_recalculation(pet_id)

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

    def get_numeric_log(self, pet_log_numeric_id: int):
        """기록 단건 조회"""
        return self.repo.get_log_by_id(pet_log_numeric_id)

    def register_numeric_log(
        self,
        customer_id: int,
        pet_id: int,
        category: str,
        log_status: float,
        log_date: datetime,
        memo: str = None,
    ) -> tuple:
        """범용 수치형 기록(poop, water, walk 등)을 등록합니다."""
        self._validate_log_date(log_date)
        
        # 카테고리별 유효성 검사
        if category == "poop":
            self._validate_log_status(log_status)
        elif category == "walk":
            if log_status < 0:
                raise ValueError("산책 시간은 0분 이상이어야 합니다.")

        is_duplicate = self.repo.check_duplicate(pet_id, log_date, category=category)

        log = CompanionPetLogNumeric(
            pet_id=pet_id,
            customer_id=customer_id,
            category=category,
            log_status=Decimal(str(log_status)),
            log_date=log_date,
            memo=memo,
            active=True  # 신규 기록은 항상 활성 상태
        )
        self.repo.add_log(log)
        self.repo.commit()
        self.repo.refresh(log)

        # 동기화 및 재계산
        if category in ["weight", "bcs"]:
            self.sync_pet_latest_status(pet_id, category)
        self._trigger_recalculation(pet_id)

        return log, is_duplicate

    def register_weight_bcs_bulk(
        self, customer_id: int, pet_id: int, weight: float = None, bcs: int = None, log_date: datetime = None, memo: str = None
    ) -> list:
        """체중 및 BCS 데이터를 두 개의 레코드로 분할 저장합니다."""
        inserted_logs = []
        self._validate_log_date(log_date)

        # 1. 체중 처리
        if weight is not None:
            if weight <= 0 or weight >= 200:
                raise ValueError("체중은 0 초과 200 미만이어야 합니다.")
            log_weight = CompanionPetLogNumeric(
                pet_id=pet_id,
                customer_id=customer_id,
                category="weight",
                log_status=Decimal(str(weight)),
                log_date=log_date,
                memo=memo,
                active=True
            )
            self.repo.add_log(log_weight)
            inserted_logs.append(log_weight)

        # 2. BCS 처리
        if bcs is not None:
            if not (1 <= bcs <= 9):
                raise ValueError("BCS 점수는 1~9 사이여야 합니다.")
            log_bcs = CompanionPetLogNumeric(
                pet_id=pet_id,
                customer_id=customer_id,
                category="bcs",
                log_status=Decimal(str(bcs)),
                log_date=log_date,
                memo=memo,
                active=True
            )
            self.repo.add_log(log_bcs)
            inserted_logs.append(log_bcs)

        if not inserted_logs:
            raise ValueError("등록할 데이터(weight 또는 bcs)가 없습니다.")

        self.repo.db.flush()
        for log in inserted_logs:
            self.sync_pet_latest_status(pet_id, log.category)
        
        self.repo.commit()
        for log in inserted_logs:
            self.repo.refresh(log)
        
        self._trigger_recalculation(pet_id)
        return inserted_logs

    def update_numeric_log(self, pet_log_numeric_id: int, update_data: dict) -> CompanionPetLogNumeric:
        """수치형 기록 수정"""
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("해당 기록을 찾을 수 없습니다.")

        if "log_status" in update_data and update_data["log_status"] is not None:
            new_val = update_data["log_status"]
            # 카테고리별 유효성 재검증
            if log.category == "poop": self._validate_log_status(new_val)
            elif log.category == "weight":
                if not (0 < new_val < 200): raise ValueError("체중 범위 오류")
            elif log.category == "bcs":
                if not (1 <= new_val <= 9): raise ValueError("BCS 범위 오류")
            
            log.log_status = Decimal(str(new_val))

        if "log_date" in update_data:
            self._validate_log_date(update_data["log_date"])
            log.log_date = update_data["log_date"]

        if "memo" in update_data:
            log.memo = update_data["memo"]

        log.last_update = datetime.now()
        self.repo.db.flush()
        
        if log.category in ["weight", "bcs"]:
            self.sync_pet_latest_status(log.pet_id, log.category)
        
        self.repo.commit()
        self.repo.refresh(log)
        self._trigger_recalculation(log.pet_id)
        return log

    def delete_numeric_log(self, pet_log_numeric_id: int) -> bool:
        """소프트 딜리트 (active = False)"""
        log = self.repo.get_log_by_id(pet_log_numeric_id)
        if not log:
            raise ValueError("해당 기록을 찾을 수 없습니다.")

        pet_id = log.pet_id
        category = log.category
        
        # Soft Delete 처리
        log.active = False
        log.last_update = datetime.now()
        
        self.repo.db.flush()
        
        # 삭제 후 가장 최신 데이터로 동기화 (Fallback)
        if category in ["weight", "bcs"]:
            self.sync_pet_latest_status(pet_id, category)
        
        self.repo.commit()
        self._trigger_recalculation(pet_id)
        return True
