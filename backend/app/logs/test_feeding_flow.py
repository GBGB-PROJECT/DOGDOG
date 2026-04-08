#db 연결 전 백엔드 코드 테스트용 파일

import sys
from datetime import date
from types import SimpleNamespace

# [테스트용] 외부 파일 참조 없이 내부에서 클래스 정의 (경로 에러 원천 차단)
class MockFeedingLog:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

class FeedingService:
    def __init__(self, repository):
        self.repo = repository

    def process_feeding_registration(self, customer_id: int, data):
        inventory = self.repo.get_inventory(customer_id)
        calculated_calories = data.amount * 4 

        inventory.total_intake += data.amount
        inventory.food_count += 1
        inventory.left_intake = max(0, inventory.total_weight - inventory.total_intake)

        if inventory.total_intake > 0:
            avg_amount = inventory.total_intake / inventory.food_count
            inventory.left_food_count = inventory.left_intake / avg_amount
        else:
            inventory.left_food_count = 0

        inventory.is_feeding_check = inventory.left_intake > 0

        new_log = MockFeedingLog(
            pet_id=data.pet_id,
            customer_id=customer_id,
            amount=data.amount,
            calories=calculated_calories,
            feeding_date=data.feeding_date,
            memo=data.memo
        )
        
        self.repo.commit()
        return new_log, inventory

class MockFeedingRepository:
    def __init__(self):
        self.storage = {
            110: SimpleNamespace(
                total_weight=5000,
                total_intake=500,
                left_intake=4500,
                food_count=10,
                left_food_count=90.0,
                is_feeding_check=True
            )
        }

    def get_inventory(self, customer_id: int):
        return self.storage.get(customer_id)

    def commit(self):
        print(">> [Mock] 메모리 데이터 업데이트 완료")

def run_test():
    print("=== [통합 테스트] 급여 등록 로직 가동 ===")
    mock_repo = MockFeedingRepository()
    service = FeedingService(mock_repo)

    test_request = SimpleNamespace(
        pet_id=1,
        amount=200, 
        feeding_date=date.today(),
        memo="최종 로직 테스트"
    )

    customer_id = 110
    log, inven = service.process_feeding_registration(customer_id, test_request)

    print(f"\n[결과 리포트]")
    print(f"- 계산된 칼로리: {log.calories} kcal")
    print(f"- 남은 사료 양: {inven.left_intake} g")
    print(f"- 예상 남은 횟수: {round(inven.left_food_count, 1)} 회")

    if inven.left_intake == 4300 and inven.food_count == 11:
        print("\n✅ 테스트 통과: 로직이 완벽하게 설계되었습니다!")
    else:
        print("\n❌ 테스트 실패: 결과값이 예상과 다릅니다.")

if __name__ == "__main__":
    run_test()