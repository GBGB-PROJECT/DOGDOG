from ..models import FeedingLog

class FeedingService:
    def __init__(self, repository):
        self.repo = repository

    def execute_registration(self, customer_id: int, pet_id: int, amount: int):
        # 1. 칼로리 정보 가져오기
        feeding_info = self.repo.get_active_feeding_info(pet_id)
        cal_per_gram = float(feeding_info.one_gram_calories) if feeding_info else 4.0
        
        # 2. 칼로리 계산
        calculated_calories = int(amount * cal_per_gram)

        # 3. 잔량 업데이트
        inventory = self.repo.get_inventory(customer_id)
        if inventory:
            inventory.total_intake += amount
            inventory.food_count += 1

        # 4. 로그 생성
        new_log = FeedingLog(
            pet_id=pet_id,
            customer_id=customer_id,
            amount=amount,
            calories=calculated_calories,
            food_type="건식"
        )

        try:
            self.repo.add_log(new_log)
            self.repo.commit()
            # DB가 계산한 Generated Column(left_intake 등)을 가져오기 위해 새로고침
            if inventory:
                self.repo.refresh(inventory)
            return new_log, inventory
        except Exception as e:
            self.repo.rollback()
            raise e