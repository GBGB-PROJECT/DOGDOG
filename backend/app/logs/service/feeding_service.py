from datetime import date, datetime, timedelta
from sqlalchemy import and_
from db.models import CompanionPetFood, CompanionPet, OpdSubs, OpdDelivery, CompanionButler


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
        """재고 보정 로직 (누적량, 횟수, 잔여량) - 비관적 락 적용"""
        inventory = self.repo.get_inventory_for_update(pet_id)
        if not inventory:
            return None

        inventory.total_intake += amount_diff
        inventory.food_count += count_diff

        # 백엔드 직접 계산: 잔여량 차감 (0 이하 방지)
        current_left = inventory.left_intake or 0
        inventory.left_intake = max(current_left - amount_diff, 0)

        return inventory

    def _validate_feeding_input(self, pet_id: int, amount: int, feeding_date: date):
        """급여 입력 데이터 무결성 검증 (재고, 미래 날짜, 과거 시작일)"""
        # 1. 날짜 검증 (미래 날짜 방지)
        if feeding_date > date.today():
            raise ValueError(
                f"미래 날짜({feeding_date})로 급여 기록을 입력할 수 없습니다."
            )

        # 2. 재고 및 사료 정보 기반 검증
        inventory = self.repo.get_inventory(pet_id)
        if inventory:
            # 시작일 이전 날짜인지 검증
            if inventory.feeding_start and feeding_date < inventory.feeding_start:
                raise ValueError(
                    f"사료 급여 시작일({inventory.feeding_start}) 이전 날짜로는 기록을 추가하거나 수정할 수 없습니다."
                )

            # 잔여량보다 급여량이 많은지 검증
            if inventory.left_intake is not None and inventory.left_intake < amount:
                raise ValueError(
                    f"사료 잔여량보다 많은 양은 입력 불가합니다. (현재 남은 양: {inventory.left_intake}g)"
                )

    # 잔여 일수 및 예상 소진일 통합 계산 헬퍼
    def _recalculate_remaining(self, pet_id: int, inventory):
        """남은 사료량 기반으로 left_food_count와 expected_exdate를 계산·저장합니다."""
        guide_intake = self.repo.get_guide_intake(pet_id)

        # 1. 잔여량(left_intake) 재확인 및 업데이트
        total_weight = int(inventory.total_weight) if inventory.total_weight else 0
        total_intake = int(inventory.total_intake) if inventory.total_intake else 0
        inventory.left_intake = max(total_weight - total_intake, 0)

        # 2. ZeroDivisionError 방어: guide_intake가 0이면 계산 스킵
        if not guide_intake or guide_intake <= 0:
            inventory.left_food_count = 0
            inventory.expected_exdate = None
            return

        # 3. 남은 일수 및 소진 예정일 계산
        inventory.left_food_count = int(inventory.left_intake // guide_intake)
        inventory.expected_exdate = date.today() + timedelta(
            days=inventory.left_food_count
        )

    # 급여 기록 등록
    def register_feeding(
        self,
        customer_id: int,
        pet_id: int,
        amount: int,
        feeding_date=None,
        feeding_time=None,
        memo=None,
    ):
        """[등록] 새로운 급여 기록을 등록하고 사료 재고 및 예상 소진일을 업데이트합니다."""
        if amount <= 0:
            raise ValueError("급여량은 0보다 커야 합니다.")

        if not feeding_date:
            feeding_date = date.today()  # 디폴트: 오늘

        # 급여 데이터 검증: 날짜, 재고
        self._validate_feeding_input(pet_id, amount, feeding_date)

        cal, f_type = self._get_feeding_info(pet_id, amount)

        # total_intake / food_count 누적 업데이트 (기존 로직 유지)
        # → DB가 left_intake를 자동 재계산함 (Generated Always)
        inven = self._update_inventory_logic(pet_id, amount, count_diff=1)

        if inven:
            # feeding_start가 None이면 최초 급여일로 현재 급여 날짜 세팅
            # (새 사료 등록/교체 시 feeding_start가 Null로 초기화된다는 전제)
            if inven.feeding_start is None:
                inven.feeding_start = feeding_date

            # expected_exdate 통합 재계산
            self._recalculate_remaining(pet_id, inven)

        log = CompanionPetFood(
            pet_id=pet_id,
            customer_id=customer_id,
            amount=amount,
            calories=cal,
            feeding_date=feeding_date,
            feeding_time=feeding_time,
            memo=memo,
            food_type=f_type,
        )
        self.repo.add_log(log)

        # [AutoDelivery] 자동 주문 트리거 호출 (commit 전)
        if inven and inven.expected_exdate:
            import asyncio

            # 비동기 환경이므로 동기 메서드 내에서 호출 시 주의 필요하나,
            # 현재 FastAPI/uvicorn 환경이므로 await로 호출 (Service가 비동기인 경우 기준)
            self.trigger_auto_delivery_process(pet_id, inven.expected_exdate)

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

    def update_feeding(self, customer_id: int, pet_food_id: int, new_data: dict):
        """[수정] 특정 급여 기록을 수정하고 재고 및 파티션을 관리합니다.

        더 이상 외부에서 old_date를 받지 않고 DB에서 조회한 원본 log의 날짜를 사용합니다.
        """
        log = self.repo.get_log_by_id(pet_food_id)
        if not log:
            raise ValueError("요청하신 급여 기록을 찾을 수 없습니다.")

        # 날짜 기반 재고 보정 여부 판단
        old_date = log.feeding_date
        feeding_start = self.repo.get_feeding_start(log.pet_id)
        is_current_period = True
        if feeding_start:
            is_current_period = old_date >= feeding_start

        amount_diff = 0
        if "amount" in new_data:
            amount_diff = new_data["amount"] - log.amount

            # 현재 사료 기간의 기록만 재고 검증 수행
            if is_current_period and amount_diff > 0:
                self._validate_feeding_input(log.pet_id, amount_diff, old_date)
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

        if "feeding_time" in new_data:
            log.feeding_time = new_data["feeding_time"]

        # 현재 사료 기간의 기록만 재고에 반영
        inven = None
        if is_current_period:
            inven = self._update_inventory_logic(log.pet_id, amount_diff)
            if inven:
                self._recalculate_remaining(log.pet_id, inven)

        # 날짜(Partition Key) 변경 시 삭제 후 재삽입 (Delete -> Insert)
        if "new_feeding_date" in new_data and new_data["new_feeding_date"] != old_date:
            new_date = new_data["new_feeding_date"]

            # 미래 날짜는 항상 차단
            if new_date > date.today():
                raise ValueError(
                    f"미래 날짜({new_date})로 급여 기록을 수정할 수 없습니다."
                )

            # 현재 사료 기간이면 시작일 이전 이동 방지 등 기존 검증 유지
            if is_current_period:
                self._validate_feeding_input(log.pet_id, 0, new_date)

            # PK 변경을 위한 D&I 처리
            new_log_data = {
                "pet_id": log.pet_id,
                "customer_id": log.customer_id,
                "amount": log.amount,
                "calories": log.calories,
                "memo": log.memo,
                "feeding_date": new_date,
                "feeding_time": log.feeding_time,
                "food_type": log.food_type,
            }
            self.repo.add_log(new_log)
            log = new_log

        # [AutoDelivery] 자동 주문 트리거 호출 (수정 시 소진일 변동 대응)
        if inven and inven.expected_exdate:
            self.trigger_auto_delivery_process(log.pet_id, inven.expected_exdate)

        self.repo.commit()
        if inven:
            self.repo.refresh(inven)

        return log, inven

    # 급여기록 삭제 및 소모 잔여량 복구
    def delete_feeding(self, customer_id: int, pet_food_id: int):
        """[삭제] 급여 기록을 삭제하고 소모된 재고를 복구합니다.

        날짜 기반 재고 보정 로직:
        - feeding_date >= feeding_start → 현재 사료 기간이므로 재고 복구 수행
        - feeding_date < feeding_start  → 과거 사료 기간이므로 로그만 삭제
        """
        log = self.repo.get_log_by_id(pet_food_id)
        if not log:
            raise ValueError("요청하신 급여 기록을 찾을 수 없습니다.")

        feeding_date = log.feeding_date

        # 날짜 기반 재고 복구 여부 판단
        feeding_start = self.repo.get_feeding_start(log.pet_id)
        is_current_period = True
        if feeding_start:
            is_current_period = feeding_date >= feeding_start

        # 현재 사료 기간의 기록만 재고 원복
        inven = None
        if is_current_period:
            inven = self._update_inventory_logic(log.pet_id, -log.amount, count_diff=-1)
            if inven:
                self._recalculate_remaining(log.pet_id, inven)

        self.repo.delete_log(log)
        self.repo.commit()

        return True, inven

    def trigger_auto_delivery_process(self, pet_id: int, expected_exdate: date):
        """
        소진일(expected_exdate) 업데이트 직후 자동 주문 생성 로직을 실행합니다.
        전체 로직은 상위 호출부의 트랜잭션 범위 내에서 실행됩니다.
        """
        if not expected_exdate:
            return

        try:
            # 1. 구독자 검증 및 구독 정보 조회
            # pet_id -> customer_id -> subs (활성 구독 또는 자동 배송 설정 확인)
            subs_info = (
                self.repo.db.query(OpdSubs)
                .join(
                    CompanionButler, CompanionButler.customer_id == OpdSubs.customer_id
                )
                .filter(
                    and_(
                        CompanionButler.pet_id == pet_id,
                        CompanionButler.active == True,  # 활성화된 집사인지 확인
                        OpdSubs.is_subs_status == True,  # 활성 구독자
                        OpdSubs.is_auto_delivery == True,  # 자동 배송 동의
                    )
                )
                .first()
            )

            if not subs_info:
                # print(f"[AutoDelivery] Skip: Pet {pet_id} is not an active subscriber.")
                return

            # 2. 타임 체크: 소진일이 오늘 기준 9일 이하로 남았는지 확인
            today = date.today()
            days_left = (expected_exdate - today).days

            if days_left > 9:
                # print(f"[AutoDelivery] Skip: {days_left} days left until exdate (Threshold: 9 days)")
                return

            # 3. 멱등성(Idempotency) 보장: 중복 주문 생성 방지 로직
            # [수정] order_start_date 타입 정합성 (date -> datetime 캐스팅)
            target_date = expected_exdate - timedelta(days=2)
            order_start_date = datetime.combine(target_date, datetime.min.time())

            existing_order = (
                self.repo.db.query(OpdDelivery)
                .filter(
                    and_(
                        OpdDelivery.subs_id == subs_info.subs_id,
                        # 동일 주기에 대한 중복 생성을 막기 위해 전후 3일 범위를 체크
                        OpdDelivery.order_start_date
                        >= (order_start_date - timedelta(days=3)),
                        OpdDelivery.order_start_date
                        <= (order_start_date + timedelta(days=3)),
                    )
                )
                .first()
            )

            if existing_order:
                # print(f"[AutoDelivery] Skip: Delivery already exists for this cycle")
                return

            # 4. 배송 테이블 Insert (주문 생성)
            new_delivery = OpdDelivery(
                subs_id=subs_info.subs_id,
                delivery_status_id=101,  # 101: 상품준비중
                order_start_date=order_start_date,
                insert_delivery_date=datetime.now(),
                last_update=datetime.now(),
            )

            self.repo.db.add(new_delivery)
            # flush를 통해 ID를 생성하되, 최종 commit은 상위 트랜잭션에 위임
            self.repo.db.flush()

            print(
                f"[AutoDelivery] Success: Created new delivery order for Pet {pet_id}"
            )

        except Exception as e:
            print(f"[AutoDelivery] Critical Error: {str(e)}")
            # 에러 발생 시 상위 트랜잭션 전체 롤백을 위해 raise
            raise e
