
# 프로젝트 루트 및 backend 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))


import unittest
from unittest.mock import MagicMock
from types import SimpleNamespace
from datetime import datetime, timedelta
from decimal import Decimal
from app.logs.service.pet_log_service import PetLogService
from app.logs.repository.pet_log_repository import PetLogRepository


class TestPoopLog(unittest.TestCase):
    def setUp(self):
        self.db = MagicMock()
        self.repo = PetLogRepository(self.db)
        self.service = PetLogService(self.repo)

        self.pet_id = 101
        self.customer_id = 1

        # 리포지토리 메서드 Mock
        self.repo.check_duplicate = MagicMock(return_value=False)
        self.repo.add_log = MagicMock()
        self.repo.commit = MagicMock()
        self.repo.refresh = MagicMock()
        self.repo.delete_log = MagicMock()

    def test_register_success(self):
        """[등록] 정상적인 배변 기록 등록"""
        log_date = datetime.now() - timedelta(hours=1)

        log, is_dup = self.service.register_poop_log(
            customer_id=self.customer_id,
            pet_id=self.pet_id,
            log_status=4.0,
            log_date=log_date,
            memo="정상 변",
        )

        self.assertEqual(log.category, "poop")
        self.assertEqual(log.log_status, Decimal("4.0"))
        self.assertEqual(log.pet_id, self.pet_id)
        self.assertFalse(is_dup)
        self.repo.add_log.assert_called_once()
        self.repo.commit.assert_called_once()

    def test_register_future_date_fail(self):
        """[등록] 미래 시간 등록 시 실패"""
        future = datetime.now() + timedelta(hours=1)

        with self.assertRaises(ValueError) as cm:
            self.service.register_poop_log(
                self.customer_id, self.pet_id, 4.0, future
            )
        self.assertIn("미래 시간", str(cm.exception))

    def test_register_invalid_score_low(self):
        """[등록] 점수 1.0 미만 시 실패"""
        log_date = datetime.now() - timedelta(hours=1)

        with self.assertRaises(ValueError) as cm:
            self.service.register_poop_log(
                self.customer_id, self.pet_id, 0.5, log_date
            )
        self.assertIn("1.0~7.0", str(cm.exception))

    def test_register_invalid_score_high(self):
        """[등록] 점수 7.0 초과 시 실패"""
        log_date = datetime.now() - timedelta(hours=1)

        with self.assertRaises(ValueError) as cm:
            self.service.register_poop_log(
                self.customer_id, self.pet_id, 8.0, log_date
            )
        self.assertIn("1.0~7.0", str(cm.exception))

    def test_register_duplicate_warning(self):
        """[등록] 중복 시간 등록 시 경고 반환 (차단 아님)"""
        self.repo.check_duplicate = MagicMock(return_value=True)
        log_date = datetime.now() - timedelta(hours=1)

        log, is_dup = self.service.register_poop_log(
            self.customer_id, self.pet_id, 4.0, log_date
        )
        self.assertTrue(is_dup)
        self.repo.add_log.assert_called_once()  # 등록은 정상 진행

    def test_update_success(self):
        """[수정] 점수 및 메모 수정 성공"""
        mock_log = MagicMock(
            pet_log_numeric_id=1,
            log_status=Decimal("4.0"),
            memo="이전 메모",
            log_date=datetime.now() - timedelta(hours=2),
            last_update=datetime.now() - timedelta(hours=2),
        )
        self.repo.get_log_by_id = MagicMock(return_value=mock_log)

        self.service.update_poop_log(1, {"log_status": 5.0, "memo": "색상 변화"})

        self.assertEqual(mock_log.log_status, Decimal("5.0"))
        self.assertEqual(mock_log.memo, "색상 변화")
        self.repo.commit.assert_called_once()

    def test_update_future_date_fail(self):
        """[수정] 미래 시간으로 변경 시 실패"""
        mock_log = MagicMock(
            pet_log_numeric_id=1,
            log_date=datetime.now() - timedelta(hours=2),
        )
        self.repo.get_log_by_id = MagicMock(return_value=mock_log)
        future = datetime.now() + timedelta(hours=1)

        with self.assertRaises(ValueError) as cm:
            self.service.update_poop_log(1, {"log_date": future})
        self.assertIn("미래 시간", str(cm.exception))

    def test_update_not_found_fail(self):
        """[수정] 존재하지 않는 로그 수정 시 실패"""
        self.repo.get_log_by_id = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as cm:
            self.service.update_poop_log(999, {"memo": "test"})
        self.assertIn("찾을 수 없습니다", str(cm.exception))

    def test_delete_success(self):
        """[삭제] Soft Delete 성공 확인"""
        mock_log = MagicMock(pet_log_numeric_id=1)
        self.repo.get_log_by_id = MagicMock(return_value=mock_log)

        result = self.service.delete_poop_log(1)

        self.assertTrue(result)
        self.repo.delete_log.assert_called_once_with(mock_log)
        self.repo.commit.assert_called_once()

    def test_delete_not_found_fail(self):
        """[삭제] 존재하지 않는 로그 삭제 시 실패"""
        self.repo.get_log_by_id = MagicMock(return_value=None)

        with self.assertRaises(ValueError) as cm:
            self.service.delete_poop_log(999)
        self.assertIn("찾을 수 없습니다", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
