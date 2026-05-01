import flet as ft
import datetime
from domains.logs.controller.grid_controller import GridController

class StatusController:
    """
    [Controller] StatusController
    역할: 그리드(Logs) 팝업 메뉴의 데이터 처리, 세션 스토리지 관리, API 호출을 전담합니다.
    - View에서 분리되어 순수 비즈니스 로직과 이벤트 라우팅만 처리합니다.
    """
    def __init__(self, page, popup, on_refresh_callback=None):
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self.on_refresh_callback = on_refresh_callback
        self.grid_ctrl = GridController(page)
        self.api_client = self.grid_ctrl.api_client  # GridController에서 초기화된 api_client 활용
        
        # 팝업 초기화 시 기존 customer_food_id 제거
        if self.storage.get("customer_food_id"):
            self.storage.remove("customer_food_id")

    def change_customer_food_id(self, value):
        try:
            self.storage.set("customer_food_id", int(value))
        except ValueError:
            pass

    def change_weight(self, call, value, is_float=False, is_bcs=False):
        if is_bcs:
            try: self.storage.set(f"{call}_bcs_weight", int(value))
            except ValueError: pass
        elif is_float:
            try: self.storage.set(f"{call}_float_weight", float(value))
            except ValueError: pass
        else:
            try: self.storage.set(f"{call}_weight", int(value))
            except ValueError: pass

    def change_memo(self, call, value):
        self.storage.set(f"{call}_memo", str(value))

    def change_date(self, call, selected_datetime):
        if selected_datetime:
            now = datetime.timedelta(hours=9)
            val = selected_datetime + now
            self.storage.set(f"{call}_date", val.strftime("%Y-%m-%d"))
            return val.strftime("%Y.%m.%d")
        return None

    def change_time(self, call, selected_datetime):
        if selected_datetime:
            self.storage.set(f"{call}_time", selected_datetime.strftime("%H:%M"))
            return selected_datetime.strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후")
        return None

    def set_default_datetime(self, call):
        """초기 진입 시 현재 날짜/시간을 세션에 세팅"""
        now = datetime.datetime.now()
        self.storage.set(f"{call}_date", now.strftime("%Y-%m-%d"))
        self.storage.set(f"{call}_time", now.strftime("%H:%M"))

    async def fetch_feeding_init_data(self):
        """
        밥주기 팝업 진입 시 강아지 ID, 권장 급여량, 사료 정보를 조회하여 반환
        """
        pet_id = (self.storage.get("pet_id") or 
                  self.storage.get("customer_pet_id") or 
                  self.storage.get("current_pet_id"))
                  
        pet_name = self.storage.get("customer_pet_name") or "아이"
        recommended_amount = await self.grid_ctrl.get_one_time_feeding_amount(pet_id)
        
        has_food = False
        food_options_data = []
        initial_value = None

        if pet_id:
            try:
                food_data = await self.grid_ctrl.get_pet_food_info(pet_id)
                if food_data:
                    p_id = food_data.get("product_id")
                    brand = food_data.get("product_brand") or ""
                    name = food_data.get("product_name") or ""
                    weight = food_data.get("product_weight") or 0
                    label = f"[{brand}] {name} ({weight}g)" if brand or name else f"알 수 없는 사료 ({weight}g)"
                    
                    food_options_data.append({"key": str(p_id), "text": label})
                    initial_value = str(p_id)
                    self.storage.set("customer_food_id", p_id)
                    has_food = True
                else:
                    food_options_data.append({"key": "none", "text": "현재 급여 중인 사료가 없습니다."})
            except Exception as err:
                print(f"[ERROR] 사료 정보 조회 중 오류: {err}")
                food_options_data.append({"key": "none", "text": "사료 정보를 불러올 수 없습니다."})
        else:
            food_options_data.append({"key": "none", "text": "강아지 정보를 찾을 수 없습니다."})

        return {
            "pet_name": pet_name,
            "recommended_amount": recommended_amount,
            "has_food": has_food,
            "food_options_data": food_options_data,
            "initial_value": initial_value
        }

    async def save_event(self, call):
        """저장 버튼 클릭 시 API 호출 및 후처리"""
        import components as dogdog
        
        # 0. 공통 정보 (pet_id, date, time)
        pet_id = (self.storage.get("pet_id") or 
                  self.storage.get("customer_pet_id") or 
                  self.storage.get("current_pet_id"))
        
        log_date_str = self.storage.get(f"{call}_date")
        log_time_str = self.storage.get(f"{call}_time")
        
        # 날짜/시간 결합
        if log_date_str and log_time_str:
            full_log_date = f"{log_date_str}T{log_time_str}:00"
        else:
            full_log_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # 1. 밥주기(feeding)는 기존 전용 로직 활용
        if call == "feeding":
            if not self.storage.get("customer_food_id") or not self.storage.get(f"{call}_weight"):
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("사료 정보 또는 급여량을 입력해주세요."))
                self.page.snack_bar.open = True
                self.page.update()
                return
            success = await self.grid_ctrl.save_feeding_api(call)
            if success:
                await self._post_save_process()
            return

        # 2. 통합 수치형 API (numeric) 처리
        category = None
        payload = {"log_date": full_log_date, "memo": self.storage.get(f"{call}_memo")}

        if call == "watering":
            category = "water"
            val = self.storage.get(f"{call}_weight")
            if val is None:
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("물 섭취량을 입력해주세요."))
                self.page.snack_bar.open = True
                self.page.update()
                return
            payload["log_status"] = val

        elif call == "daily_walks":
            category = "walk"
            val = self.storage.get(f"{call}_weight")
            if val is None:
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("산책 시간을 입력해주세요."))
                self.page.snack_bar.open = True
                self.page.update()
                return
            payload["log_status"] = val

        elif call == "hygiene_bowel":
            category = "poop"
            val = self.storage.get(f"{call}_weight")
            if val is None:
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("배변 스코어를 선택해주세요."))
                self.page.snack_bar.open = True
                self.page.update()
                return
            payload["log_status"] = val

        elif call == "health_log":
            category = "weight_bcs"
            weight = self.storage.get(f"{call}_float_weight")
            bcs = self.storage.get(f"{call}_bcs_weight")
            if weight is None and bcs is None:
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("몸무게 또는 BCS를 입력해주세요."))
                self.page.snack_bar.open = True
                self.page.update()
                return
            payload["weight"] = weight
            payload["bcs"] = bcs

        if not category:
            return

        # 3. API 호출
        try:
            res = await self.api_client.post(f"/logs/numeric/{category}/{pet_id}", data=payload)
            if res.status_code in [200, 201]:
                self.page.snack_bar = ft.SnackBar(
                    content=dogdog.basic_text("기록이 저장되었습니다.", color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_400
                )
                self.page.snack_bar.open = True
                await self._post_save_process()
            else:
                error_msg = res.json().get("detail", "저장에 실패했습니다.")
                self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text(f"오류: {error_msg}"))
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as e:
            print(f"[ERROR] API 전송 중 오류 발생: {e}")
            self.page.snack_bar = ft.SnackBar(content=dogdog.basic_text("서버 통신 중 오류가 발생했습니다."))
            self.page.snack_bar.open = True
            self.page.update()

    async def _post_save_process(self):
        """저장 성공 후 공통 처리 로직"""
        self.popup.bottom_sheet_popup.open = False
        self.page.pubsub.send_all("update_dashboard")
        self.page.update()
        
        if self.on_refresh_callback:
            if hasattr(self.on_refresh_callback, '__call__'):
                await self.on_refresh_callback()

    def button_event(self, e, call, content):
        """버튼 클릭 이벤트 라우터 (View에서 호출)"""
        import asyncio
        if content == "save":
            asyncio.create_task(self.save_event(call))
        elif content == "cancel":
            self.popup.bottom_sheet_popup.open = False
            self.page.update()
        elif content == "feeding_add":
            # 사료 등록 화면으로 이동 로직 (생략)
            pass
