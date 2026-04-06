from datetime import date
from ..models import FeedingLog

class FeedingService:
    def __init__(self, repository):
        self.repo = repository

    def _calculate_calories(self, pet_id: int, amount: int) -> int:
        """반려견의 현재 사료 정보를 기반으로 섭취 칼로리를 계산합니다."""
        feeding_info = self.repo.get_active_feeding_info(pet_id)
        cal_per_gram = float(feeding_info.one_gram_calories) if feeding_info else 4.0
        return int(amount * cal_per_gram)

    def _update_inventory(self, customer_id: int, amount_diff: int, count_diff: int = 0):
        """사료 재고 데이터를 업데이트합니다. (누적량, 잔여량, 횟수)"""
        inventory = self.repo.get_inventory(customer_id)
        if not inventory:
            return None
        
        inventory.total_intake += amount_diff
        inventory.food_count += count_diff
        
        # 잔량 및 예상 횟수 계산
        inventory.left_intake = max(0, inventory.total_weight - inventory.total_intake)
        
        if inventory.total_intake > 0 and inventory.food_count > 0:
            avg_amount = inventory.total_intake / inventory.food_count
            inventory.left_food_count = float(inventory.left_intake / avg_amount)
        else:
            inventory.left_food_count = 0
            
        return inventory

    def register_feeding(self, customer_id: int, pet_id: int, amount: int, feeding_date=None, memo=None):
        """새로운 급여 기록을 등록합니다."""
        if not feeding_date:
            feeding_date = date.today()
            
        # 1. 칼로리 계산
        calculated_calories = self._calculate_calories(pet_id, amount)
        
        # 2. 재고 정보 업데이트 (누적량 +amount, 횟수 +1)
        inventory = self._update_inventory(customer_id, amount, count_diff=1)
        
        # 3. 로그 객체 생성
        new_log = FeedingLog(
            pet_id=pet_id,
            customer_id=customer_id,
            amount=amount,
            calories=calculated_calories,
            feeding_date=feeding_date,
            memo=memo,
            food_type="건식" # 기본값
        )
        
        try:
            self.repo.add_log(new_log)
            self.repo.commit()
            if inventory:
                self.repo.refresh(inventory)
            return new_log, inventory
        except Exception as e:
            self.repo.rollback()
            raise e

    def update_feeding(self, customer_id: int, pet_food_id: int, old_date, new_data: dict):
        """기존 급여 기록을 수정합니다. (재고 보정 및 파티션 이동 지원)"""
        log = self.repo.get_log_by_id_and_date(pet_food_id, old_date)
        if not log:
            raise ValueError("ERR_NOT_FOUND")
        if log.customer_id != customer_id:
            raise PermissionError("ERR_FORBIDDEN")
            
        amount_diff = 0
        new_amount = new_data.get("amount")
        new_date = new_data.get("new_feeding_date")
        
        # 1. 급여량 수정 시 차액 계산 및 칼로리 재계산
        if new_amount is not None:
            old_amount = log.amount
            amount_diff = new_amount - old_amount
            log.amount = new_amount
            log.calories = self._calculate_calories(log.pet_id, new_amount)
            
        if "memo" in new_data:
            log.memo = new_data["memo"]
            
        # 2. 재고 보정
        inventory = self._update_inventory(customer_id, amount_diff)
        
        try:
            # 3. 날짜 변경 시 파티션 이동 처리
            if new_date and new_date != old_date:
                # SQLAlchemy에선 PK(Partition Key) 수정 시 삭제 후 재삽입이 안전함
                new_log_data = {
                    "pet_id": log.pet_id,
                    "customer_id": log.customer_id,
                    "amount": log.amount,
                    "calories": log.calories,
                    "memo": log.memo,
                    "feeding_date": new_date,
                    "food_type": log.food_type
                }
                self.repo.delete_log(log)
                new_log = FeedingLog(**new_log_data)
                self.repo.add_log(new_log)
                log = new_log
            
            self.repo.commit()
            if inventory:
                self.repo.refresh(inventory)
            return log, inventory
        except Exception as e:
            self.repo.rollback()
            raise e

    def delete_feeding(self, customer_id: int, pet_food_id: int, feeding_date):
        """급여 기록을 삭제하고 재고를 원복합니다."""
        log = self.repo.get_log_by_id_and_date(pet_food_id, feeding_date)
        if not log:
            raise ValueError("ERR_NOT_FOUND")
        if log.customer_id != customer_id:
            raise PermissionError("ERR_FORBIDDEN")
            
        # 재고 원복 (누적량 -amount, 횟수 -1)
        inventory = self._update_inventory(customer_id, -log.amount, count_diff=-1)
        
        try:
            self.repo.delete_log(log)
            self.repo.commit()
            return True, inventory
        except Exception as e:
            self.repo.rollback()
            raise e

    def get_feeding_logs(self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0):
        """기간별 급여 기록 및 통계 데이터를 조회합니다."""
        logs = self.repo.get_logs_by_pet_and_range(pet_id, start_date, end_date, limit, offset)
        
        # 합계 계산
        total_amount = sum(l.amount for l in logs)
        total_calories = sum(l.calories for l in logs)
        
        return {
            "logs": logs,
            "total_amount": total_amount,
            "total_calories": total_calories
        }