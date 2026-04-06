import sys
from datetime import date
from types import SimpleNamespace
from decimal import Decimal

# 실제 서비스 파일 불러오기 시도 (경로 설정)
# sys.path.append('backend/app')

class MockInventory:
    def __init__(self, total_weight, total_intake=0, food_count=0):
        self.total_weight = total_weight
        self.total_intake = total_intake
        self.food_count = food_count
        self.left_intake = total_weight - total_intake
        self.left_food_count = 0.0

class MockFeedingLog:
    def __init__(self, **kwargs):
        self.pet_food_id = kwargs.get("pet_food_id", 101)
        for k, v in kwargs.items():
            setattr(self, k, v)

class MockRepo:
    def __init__(self):
        self.inventory = MockInventory(5000, 500, 10)
        self.logs = {} # (id, date) -> log

    def get_inventory(self, customer_id):
        return self.inventory

    def get_active_feeding_info(self, pet_id):
        return SimpleNamespace(one_gram_calories=Decimal('4.0'))

    def add_log(self, log):
        self.logs[(log.pet_food_id, log.feeding_date)] = log

    def delete_log(self, log):
        if (log.pet_food_id, log.feeding_date) in self.logs:
            del self.logs[(log.pet_food_id, log.feeding_date)]

    def get_log_by_id_and_date(self, pet_food_id, feeding_date):
        return self.logs.get((pet_food_id, feeding_date))

    def commit(self):
        pass

    def rollback(self):
        pass

    def refresh(self, obj):
        pass

# 실제 서비스 로직 복사 (테스트에서 직접 임포트가 어렵다면 구조 검증을 위해 복사/사용)
# 여기선 위에서 작성한 FeedingService와 유사한 로직을 테스트함

def run_comprehensive_test():
    print("=== [통합 테스트] Feeding CRUD 로직 검증 시작 ===")
    from feeding_service import FeedingService # 상대 경로 임포트 가정 또는 로직 직접 정의
    
    # [1] 등록 테스트
    repo = MockRepo()
    service = FeedingService(repo)
    
    print("\n[Step 1] 등록 테스트 (Registration)")
    log, inven = service.register_feeding(110, 1, 200, date(2026,4,1), "맛있게 먹음")
    
    print(f"- 생성된 로그 칼로리: {log.calories} kcal (예상 800)")
    print(f"- 업데이트된 누적량: {inven.total_intake} g (예상 700)")
    print(f"- 업데이트된 잔여량: {inven.left_intake} g (예상 4300)")
    print(f"- 예상 남은 횟수: {round(inven.left_food_count, 1)} 회")
    
    assert log.calories == 800
    assert inven.total_intake == 700
    assert inven.left_intake == 4300
    
    # [2] 수정 테스트 (Amount 변경)
    print("\n[Step 2] 수정 테스트 (Update - Amount)")
    # 기존 200g을 300g으로 수정 (+100g 차액 발생)
    updated_log, inven = service.update_feeding(110, log.pet_food_id, date(2026,4,1), {"amount": 300})
    
    print(f"- 수정된 로그 칼로리: {updated_log.calories} kcal (예상 1200)")
    print(f"- 보정된 누적량: {inven.total_intake} g (예상 800)")
    print(f"- 보정된 잔여량: {inven.left_intake} g (예상 4200)")
    
    assert updated_log.calories == 1200
    assert inven.total_intake == 800
    
    # [3] 수정 테스트 (날짜 변경/파티션 이동)
    print("\n[Step 3] 수정 테스트 (Update - Date Migration)")
    new_date = date(2026,3,31)
    updated_log, inven = service.update_feeding(110, updated_log.pet_food_id, date(2026,4,1), {"new_feeding_date": new_date})
    
    print(f"- 변경된 날짜: {updated_log.feeding_date} (예상 2026-03-31)")
    # 이전 날짜인 (101, 2026-04-01)은 삭제되고 (101, 2026-03-31)이 생성되어야 함
    
    # [4] 삭제 테스트
    print("\n[Step 4] 삭제 테스트 (Deletion)")
    before_intake = inven.total_intake
    service.delete_feeding(110, updated_log.pet_food_id, date(2026,3,31))
    
    print(f"- 삭제 후 누적량: {inven.total_intake} g (예상 {before_intake - 300})")
    print(f"- 삭제 후 잔여량: {inven.left_intake} g (예상 {5000 - (before_intake - 300)})")
    
    assert inven.total_intake == (before_intake - 300)
    
    print("\n✅ 모든 CRUD 로직 테스트 통과!")

if __name__ == "__main__":
    # feeding_service.py 가 같은 디렉토리에 있거나 PYTHONPATH에 있어야 함
    # 이 테스트 파일은 backend/app/domains/logs/ 하위에서 실행된다고 가정
    try:
        run_comprehensive_test()
    except Exception as e:
        print(f"\n❌ 테스트 실패: {str(e)}")
        import traceback
        traceback.print_exc()