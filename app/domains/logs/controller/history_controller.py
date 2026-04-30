from api_client import ApiClient
import datetime

class HistoryController:
    """
    [Controller] HistoryController
    역할: 히스토리(/history) 화면의 비즈니스 로직과 API 데이터 조회를 담당합니다.
    - View에서 분리되어 데이터만 제공하며, 날짜 필터링 로직을 수행합니다.
    """
    def __init__(self, page):
        self.page = page
        self.api_client = ApiClient(page)

    async def get_timeline_logs(self, pet_id: int):
        """
        타임라인 데이터를 서버에서 가져옵니다.
        API: GET /api/v1/logs/{pet_id}
        """
        try:
            response = await self.api_client.get(f"/logs/{pet_id}")
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                print(f"[HistoryController] API 호출 실패: {response.status_code}")
                return []
        except Exception as e:
            print(f"[HistoryController] 데이터 조회 중 예외 발생: {e}")
            return []

    def get_filtered_logs_and_date_str(self, logs: list):
        """
        세션 스토리지의 선택된 날짜(select_log_date, select_log_week)를 확인하여
        표시할 날짜 문자열(view_date_str)과 필터링된 로그 배열을 반환합니다.
        """
        storage = self.page.session.store
        now = datetime.datetime.now()
        
        # 1. 표시할 날짜 제목과 필터링 기준 날짜 목록 결정
        if storage.get("select_log_date"):
            date_str = storage.get("select_log_date")
            valid_dates = [date_str]
            storage.remove("select_log_date")
        elif storage.get("select_log_week"):
            date_str = storage.get("select_log_week")
            valid_dates = [
                (now - datetime.timedelta(days=i)).strftime("%Y.%m.%d")
                for i in range(7)
            ]
            storage.remove("select_log_week")
        else:
            date_str = now.strftime("%Y.%m.%d")
            valid_dates = [date_str]

        # 2. 날짜에 맞게 로그 필터링
        filtered_logs = []
        for log in logs:
            # API 응답에 log_date나 date가 있다고 가정. 없으면 일단 포함.
            raw_date = log.get("log_date") or log.get("date")
            if raw_date:
                # "2024-05-12 13:23" 형태의 경우 "2024.05.12"로 변환
                date_part = raw_date.split(" ")[0].replace("-", ".")
                if date_part in valid_dates:
                    filtered_logs.append(log)
            else:
                # 날짜 정보가 없으면 우선 포함시킴 (새로운 API 스펙 대응)
                filtered_logs.append(log)

        return filtered_logs, date_str
