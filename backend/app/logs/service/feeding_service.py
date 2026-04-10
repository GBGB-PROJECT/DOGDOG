from datetime import date
from db.models import CompanionPetFood


class FeedingService:
    def __init__(self, repository):
        self.repo = repository

    # 사료 정보 가져오기
    def _get_feeding_info(self, pet_id: int, amount: int) -> tuple:
        """반려견의 사료 정보를 기반으로 섭취 칼로리와 사료 타입을 산출합니다."""
        # 1. DB에서 현재 강아지가 먹고 있는 사료 정보를 가져오기
        info = self.repo.get_active_feeding_info(pet_id)

        # 사료 정보(info) 자체가 없으면 즉시 에러
        if not info:
            raise ValueError(
                f"반려동물(ID:{pet_id})의 활성화된 사료 매칭 정보가 없습니다."
            )

        # 1g당 칼로리 정보가 없으면 계산 불가하므로 에러
        if info.one_gram_calories is None:
            raise ValueError(
                f"해당 사료의 칼로리 정보가 설정되지 않았습니다. (Pet ID: {pet_id})"
            )

        # 2. 칼로리 계산: (먹은 양 * 1g당 칼로리)
        cal_per_gram = float(info.one_gram_calories)
        calories = int(amount * cal_per_gram)

        # 3. 사료 타입 추출
        # 연쇄적으로 데이터가 존재하는지 확인하고, 하나라도 없으면 에러
        if not info.product:
            raise ValueError("사료 매칭 정보에 연결된 제품(Product)이 없습니다.")

        if not info.product.product_detail:
            raise ValueError(
                f"제품(ID:{info.product_id})의 상세 정보(Detail)가 존재하지 않습니다."
            )

        food_type = info.product.product_detail.type

        # 타입 값이 비어있을 경우에도 에러 발생
        if not food_type:
            raise ValueError("사료 제품의 타입(건식/습식 등) 정보가 누락되었습니다.")

        return calories, food_type

    # 재고 보정 로직
    def _update_inventory_logic(
        self, pet_id: int, amount_diff: int, count_diff: int = 0
    ):
        """재고 보정 로직 (누적량, 횟수)"""
        inventory = self.repo.get_inventory(pet_id)
        if not inventory:
            return None

        inventory.total_intake += amount_diff
        inventory.food_count += count_diff

        return inventory

    # 사료 잔여량 체크 로직
    def _validate_stock(self, pet_id: int, required_amount: int):
        """현재 잔여량이 필요한 양보다 충분한지 검증합니다."""
        inventory = self.repo.get_inventory(pet_id)
        if not inventory:
            return  # 재고 레코드가 없으면 체크를 건너뜁니다.

        # left_intake
        if (
            inventory.left_intake is not None
            and inventory.left_intake < required_amount
        ):
            raise ValueError(
                f"사료 잔여량보다 많은 양은 입력 불가합니다. (현재 남은 양: {inventory.left_intake}g)"
            )

    def _validate_date(self, feeding_date: date):
        """급여 날짜가 미래인지 검증합니다."""
        if feeding_date > date.today():
            raise ValueError(f"미래 날짜({feeding_date})로 급여 기록을 입력할 수 없습니다.")

    # 급여 기록 등록
    def register_feeding(
        self, customer_id: int, pet_id: int, amount: int, feeding_date=None, memo=None
    ):
        if amount <= 0:
            raise ValueError("급여량은 0보다 커야 합니다.")

        """[등록] 새로운 급여 기록을 등록하고 사료 재고를 업데이트합니다."""
        if not feeding_date:
            feeding_date = date.today()  # 디폴트: 오늘

        # 미래 날짜 체크 추가
        self._validate_date(feeding_date)

        # 급여 중 사료 잔여량 체크 추가
        self._validate_stock(pet_id, amount)

        cal, f_type = self._get_feeding_info(pet_id, amount)
        inven = self._update_inventory_logic(pet_id, amount, count_diff=1)

        log = CompanionPetFood(
            pet_id=pet_id,
            customer_id=customer_id,
            amount=amount,
            calories=cal,
            feeding_date=feeding_date,
            memo=memo,
            food_type=f_type,
        )
        self.repo.add_log(log)
        self.repo.commit()

        return log, inven

    def get_feeding_logs(
        self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0
    ):
        """[조회] 특정 기간의 급여 기록과 통계를 반환합니다."""
        data = self.repo.get_logs_by_pet_and_range(
            pet_id, start_date, end_date, limit, offset
        )
        total_amount = sum(l.amount for l in data)
        total_calories = sum(l.calories for l in data)

        return {
            "logs": data,
            "total_amount": total_amount,
            "total_calories": total_calories,
        }

    # 급여 기록 수정 및 잔여량 수정
    def update_feeding(
        self, customer_id: int, pet_food_id: int, old_date, new_data: dict
    ):
        """[수정] 특정 급여 기록을 수정하고 재고 및 파티션을 관리합니다."""
        log = self.repo.get_log_by_id_and_date(pet_food_id, old_date)
        if not log:
            raise ValueError("ERR_NOT_FOUND")

        amount_diff = 0
        if "amount" in new_data:
            amount_diff = new_data["amount"] - log.amount

            # 수정되는 양이 잔여량보다 많은지 체크
            if amount_diff > 0:
                self._validate_stock(log.pet_id, amount_diff)
            # 이전 기록의 1g당 칼로리 역산 (0으로 나누기 방지 포함)
            if log.amount > 0:
                old_cal_per_gram = log.calories / log.amount
            else:
                # 혹시 기존 양이 0이었다면 현재 마스터 정보에서 가져옴
                info = self.repo.get_active_feeding_info(log.pet_id)
                old_cal_per_gram = float(info.one_gram_calories) if info else 0

            # 재고 보정값 계산
            amount_diff = new_data["amount"] - log.amount

            # 새로운 양에 맞춰 칼로리 재계산 (타입은 기존 것 유지)
            log.amount = new_data["amount"]
            log.calories = int(log.amount * old_cal_per_gram)

        if "memo" in new_data:
            log.memo = new_data["memo"]

        inven = self._update_inventory_logic(log.pet_id, amount_diff)

        # 날짜(Partition Key) 변경 시 삭제 후 재삽입 (Delete -> Insert)
        if "new_feeding_date" in new_data and new_data["new_feeding_date"] != old_date:
            # 미래 날짜 체크 추가 (수정 시)
            self._validate_date(new_data["new_feeding_date"])

            # PK 변경을 위한 D&I 처리
            new_log_data = {
                "pet_id": log.pet_id,
                "customer_id": log.customer_id,
                "amount": log.amount,
                "calories": log.calories,
                "memo": log.memo,
                "feeding_date": new_data["new_feeding_date"],
                "food_type": log.food_type,
            }
            self.repo.delete_log(log)
            new_log = CompanionPetFood(**new_log_data)
            self.repo.add_log(new_log)
            log = new_log

        self.repo.commit()
        if inven:
            self.repo.refresh(inven)

        return log, inven

    # 급여기록 삭제 및 소모 잔여량 복구
    def delete_feeding(
        self, customer_id: int, pet_food_id: int, feeding_date
    ):  # 권한 이슈로 테스트 미진행
        """[삭제] 급여 기록을 삭제하고 소모된 재고를 복구합니다."""
        log = self.repo.get_log_by_id_and_date(pet_food_id, feeding_date)
        if not log:
            raise ValueError("ERR_NOT_FOUND")

        # 재고 원복
        inven = self._update_inventory_logic(log.pet_id, -log.amount, count_diff=-1)
        self.repo.delete_log(log)
        self.repo.commit()

        return True, inven
