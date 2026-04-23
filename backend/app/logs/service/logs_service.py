from datetime import date, datetime
from typing import Optional
from app.logs.repository.logs_repository import LogsRepository

class LogsService:
    """통합 로그 탭 주요 기능 처리 (급여 + 기타 이력 병합)"""

    def __init__(self, repository: LogsRepository):
        self.repo = repository

    def get_unified_logs(self, pet_id: int, target_date: date, category: Optional[str] = None):
        """특정 날짜의 통합 로그 목록을 조회하고 시간 역순으로 정렬합니다."""
        
        merged_logs = []

        # 1. 급여 기록 추가 (category 필터링: None, 'all', 또는 'feeding')
        if not category or category == "all" or category == "feeding":
            feeding_logs = self.repo.get_feeding_logs_by_date(pet_id, target_date)
            for log in feeding_logs:
                # pet_food는 feeding_date만 기록되므로, 
                # 시간 정보가 없으면 last_update 기반이거나 임의로 00:00으로 셋팅
                # 여기서는 UI 시간 표시용으로 datetime을 만듭니다.
                record_time = log.last_update if log.last_update else datetime.combine(target_date, datetime.min.time())
                merged_logs.append({
                    "id": log.pet_food_id,
                    "domain": "feeding",
                    "category": "feeding",
                    "amount": log.amount,
                    "unit": "g",
                    "calories": log.calories,
                    "memo": log.memo,
                    "timestamp": record_time,  # 정렬을 위한 datetime 객체
                    "display_time": record_time.strftime("%H:%M"),
                })

        # 2. 기타 로깅 추가 (category: None, 'all', 또는 기타 카테고리)
        fetch_numeric = not category or category == "all" or category != "feeding"
        if fetch_numeric:
            numeric_logs = self.repo.get_numeric_logs_by_date(pet_id, target_date)
            for log in numeric_logs:
                if category and category != "all" and log.category != category:
                    continue  # 카테고리가 지정되었지만 일치하지 않으면 건너뜀
                
                record_time = log.log_date if log.log_date else log.last_update
                
                # 단위 및 값을 UI 친화적으로 변환
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
                    "calories": 0, # 급여가 아니므로 0
                    "memo": log.memo,
                    "timestamp": record_time,  # 정렬용
                    "display_time": record_time.strftime("%H:%M") if record_time else "",
                })

        # 3. 시간 역순으로 병합 정렬
        merged_logs.sort(key=lambda x: x["timestamp"], reverse=True)

        # 4. JSON 응답 포맷에 맞게 datetime 직렬화 처리
        for log in merged_logs:
            if isinstance(log["timestamp"], datetime):
                log["timestamp"] = log["timestamp"].isoformat()

        return merged_logs
