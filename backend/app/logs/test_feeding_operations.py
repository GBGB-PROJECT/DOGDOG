import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import date
from sqlalchemy.exc import ProgrammingError, InternalError
from app.logs.service.feeding_service import FeedingService
from app.logs.repository.feeding_repository import FeedingRepository

class TestFeedingOperations(unittest.TestCase):
    def setUp(self):
        # DB 세션 및 리포지토리 모킹
        self.db = MagicMock()
        self.repo = FeedingRepository(self.db)
        self.service = FeedingService(self.repo)
        
        self.pet_id = 101
        self.customer_id = 110
        self.amount = 500

        # 기본 재고 데이터 설정 (Mock)
        # CompanionCustomerFood의 PK는 pet_id임
        self.mock_inventory = SimpleNamespace(
            pet_id=self.pet_id,
            total_weight=5000,
            total_intake=500,
            food_count=10,
            left_intake=4500,
            left_food_count=90.0
        )
        self.repo.get_inventory = MagicMock(return_value=self.mock_inventory)
        self.repo.get_active_feeding_info = MagicMock(return_value=SimpleNamespace(one_gram_calories=4.2))

    def test_read_priority_public_success(self):
        """[조회] public 스키마 최우선 참조 여부 확인"""
        mock_log = SimpleNamespace(amount=500, calories=2100, memo="From Public")
        self.repo.get_logs_by_pet_and_range = MagicMock(return_value=[mock_log])
        
        result = self.service.get_feeding_logs(self.pet_id)
        
        self.assertEqual(result["logs"][0].memo, "From Public")
        print("✅ [성공] public 스키마 데이터 조회 확인")

    def test_cud_fallback_to_dog5_on_permission_denied(self):
        """[등록] public 권한 부족 시 dog_5 폴백 확인"""
        permission_error = ProgrammingError("INSERT failed", {}, "InsufficientPrivilege: permission denied")
        
        # 첫 시도(commit)에서 에러 발생 시뮬레이션
        self.repo.commit = MagicMock(side_effect=[permission_error, None])
        
        with patch.object(self.repo, 'switch_schema') as mock_switch:
            log, inven = self.service.register_feeding(
                customer_id=self.customer_id,
                pet_id=self.pet_id,
                amount=self.amount,
                memo="Fallback Test"
            )
            
            # 검증: dog_5로 전환 호출 확인
            mock_switch.assert_called_with("dog_5")
            # 검증: 두 번째 commit이 성공하여 결과가 리턴됨
            self.assertEqual(self.repo.commit.call_count, 2)
            print("✅ [성공] 등록 단계 권한 에러 시 dog_5 폴백 확인")

    def test_update_inventory_discrepancy(self):
        """[수정] 급여량 차액만큼 재고가 보정되는지 확인"""
        mock_log = SimpleNamespace(pet_id=self.pet_id, amount=300, calories=1200, feeding_date=date.today())
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        # 300g -> 500g으로 수정 시 amount_diff는 +200g
        old_intake = self.mock_inventory.total_intake
        self.service.update_feeding(self.customer_id, 1, date.today(), {"amount": 500})
        
        self.assertEqual(self.mock_inventory.total_intake, old_intake + 200)
        print("✅ [성공] 수정 시 재고 차액 보정 확인")

    def test_partition_move_on_date_change(self):
        """[수정] 날짜 변경 시 삭제 후 재삽입 로직 확인"""
        old_date = date(2026, 4, 1)
        new_date = date(2026, 4, 2)
        mock_log = MagicMock(pet_id=self.pet_id, customer_id=self.customer_id, amount=300, calories=1200, feeding_date=old_date, food_type="건식")
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        with patch.object(self.repo, 'delete_log') as mock_delete, \
             patch.object(self.repo, 'add_log') as mock_add:
            
            self.service.update_feeding(self.customer_id, 1, old_date, {"new_feeding_date": new_date})
            
            # 검증: 이전 로그 삭제 및 새 로그 추가 호출
            mock_delete.assert_called()
            mock_add.assert_called()
            print("✅ [성공] 날짜 변경 시 파티션 이동(Delete->Insert) 확인")

    def test_delete_inventory_restore(self):
        """[삭제] 기록 삭제 시 재고가 올바르게 복구되는지 확인"""
        mock_log = SimpleNamespace(pet_id=self.pet_id, amount=300, calories=1200, feeding_date=date.today())
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        old_intake = self.mock_inventory.total_intake
        old_count = self.mock_inventory.food_count
        
        self.service.delete_feeding(self.customer_id, 1, date.today())
        
        # 삭제 시 intake는 -300, count는 -1
        self.assertEqual(self.mock_inventory.total_intake, old_intake - 300)
        self.assertEqual(self.mock_inventory.food_count, old_count - 1)
        print("✅ [성공] 삭제 시 재고 및 횟수 원복 확인")

if __name__ == "__main__":
    unittest.main()
