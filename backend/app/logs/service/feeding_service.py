from datetime import date
from sqlalchemy.exc import ProgrammingError, InternalError
from db.models import CompanionPetFood

class FeedingService:
    def __init__(self, repository):
        self.repo = repository

    def _calculate_calories(self, pet_id: int, amount: int) -> int:
        """반려견의 사료 정보를 기반으로 섭취 칼로리를 산출합니다."""
        info = self.repo.get_active_feeding_info(pet_id)
        cal_per_gram = float(info.one_gram_calories) if info else 4.0
        return int(amount * cal_per_gram)

    def _update_inventory_logic(self, pet_id: int, amount_diff: int, count_diff: int = 0):
        """재고 보정 로직 (누적량, 잔량, 횟수)"""
        inventory = self.repo.get_inventory(pet_id)
        if not inventory:
            return None
        
        inventory.total_intake += amount_diff
        inventory.food_count += count_diff
        inventory.left_intake = max(0, inventory.total_weight - inventory.total_intake)
        
        # 평균 급여량 기반 남은 횟수 계산
        if inventory.total_intake > 0 and inventory.food_count > 0:
            avg = inventory.total_intake / inventory.food_count
            inventory.left_food_count = float(inventory.left_intake / avg)
        else:
            inventory.left_food_count = 0
            
        return inventory

    def _is_permission_error(self, e: Exception) -> bool:
        """권한 부족(InsufficientPrivilege) 에러인지 판별합니다."""
        error_msg = str(e).lower()
        return "insufficientprivilege" in error_msg or "permission denied" in error_msg

    def register_feeding(self, customer_id: int, pet_id: int, amount: int, feeding_date=None, memo=None):
        """[등록] Public 우선 시도 후 권한 부족 시 dog_5로 폴백하여 저장합니다."""
        if not feeding_date:
            feeding_date = date.today()
            
        def _registration_logic():
            # 1. 정보 산출
            cal = self._calculate_calories(pet_id, amount)
            inven = self._update_inventory_logic(pet_id, amount, count_diff=1)
            
            # 2. 로그 생성
            log = CompanionPetFood(
                pet_id=pet_id, customer_id=customer_id, amount=amount,
                calories=cal, feeding_date=feeding_date, memo=memo, food_type="건식"
            )
            self.repo.add_log(log)
            self.repo.commit()
            if inven: self.repo.refresh(inven)
            return log, inven

        # 이원화 전략 실행
        try:
            # 먼저 기본 설정(public 우선)대로 시도
            return _registration_logic()
        except (ProgrammingError, InternalError) as e:
            if self._is_permission_error(e):
                self.repo.rollback() # 트랜잭션 실패 시 초기화
                print("⚠️ [Fallback] public 권한 부족으로 dog_5 스키마로 전환합니다.")
                self.repo.switch_schema("dog_5")
                return _registration_logic()
            raise e

    def get_feeding_logs(self, pet_id: int, start_date=None, end_date=None, limit=20, offset=0):
        """[조회] public 및 dog_5 통합 로그를 조회합니다."""
        # search_path가 public, dog_5 순서이므로 public 데이터가 우선 노출됩니다.
        data = self.repo.get_logs_by_pet_and_range(pet_id, start_date, end_date, limit, offset)
        total_amount = sum(l.amount for l in data)
        total_calories = sum(l.calories for l in data)
        
        return {
            "logs": data,
            "total_amount": total_amount,
            "total_calories": total_calories
        }

    def update_feeding(self, customer_id: int, pet_food_id: int, old_date, new_data: dict):
        """[수정] 스키마 이원화 전략을 지원하는 수정 로직입니다."""
        def _update_logic():
            log = self.repo.get_log_by_id_and_date(pet_food_id, old_date)
            if not log: raise ValueError("ERR_NOT_FOUND")
            
            amount_diff = 0
            if "amount" in new_data:
                amount_diff = new_data["amount"] - log.amount
                log.amount = new_data["amount"]
                log.calories = self._calculate_calories(log.pet_id, log.amount)
            
            if "memo" in new_data: log.memo = new_data["memo"]
            
            inven = self._update_inventory_logic(log.pet_id, amount_diff)
            
            # 날짜(Partition Key) 변경 시 삭제 후 재삽입
            if "new_feeding_date" in new_data and new_data["new_feeding_date"] != old_date:
                # PK 변경을 위한 D&I 처리
                new_log_data = {
                    "pet_id": log.pet_id, "customer_id": log.customer_id,
                    "amount": log.amount, "calories": log.calories,
                    "memo": log.memo, "feeding_date": new_data["new_feeding_date"],
                    "food_type": log.food_type
                }
                self.repo.delete_log(log)
                new_log = CompanionPetFood(**new_log_data)
                self.repo.add_log(new_log)
                log = new_log
                
            self.repo.commit()
            if inven: self.repo.refresh(inven)
            return log, inven

        try:
            return _update_logic()
        except (ProgrammingError, InternalError) as e:
            if self._is_permission_error(e):
                self.repo.rollback()
                self.repo.switch_schema("dog_5")
                return _update_logic()
            raise e

    def delete_feeding(self, customer_id: int, pet_food_id: int, feeding_date):
        """[삭제] 스키마 이원화 전략을 지원하는 삭제 및 재고 복구 로직입니다."""
        def _delete_logic():
            log = self.repo.get_log_by_id_and_date(pet_food_id, feeding_date)
            if not log: raise ValueError("ERR_NOT_FOUND")
            
            # 재고 원복
            inven = self._update_inventory_logic(log.pet_id, -log.amount, count_diff=-1)
            self.repo.delete_log(log)
            self.repo.commit()
            return True, inven

        try:
            return _delete_logic()
        except (ProgrammingError, InternalError) as e:
            if self._is_permission_error(e):
                self.repo.rollback()
                self.repo.switch_schema("dog_5")
                return _delete_logic()
            raise e