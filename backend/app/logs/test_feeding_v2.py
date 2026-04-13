import os
import sys

# 프로젝트 루트 및 backend 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__)) # ..../backend/app/logs
backend_dir = os.path.abspath(os.path.join(current_dir, "../../../")) # ..../backend
project_root = os.path.abspath(os.path.join(backend_dir, "../")) # ..../

if project_root not in sys.path: sys.path.insert(0, project_root)
if backend_dir not in sys.path: sys.path.insert(0, backend_dir)

import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from datetime import date, timedelta
from app.logs.service.feeding_service import FeedingService
from app.logs.repository.feeding_repository import FeedingRepository

class TestFeedingV2(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.repo = FeedingRepository(self.db)
        self.service = FeedingService(self.repo)
        
        self.pet_id = 101
        self.customer_id = 1 # API 최신값
        self.amount = 500

        # 기본 재고 데이터 Mock
        self.mock_inventory = SimpleNamespace(
            pet_id=self.pet_id,
            total_weight=5000,
            total_intake=1000,
            food_count=10,
            left_intake=4000,
            feeding_start=date(2025, 1, 1)
        )
        
        # 기본 급여 정보 Mock (칼로리, 제품 정보 포함)
        self.mock_info = MagicMock()
        self.mock_info.one_gram_calories = 4.0
        self.mock_info.product = MagicMock()
        self.mock_info.product.product_detail = MagicMock()
        self.mock_info.product.product_detail.type = "건식"

        # 리포지토리 메서드 연결
        self.repo.get_inventory = MagicMock(return_value=self.mock_inventory)
        self.repo.get_active_feeding_info = MagicMock(return_value=self.mock_info)
        self.repo.check_pet_ownership = MagicMock(return_value=True)
        self.repo.check_active_feeding_exists = MagicMock(return_value=True)

    def test_register_future_date_fail(self):
        """[검증] 미래 날짜 등록 시 실패 여부 확인"""
        future_date = date.today() + timedelta(days=1)
        with self.assertRaises(ValueError) as cm:
            self.service.register_feeding(self.customer_id, self.pet_id, self.amount, future_date)
        self.assertIn("미래 날짜", str(cm.exception))

    def test_register_zero_amount_fail(self):
        """[검증] 급여량 0 이하 등록 시 실패 여부 확인"""
        with self.assertRaises(ValueError) as cm:
            self.service.register_feeding(self.customer_id, self.pet_id, 0)
        self.assertIn("0보다 커야 합니다", str(cm.exception))

    def test_register_over_stock_fail(self):
        """[검증] 잔여량보다 많은 양 등록 시 실패 여부 확인"""
        self.mock_inventory.left_intake = 100
        with self.assertRaises(ValueError) as cm:
            self.service.register_feeding(self.customer_id, self.pet_id, 200)
        self.assertIn("잔여량보다 많은 양은 입력 불가", str(cm.exception))

    def test_register_success(self):
        """[성공] 정상적인 급여 등록 및 재고 업데이트 확인"""
        log, inven = self.service.register_feeding(self.customer_id, self.pet_id, 100)
        
        self.assertEqual(log.amount, 100)
        self.assertEqual(log.calories, 400) # 100 * 4.0
        self.assertEqual(inven.total_intake, 1100) # 1000 + 100
        self.assertEqual(inven.food_count, 11) # 10 + 1

    def test_update_success_with_amount_change(self):
        """[수정] 급여량 수정 시 칼로리 재계산 및 재고 보정 확인"""
        old_date = date.today()
        # 기존 로그: 200g, 800kcal
        mock_log = MagicMock(pet_id=self.pet_id, amount=200, calories=800, feeding_date=old_date)
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        # 200g -> 300g으로 수정 (diff +100)
        self.service.update_feeding(self.customer_id, 1, old_date, {"amount": 300})
        
        self.assertEqual(mock_log.amount, 300)
        self.assertEqual(mock_log.calories, 1200) # 300 * (800/200)
        self.assertEqual(self.mock_inventory.total_intake, 1100) # 1000 + 100

    def test_update_future_date_fail(self):
        """[수정] 변경하려는 날짜가 미래인 경우 실패 확인"""
        old_date = date.today() - timedelta(days=1)
        future_date = date.today() + timedelta(days=1)
        mock_log = MagicMock(pet_id=self.pet_id, amount=200, calories=800, feeding_date=old_date)
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        with self.assertRaises(ValueError) as cm:
            self.service.update_feeding(self.customer_id, 1, old_date, {"new_feeding_date": future_date})
        self.assertIn("미래 날짜", str(cm.exception))

    def test_delete_success(self):
        """[삭제] 삭제 시 재고 및 횟수 원복 확인"""
        log_date = date.today()
        mock_log = MagicMock(pet_id=self.pet_id, amount=200, calories=800, feeding_date=log_date)
        self.repo.get_log_by_id_and_date = MagicMock(return_value=mock_log)
        
        self.service.delete_feeding(self.customer_id, 1, log_date)
        
        self.assertEqual(self.mock_inventory.total_intake, 800) # 1000 - 200
        self.assertEqual(self.mock_inventory.food_count, 9) # 10 - 1

if __name__ == "__main__":
    unittest.main()
