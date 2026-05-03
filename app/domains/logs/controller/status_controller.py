import flet as ft
import datetime
from domains.logs.controller.grid_controller import GridController


class StatusController:
    """
    [Controller] StatusController
    역할: 그리드(Logs) 팝업 메뉴의 데이터 처리, 세션 스토리지 관리, API 호출을 전담합니다.
    - View에서 분리되어 순수 비즈니스 로직과 이벤트 라우팅만 처리합니다.
    """

    def __init__(
        self, page, popup, on_refresh_callback=None, edit_mode=False, log_data=None
    ):
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self.on_refresh_callback = on_refresh_callback
        self.edit_mode = edit_mode
        self.log_data = log_data
        self.grid_ctrl = GridController(page)
        self.api_client = self.grid_ctrl.api_client

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
            try:
                self.storage.set(f"{call}_bcs_weight", int(value))
            except ValueError:
                pass
        elif is_float:
            try:
                self.storage.set(f"{call}_float_weight", float(value))
            except ValueError:
                pass
        else:
            try:
                self.storage.set(f"{call}_weight", int(value))
            except ValueError:
                pass

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
            return (
                selected_datetime.strftime("%p %H:%M")
                .replace("AM", "오전")
                .replace("PM", "오후")
            )
        return None

    def set_default_datetime(self, call):
        """초기 진입 시 날짜/시간 및 기존 데이터를 세션에 세팅 (수정 모드 대응)"""
        now = datetime.datetime.now()
        log_date_str = now.strftime("%Y-%m-%d")
        log_time_str = now.strftime("%H:%M")

        if self.edit_mode and self.log_data:
            raw_date = self.log_data.get("log_date") or self.log_data.get("date")
            if raw_date:
                try:
                    dt = datetime.datetime.fromisoformat(raw_date.replace(" ", "T"))
                    log_date_str = dt.strftime("%Y-%m-%d")
                    log_time_str = dt.strftime("%H:%M")
                except:
                    pass

            self.storage.set(f"{call}_memo", self.log_data.get("memo", ""))

            log_status = self.log_data.get("log_status")
            if log_status is not None:
                self.storage.set(f"{call}_weight", log_status)

            if call == "health_log":
                # [해결 2] category와 log_status를 기반으로 데이터 추출 및 매핑 (저장 단절 방지)
                category = self.log_data.get("category")
                log_status = self.log_data.get("log_status")
                
                try:
                    if category == "weight" and log_status is not None:
                        self.storage.set(f"{call}_float_weight", float(log_status))
                    elif category == "bcs" and log_status is not None:
                        self.storage.set(f"{call}_bcs_weight", int(float(log_status)))
                except (ValueError, TypeError):
                    pass

            if call == "feeding":
                amount = self.log_data.get("amount")
                if amount is not None:
                    self.storage.set(f"{call}_weight", amount)
                pet_food_id = self.log_data.get("pet_food_id")
                if pet_food_id is not None:
                    self.storage.set("customer_food_id", pet_food_id)

        self.storage.set(f"{call}_date", log_date_str)
        self.storage.set(f"{call}_time", log_time_str)

    async def fetch_feeding_init_data(self):
        """밥주기 팝업 진입 시 강아지 ID, 권장 급여량, 사료 정보를 조회하여 반환"""
        pet_id = (
            self.storage.get("pet_id")
            or self.storage.get("customer_pet_id")
            or self.storage.get("current_pet_id")
        )

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
                    label = (
                        f"[{brand}] {name} ({weight}g)"
                        if brand or name
                        else f"알 수 없는 사료 ({weight}g)"
                    )

                    food_options_data.append({"key": str(p_id), "text": label})
                    initial_value = str(p_id)
                    self.storage.set("customer_food_id", p_id)
                    has_food = True
                else:
                    food_options_data.append(
                        {"key": "none", "text": "현재 급여 중인 사료가 없습니다."}
                    )
            except Exception as err:
                print(f"[ERROR] 사료 정보 조회 중 오류: {err}")
                food_options_data.append(
                    {"key": "none", "text": "사료 정보를 불러올 수 없습니다."}
                )
        else:
            food_options_data.append(
                {"key": "none", "text": "강아지 정보를 찾을 수 없습니다."}
            )

        return {
            "pet_name": pet_name,
            "recommended_amount": recommended_amount,
            "has_food": has_food,
            "food_options_data": food_options_data,
            "initial_value": initial_value,
        }

    async def save_event(self, call):
        """저장 버튼 클릭 시 API 호출 및 후처리"""
        import components as dogdog

        pet_id = (
            self.storage.get("pet_id")
            or self.storage.get("customer_pet_id")
            or self.storage.get("current_pet_id")
        )

        log_date_str = self.storage.get(f"{call}_date")
        log_time_str = self.storage.get(f"{call}_time")

        if log_date_str and log_time_str:
            full_log_date = f"{log_date_str}T{log_time_str}:00"
        else:
            full_log_date = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        if call == "feeding":
            try:
                # 세션에서 사료 ID 및 급여량 추출
                food_id = self.storage.get("customer_food_id")
                amount  = self.storage.get(f"{call}_weight")

                # 필수 값 검증: 사료 ID 또는 급여량 누락 시 안내
                if not food_id or not amount:
                    self.page.snack_bar = ft.SnackBar(
                        content=dogdog.basic_text("사료 정보 또는 급여량을 입력해주세요.")
                    )
                    self.page.snack_bar.open = True
                    self.page.update()
                    return

                if self.edit_mode and self.log_data:
                    # [수정] PATCH /api/v1/logs/feeding/{pet_food_id}
                    # pet_food_id(급여 로그 PK)를 우선 사용, 없으면 id로 폴백
                    raw_id = self.log_data.get("pet_food_id") or self.log_data.get("id")
                    log_id = int(raw_id) if raw_id else 0

                    req_date = self.storage.get(f"{call}_date")
                    req_time = self.storage.get(f"{call}_time") or "00:00"

                    payload = {
                        "amount":           int(float(amount)),
                        "memo":             str(self.storage.get(f"{call}_memo") or ""),
                        "new_feeding_date": req_date,
                        "feeding_time":     f"{req_time}:00.000Z",
                    }

                    res = await self.api_client.patch(f"/logs/feeding/{log_id}", data=payload)
                    if res.status_code in [200, 201]:
                        self.page.snack_bar = ft.SnackBar(
                            content=dogdog.basic_text(
                                "급여 기록이 수정되었습니다.", color=ft.Colors.WHITE
                            ),
                            bgcolor=ft.Colors.GREEN_400,
                        )
                        self.page.snack_bar.open = True
                        await self._post_save_process()
                    else:
                        # 서버 에러 메시지를 사용자에게 노출
                        try:
                            error_msg = res.json().get("detail", "수정에 실패했습니다.")
                        except Exception:
                            error_msg = f"HTTP {res.status_code}"
                        self.page.snack_bar = ft.SnackBar(
                            content=dogdog.basic_text(f"오류: {error_msg}")
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    return
                else:
                    # [신규] 기존의 grid_ctrl.save_feeding_api 활용 (안정적인 기존 로직)
                    success = await self.grid_ctrl.save_feeding_api(call)
                    if success:
                        await self._post_save_process()
                    return

            except Exception as e:
                print(f"[ERROR] Feeding Save Error: {e}")
                return

        # 2. 통합 수치형 API (numeric) 처리
        category = None
        payload = {"log_date": full_log_date, "memo": self.storage.get(f"{call}_memo")}

        if call == "watering":
            category = "water"
            payload["log_status"] = self.storage.get(f"{call}_weight")
        elif call == "daily_walks":
            category = "walk"
            payload["log_status"] = self.storage.get(f"{call}_weight")
        elif call == "hygiene_bowel":
            category = "poop"
            payload["log_status"] = self.storage.get(f"{call}_weight")
        elif call == "health_log":
            category = "weight_bcs"
            if self.edit_mode and self.log_data:
                # [해결 3] 수정 모드 시 통합 API 명세에 맞춰 log_status 단일 필드 전송
                log_category = self.log_data.get("category")
                try:
                    if log_category == "weight":
                        val = self.storage.get(f"{call}_float_weight")
                        payload["log_status"] = float(val) if val is not None and str(val).strip() != "" else None
                    elif log_category == "bcs":
                        val = self.storage.get(f"{call}_bcs_weight")
                        payload["log_status"] = int(float(val)) if val is not None and str(val).strip() != "" else None
                except (ValueError, TypeError):
                    payload["log_status"] = None
            else:
                # [신규 등록] 기존처럼 weight와 bcs 두 개를 모두 전송
                w_val = self.storage.get(f"{call}_float_weight")
                b_val = self.storage.get(f"{call}_bcs_weight")
                payload["weight"] = float(w_val) if w_val is not None and str(w_val).strip() != "" else None
                payload["bcs"] = int(float(b_val)) if b_val is not None and str(b_val).strip() != "" else None
        elif call == "status_log":
            category = "status"

        if not category:
            return

        # 3. API 호출 (POST or PUT)
        try:
            if self.edit_mode and self.log_data:
                # [해결됨] "id" 키 에러를 방지하고 "pet_log_numeric_id"를 정확하게 뽑아냅니다.
                raw_id = self.log_data.get("id") or self.log_data.get(
                    "pet_log_numeric_id"
                )
                log_id = int(raw_id) if raw_id else 0

                res = await self.api_client.put(f"/logs/numeric/{log_id}", data=payload)
            else:
                res = await self.api_client.post(
                    f"/logs/numeric/{category}/{pet_id}", data=payload
                )

            if res.status_code in [200, 201]:
                msg = (
                    "기록이 수정되었습니다."
                    if self.edit_mode
                    else "기록이 저장되었습니다."
                )
                self.page.snack_bar = ft.SnackBar(
                    content=dogdog.basic_text(msg, color=ft.Colors.WHITE),
                    bgcolor=ft.Colors.GREEN_400,
                )
                self.page.snack_bar.open = True
                await self._post_save_process()
            else:
                error_msg = res.json().get("detail", "작업에 실패했습니다.")
                self.page.snack_bar = ft.SnackBar(
                    content=dogdog.basic_text(f"오류: {error_msg}")
                )
                self.page.snack_bar.open = True
                self.page.update()
        except Exception as e:
            print(f"[ERROR] API 전송 중 오류 발생: {e}")
            self.page.snack_bar = ft.SnackBar(
                content=dogdog.basic_text("서버 통신 중 오류가 발생했습니다.")
            )
            self.page.snack_bar.open = True
            self.page.update()

    async def _post_save_process(self):
        """저장 성공 후 공통 처리 로직"""
        self.popup.bottom_sheet_popup.open = False
        self.page.pubsub.send_all("update_dashboard")
        self.page.update()

        if self.on_refresh_callback:
            if hasattr(self.on_refresh_callback, "__call__"):
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
            pass
