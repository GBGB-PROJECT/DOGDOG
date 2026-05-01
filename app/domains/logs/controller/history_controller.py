import flet as ft
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
        self.selected_log_data = None      # [수정] 현재 선택된 로그 데이터
        self.selected_ui_container = None  # [추가] 현재 선택된 로그 UI 컨테이너
        self.log_containers = []      # 화면에 그려진 로그 컨테이너 참조 리스트
        self.on_refresh_callback = None # 뷰 새로고침 콜백

    async def get_timeline_logs(self, pet_id: int):
        # ... (기존 코드 유지)
        try:
            response = await self.api_client.get(f"/logs/{pet_id}")
            if response.status_code == 200:
                return response.json().get("data", [])
            else:
                return []
        except Exception:
            return []

    def get_filtered_logs_and_date_str(self, logs: list):
        """
        세션 스토리지의 선택된 날짜를 확인하여 필터링된 로그 배열을 반환합니다.
        """
        storage = self.page.session.store
        now = datetime.datetime.now()
        
        if storage.get("select_log_date"):
            date_str = storage.get("select_log_date")
            valid_dates = [date_str]
        elif storage.get("select_log_week"):
            date_str = storage.get("select_log_week")
            valid_dates = [(now - datetime.timedelta(days=i)).strftime("%Y.%m.%d") for i in range(7)]
        else:
            date_str = now.strftime("%Y.%m.%d")
            valid_dates = [date_str]

        filtered_logs = []
        for log in logs:
            raw_date = log.get("log_date") or log.get("date")
            if raw_date:
                date_part = raw_date.split(" ")[0].replace("-", ".")
                if date_part in valid_dates:
                    filtered_logs.append(log)
            else:
                filtered_logs.append(log)

        return filtered_logs, date_str

    def select_log(self, log_data, container):
        """기록 컨테이너 클릭 시 단일 선택 로직"""
        # 기존 선택 해제
        for c in self.log_containers:
            c.bgcolor = None
            
        # 새로운 선택 (토글링 지원)
        if self.selected_log_data and self.selected_log_data.get("id") == log_data.get("id"):
            self.selected_log_data = None
            self.selected_ui_container = None
        else:
            self.selected_log_data = log_data
            self.selected_ui_container = container
            container.bgcolor = ft.Colors.GREY_200
        
        self.page.update()

    def history_delete(self, e):
        """삭제 버튼 클릭 시"""
        if not self.selected_log_data:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("삭제할 기록을 선택해주세요."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        import components as dogdog
        delete_popup = self.popup.event_popup
        delete_popup.title = dogdog.basic_text("기록 삭제", size=16, weight="bold")
        delete_popup.content = dogdog.basic_text("선택하신 기록을 삭제하시겠습니까?")
        
        # [수정 사항] 버튼 리스트를 명시적으로 덮어씌워 확실하게 이벤트 연결
        delete_popup.actions = [
            ft.TextButton("Cancel", on_click=self.close_delete_popup),
            ft.TextButton("OK", on_click=lambda e: self.page.run_task(self.confirm_delete, e))
        ]

        if delete_popup not in self.page.overlay:
            self.page.overlay.append(delete_popup)

        delete_popup.open = True
        self.page.update()

    def close_delete_popup(self, e):
        """[추가] 삭제 확인 팝업 닫기"""
        self.popup.event_popup.open = False
        self.page.update()

    async def confirm_delete(self, e):
        """[수정] OK 버튼 클릭 시 실행되는 비동기 삭제 함수"""
        # 1. 팝업부터 즉시 닫기
        self.popup.event_popup.open = False
        self.page.update()

        # [방어 코드 추가] 선택된 로그 데이터가 없으면 중단
        if not self.selected_log_data or not self.selected_log_data.get("id"):
            print("Confirm Delete Error: No log selected.")
            return

        # 2. 기존 API 호출 및 삭제 로직 수행
        # [문제 1 해결] log_id를 int로 형변환하여 422 에러 방지
        log_id = int(self.selected_log_data.get("id"))
        domain = self.selected_log_data.get("domain")
        
        endpoint = f"/logs/feeding/{log_id}" if domain == "feeding" else f"/logs/numeric/{log_id}"

        try:
            res = await self.api_client.delete(endpoint)
            if res.status_code in [200, 204]:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("기록이 삭제되었습니다."))
                
                # [Step 1] 선택 상태 초기화
                self.selected_log_data = None
                self.selected_ui_container = None
                
                # [Step 1] refresh 콜백을 await로 호출하여 UI 동기화 보장
                if self.on_refresh_callback:
                    await self.on_refresh_callback()
            else:
                self.page.snack_bar = ft.SnackBar(content=ft.Text(f"삭제에 실패했습니다. (코드: {res.status_code})"))
        except Exception as err:
            print(f"Delete Error: {err}")
            self.page.snack_bar = ft.SnackBar(content=ft.Text("서버 오류가 발생했습니다."))
        
        self.page.snack_bar.open = True
        self.page.update()

    def history_edit(self, e):
        """수정 버튼 클릭 시"""
        if not self.selected_log_data:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("수정할 기록을 선택해주세요."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        # 수정 팝업 호출 (grid_view.bottom_sheet 연동)
        from domains.logs.views import grid_view
        domain = self.selected_log_data.get("domain")
        
        # numeric의 경우 category에 따라 call 값 매칭
        call_map = {
            "water": "watering",
            "walk": "daily_walks",
            "poop": "hygiene_bowel",
            "weight": "health_log",
            "bcs": "health_log"
        }
        
        call = "feeding" if domain == "feeding" else call_map.get(self.selected_log_data.get("category"), "status_log")
        
        self.page.run_task(
            grid_view.bottom_sheet, 
            e, self.page, self.popup, call, 
            on_refresh_callback=self.on_refresh_callback,
            edit_mode=True,
            log_data=self.selected_log_data
        )
