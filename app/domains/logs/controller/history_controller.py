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
                
                # 1. 날짜 추출 (안전하게)
                raw_date = (
                    log.get("log_date")
                    or log.get("feeding_date")
                    or log.get("date")
                    or pet_food.get("feeding_date")
                    or pet_food.get("date")
                    or today_str.replace(".", "-")
                )

                d_str = str(raw_date).split("T")[0].split(" ")[0].strip()
                date_part = d_str.replace("-", ".")

                if date_part not in valid_dates:
                    continue

                # [수술 1] 무조건 HH:MM:SS 포맷으로 강제 정규화
                if domain == "feeding":
                    t_raw = (
                        log.get("feeding_time")
                        or log.get("time")
                        or pet_food.get("feeding_time")
                        or pet_food.get("time")
                        or "00:00:00"
                    )
                    t_val = str(t_raw).split(".")[0].replace("Z", "").strip().split(" ")[-1]
                else:
                    raw_log_date = str(log.get("log_date", f"{d_str}T00:00:00"))
                    if "T" in raw_log_date:
                        t_val = raw_log_date.split("T")[-1].split(".")[0].replace("Z", "")
                    elif " " in raw_log_date:
                        t_val = raw_log_date.split(" ")[-1].split(".")[0].replace("Z", "")
                    else:
                        t_val = str(log.get("time") or log.get("log_time") or "00:00:00").split(".")[0]

                # HH:MM:SS 3파트로 반드시 맞춤 (에러 방지)
                t_parts = t_val.split(":")
                if len(t_parts) == 1:
                    t_val = f"{t_parts[0]:0>2}:00:00"
                elif len(t_parts) == 2:
                    t_val = f"{t_parts[0]:0>2}:{t_parts[1]:0>2}:00"
                else:
                    t_val = f"{t_parts[0]:0>2}:{t_parts[1]:0>2}:{t_parts[2][:2]:0>2}"

                sort_iso = f"{d_str}T{t_val}"
                log["sort_time"] = sort_iso

                # 프론트가 엉뚱한 업데이트 시간 대신 진짜 시간을 표시하도록 강제 주입
                if domain == "feeding":
                    log["last_update"] = sort_iso
                    log["log_date"]    = sort_iso
                    log["time"]        = t_val

                filtered_logs.append(log)

            except Exception as e:
                print(f"[WARN] Log parsing error: {e}")
                log["sort_time"] = f"{today_str.replace('.', '-')}T00:00:00"
                filtered_logs.append(log)

        # [수술 1] id 기준 완전 제거 → sort_time 단일 기준 내림차순 정렬
        filtered_logs.sort(key=lambda x: x.get("sort_time", ""), reverse=True)
        return filtered_logs, date_str

    def register_container(self, log_key: str, container):
        if log_key not in self.log_containers:
            self.log_containers[log_key] = []
        self.log_containers[log_key].append(container)

    def select_log(self, log_data, container):
        domain_str = log_data.get("domain", "unknown")
        log_id = log_data.get("id")
        current_log_key = f"{domain_str}_{log_id}"

        # 기존 선택 해제 (잔상 방지를 위해 투명색 부여)
        if self.selected_log_data:
            prev_domain = self.selected_log_data.get("domain", "unknown")
            prev_id = self.selected_log_data.get("id")
            prev_key = f"{prev_domain}_{prev_id}"
            if prev_key in self.log_containers:
                for c in self.log_containers[prev_key]:
                    c.bgcolor = ft.Colors.TRANSPARENT
                    c.ink = False  # [수술 2] update() 시 잉크 부활 방지
                    c.update()

        # 다시 누르면 선택 해제 토글
        is_same_log = (
            self.selected_log_data is not None
            and str(self.selected_log_data.get("id")) == str(log_id)
            and self.selected_log_data.get("domain", "unknown") == domain_str
        )

        if is_same_log:
            self.selected_log_data = None
            self.selected_ui_container = None
        else:
            # 새 항목 선택 시 회색칠
            self.selected_log_data = log_data
            self.selected_ui_container = container
            if current_log_key in self.log_containers:
                for c in self.log_containers[current_log_key]:
                    c.bgcolor = ft.Colors.GREY_200
                    c.ink = False  # [수술 2] update() 시 잉크 부활 방지
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