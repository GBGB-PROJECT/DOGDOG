from datetime import date, datetime
from typing import Optional
from app.logs.repository.logs_repository import LogsRepository

class LogsService:
    """통합 로그 탭 주요 기능 처리 (급여 + 기타 이력 병합)"""

    def __init__(self, repository: LogsRepository):
        self.repo = repository

    def get_unified_logs(
        self, 
        pet_id: int, 
        target_date: Optional[date] = None, 
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ):
        """[리팩터링] 특정 날짜 또는 기간의 통합 로그를 조회하고 최신순으로 정렬합니다."""
        
        merged_logs = []

        # 1. 급여 기록 추가
        if not category or category in ["all", "feeding"]:
            feeding_logs = self.repo.get_feeding_logs(pet_id, target_date, start_date, end_date)
            for log in feeding_logs:
                # [해결 1] 시스템 시간이 아닌 유저가 지정한 feeding_date + feeding_time 조합
                if log.feeding_date and log.feeding_time:
                    try:
                        f_time = log.feeding_time if not isinstance(log.feeding_time, str) else datetime.strptime(log.feeding_time, "%H:%M:%S").time()
                        record_time = datetime.combine(log.feeding_date, f_time)
                    except Exception:
                        record_time = log.last_update
                else:
                    record_time = log.last_update

                merged_logs.append({
                    "id": log.pet_food_id,
                    "domain": "feeding",
                    "category": "feeding",
                    "amount": log.amount,
                    "unit": "g",
                    "calories": log.calories,
                    "memo": log.memo,
                    "timestamp": record_time,
                    "display_time": record_time.strftime("%H:%M") if record_time else "00:00",
                })

        # 2. 기타 로깅 추가 (Numeric)
        if not category or category != "feeding":
            numeric_logs = self.repo.get_numeric_logs(pet_id, target_date, start_date, end_date)
            for log in numeric_logs:
                if category and category != "all" and log.category != category:
                    continue
                
                record_time = log.log_date if log.log_date else log.last_update
                
                unit = ""
                value = float(log.log_status) if log.log_status else 0
                if log.category == "poop":
                    unit = "점"
                elif log.category == "water":
                    unit = "ml"
                    
                merged_logs.append({
                    "id": log.pet_log_numeric_id,
                    "domain": "numeric",
                    "category": log.category,
                    "amount": value,
                    "unit": unit,
                    "calories": 0,
                    "memo": log.memo,
                    "timestamp": record_time,
                    "display_time": record_time.strftime("%H:%M") if record_time else "00:00",
                })

        # 3. 논리적 발생 시간 기준으로 정렬
        merged_logs.sort(key=lambda x: x["timestamp"] if x["timestamp"] else datetime.min, reverse=True)

        # 4. JSON 직렬화
        for log in merged_logs:
            if isinstance(log["timestamp"], datetime):
                log["timestamp"] = log["timestamp"].isoformat()

        return merged_logs
