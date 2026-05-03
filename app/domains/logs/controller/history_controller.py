import flet as ft
from api_client import ApiClient
import datetime

class HistoryController:
    """
    [Controller] HistoryController
    역할: 히스토리(/history) 화면의 비즈니스 로직과 API 데이터 조회를 담당합니다.
    """
    def __init__(self, page):
        self.page = page
        self.api_client = ApiClient(page)
        self.selected_log_data = None
        self.selected_ui_container = None
        self.log_containers = {}
        self.on_refresh_callback = None
        self.saved_tab_index = 0

    async def get_timeline_logs(self, pet_id: int):
        """
        [리팩터링] 세션 상태에 따라 주간/일간 모드를 판별하여 최적의 파라미터로 데이터를 Fetch합니다.
        """
        storage = self.page.session.store
        query_params = {}

        # 1. 주간/일간 모드 판별 및 파라미터 생성
        weekly_data = storage.get("select_log_week")
        daily_data = storage.get("select_log_date")

        if weekly_data:
            # [주간 모드] "YYYY.MM.DD ~ YYYY.MM.DD" 분리 및 포맷팅
            try:
                dates = weekly_data.split("~")
                start_date = dates[0].strip().replace(".", "-")
                end_date = dates[1].strip().replace(".", "-")
                query_params = {"start_date": start_date, "end_date": end_date}
            except Exception as e:
                print(f"[HistoryController] 주간 날짜 파싱 실패: {e}")
                query_params = {"date": datetime.datetime.now().strftime("%Y-%m-%d")}
        
        elif daily_data:
            # [일간 모드] 특정 날짜 포맷팅
            query_params = {"date": str(daily_data).replace(".", "-")}
        
        else:
            # [기본값] 오늘 날짜
            query_params = {"date": datetime.datetime.now().strftime("%Y-%m-%d")}

        try:
            # [DEBUG] API 호출 직전 파라미터 로그
            print(f"[DEBUG] History API 요청: /logs/{pet_id} | Params: {query_params}")
            
            # 2. 통합 API 호출 (단일 호출)
            response = await self.api_client.get(
                f"/logs/{pet_id}", 
                params=query_params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"[DEBUG] History API 응답 원본 수신 완료")
                
                # 무적의 파싱 로직 적용
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    return data.get("data", [])
                return []
            else:
                print(f"[HistoryController] API 호출 실패 (코드: {response.status_code})")
                return []
                
        except Exception as e:
            print(f"[ERROR] History 데이터 Fetch 중 상세 에러: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    def get_filtered_logs_and_date_str(self, logs: list):
        """
        [리팩터링] 통합 API 스키마(timestamp) 전용 파싱 및 하위 호환성 Key 주입 로직
        """
        storage = self.page.session.store
        now = datetime.datetime.now()
        today_str = now.strftime("%Y.%m.%d")

        # 1. 필터링 기준 날짜 설정
        if storage.get("select_log_date"):
            date_str = storage.get("select_log_date")
            valid_dates = [date_str]
        elif storage.get("select_log_week"):
            date_str = storage.get("select_log_week")
            valid_dates = [(now - datetime.timedelta(days=i)).strftime("%Y.%m.%d") for i in range(7)]
        else:
            date_str = today_str
            valid_dates = [date_str]

        filtered_logs = []
        for log in logs:
            try:
                # [해결 1] 단일 timestamp 기반 파싱 (레거시 객체 탐색 제거)
                ts_raw = log.get("timestamp")
                if not ts_raw:
                    continue

                # 날짜 및 시간 분리 (YYYY-MM-DDTHH:MM:SS)
                dt_part = ts_raw.split("T")[0]  # YYYY-MM-DD
                tm_part = ts_raw.split("T")[1][:5] if "T" in ts_raw else "00:00" # HH:MM

                # [해결 2] 날짜 필터링 (API의 YYYY-MM-DD를 UI의 YYYY.MM.DD로 변환 후 비교)
                ui_date_format = dt_part.replace("-", ".")
                if ui_date_format not in valid_dates:
                    continue

                # [해결 3] 하위 호환성 Key 주입 (기존 View 컴포넌트 보호)
                log["date"] = ui_date_format
                log["time"] = tm_part
                log["feeding_time"] = tm_part
                log["log_date"] = ts_raw  # 원본 유지
                log["display_time"] = log.get("display_time", tm_part)

                # [해결 2] 초 단위 정밀 정렬을 위한 datetime 객체 변환 (.timestamp() 활용)
                try:
                    # ISO 문자열 전체를 파싱하여 Seconds/Microseconds까지 포함된 Float값 생성
                    dt_obj = datetime.datetime.fromisoformat(ts_raw)
                    log["sort_timestamp"] = dt_obj.timestamp()
                except Exception as te:
                    print(f"[HistoryController] Timestamp 정밀 파싱 실패 ({ts_raw}): {te}")
                    log["sort_timestamp"] = 0.0

                filtered_logs.append(log)

            except Exception as e:
                print(f"[HistoryController] 데이터 가공 중 오류: {e}")

        # [해결] 튜플을 활용한 다중 정렬 (1차: 시간순, 2차: ID순)
        # 시간이 동일하더라도 ID가 큰(최신) 데이터가 위로 오도록 확실하게 정렬합니다.
        filtered_logs.sort(
            key=lambda x: (x.get("sort_timestamp", 0.0), x.get("id", 0)), 
            reverse=True
        )
        
        return filtered_logs, date_str

    def register_container(self, log_key: str, container):
        if log_key not in self.log_containers:
            self.log_containers[log_key] = []
        self.log_containers[log_key].append(container)

    def select_log(self, log_data, container):
        """[수정 2] PK 다중 탐색 + 전체 초기화 후 대상만 선택"""
        domain_str = log_data.get("domain", "unknown")
        # ★ PK가 다를 경우를 대비한 다중 탐색
        log_id = (
            log_data.get("id")
            or log_data.get("pet_food_id")
            or log_data.get("pet_log_numeric_id")
        )
        current_log_key = f"{domain_str}_{log_id}"

        # 1. 무조건 화면의 모든 컨테이너를 투명하게 초기화 (다중 선택 원천 차단)
        for key, containers in self.log_containers.items():
            for c in containers:
                c.bgcolor = ft.Colors.TRANSPARENT
                c.ink = False
                c.update()

        # 이전에 선택했던 것과 동일한 항목을 다시 누르면 선택 해제 (토글)
        prev_id = (
            self.selected_log_data.get("id")
            or self.selected_log_data.get("pet_food_id")
            or self.selected_log_data.get("pet_log_numeric_id")
        ) if self.selected_log_data else None

        is_same_log = (
            self.selected_log_data is not None
            and str(prev_id) == str(log_id)
            and self.selected_log_data.get("domain") == domain_str
        )

        if is_same_log:
            self.selected_log_data = None
            self.selected_ui_container = None
        else:
            self.selected_log_data = log_data
            self.selected_ui_container = container
            if current_log_key in self.log_containers:
                for c in self.log_containers[current_log_key]:
                    c.bgcolor = ft.Colors.GREY_200
                    c.ink = False
                    c.update()

    def history_delete(self, e):
        if not self.selected_log_data:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("삭제할 기록을 선택해주세요."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        import components as dogdog
        delete_popup = self.popup.event_popup
        delete_popup.title = dogdog.basic_text("기록 삭제", size=16, weight="bold")
        delete_popup.content = dogdog.basic_text("선택하신 기록을 삭제하시겠습니까?")
        
        delete_popup.actions = [
            ft.TextButton("Cancel", on_click=self.close_delete_popup),
            ft.TextButton("OK", on_click=lambda e: self.page.run_task(self.confirm_delete, e))
        ]

        if delete_popup not in self.page.overlay:
            self.page.overlay.append(delete_popup)

        delete_popup.open = True
        self.page.update()

    def close_delete_popup(self, e):
        self.popup.event_popup.open = False
        self.page.update()

    async def confirm_delete(self, e):
        self.popup.event_popup.open = False
        self.page.update()

        if not self.selected_log_data or not self.selected_log_data.get("id"):
            return

        log_id = int(self.selected_log_data.get("id"))
        domain = self.selected_log_data.get("domain")
        
        if domain == "feeding":
            endpoint = f"/logs/feeding/{log_id}"
        else:
            endpoint = f"/logs/numeric/{log_id}"

        try:
            res = await self.api_client.delete(endpoint)
            if res.status_code in [200, 204]:
                self.page.snack_bar = ft.SnackBar(content=ft.Text("기록이 삭제되었습니다."))
                self.selected_log_data = None
                self.selected_ui_container = None
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
        if not self.selected_log_data:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("수정할 기록을 선택해주세요."))
            self.page.snack_bar.open = True
            self.page.update()
            return

        from domains.logs.views import grid_view
        domain = self.selected_log_data.get("domain")
        
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