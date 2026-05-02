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
        [완벽 정렬 로직] datetime 객체로 변환하여 timestamp(숫자) 기반으로 절대 꼬이지 않게 정렬
        """
        storage = self.page.session.store
        now = datetime.datetime.now()
        today_str = now.strftime("%Y.%m.%d")

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
                domain = log.get("domain", "")
                pet_food = log.get("pet_food") or {}

                # 1. 날짜 추출
                raw_date = (
                    log.get("log_date")
                    or log.get("feeding_date")
                    or log.get("date")
                    or pet_food.get("feeding_date")
                    or today_str.replace(".", "-")
                )
                d_str = str(raw_date).split("T")[0].split(" ")[0].strip()
                if d_str.replace("-", ".") not in valid_dates:
                    continue

                # 2. 시간 추출 및 UI 데이터 강제 덮어쓰기 (Data Masking)
                if domain == "feeding":
                    t_raw = (
                        log.get("feeding_time")
                        or log.get("time")
                        or pet_food.get("feeding_time")
                        or "00:00:00"
                    )
                    t_val = str(t_raw).split(".")[0].replace("Z", "").strip().split(" ")[-1]
                    if len(t_val.split(":")) == 2:
                        t_val += ":00"

                    sort_iso = f"{d_str}T{t_val}"

                    # [Deep Masking] 1차: 최상위 log 객체 조작
                    log["last_update"]  = sort_iso
                    log["log_date"]     = sort_iso
                    log["date"]         = sort_iso
                    log["time"]         = t_val
                    log["feeding_time"] = t_val

                    # [Deep Masking] 2차: 중첩된 pet_food 객체 내부까지 원천 봉쇄
                    if "pet_food" in log and isinstance(log["pet_food"], dict):
                        log["pet_food"]["last_update"]   = sort_iso
                        log["pet_food"]["log_date"]      = sort_iso
                        log["pet_food"]["feeding_date"]  = d_str
                        log["pet_food"]["feeding_time"]  = t_val
                        log["pet_food"]["time"]          = t_val
                else:
                    raw_log_date = str(log.get("log_date", f"{d_str}T00:00:00"))
                    t_val = raw_log_date.replace(" ", "T").replace("Z", "").split(".")[0].split("T")[-1]
                    if len(t_val.split(":")) == 2:
                        t_val += ":00"

                # 3. 완벽한 정렬을 위한 Timestamp 숫자 생성
                try:
                    dt_obj = datetime.datetime.strptime(f"{d_str}T{t_val}", "%Y-%m-%dT%H:%M:%S")
                    sort_ts = dt_obj.timestamp()
                except:
                    sort_ts = 0.0

                log["sort_timestamp"] = sort_ts
                filtered_logs.append(log)

            except Exception as e:
                print(f"[WARN] Log parsing error: {e}")

        # 오직 숫자(Timestamp) 기준으로만 내림차순 정렬 (도메인 구끄림 방지)
        filtered_logs.sort(key=lambda x: x.get("sort_timestamp", 0.0), reverse=True)
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