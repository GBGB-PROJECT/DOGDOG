import flet as ft
from api_client import ApiClient

class PetFoodController:
    """
    [Controller] PetFoodController
    역할: 사료 검색 API, 사료 용량 API 연동 및 상태 저장(Debouncing 검색 포함)
    """
    def __init__(self, page: ft.Page, popup):
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self._search_task = None
        self.selected_product_detail_id = None
        
        # UI 컴포넌트 초기화 (레거시 뷰 호환성 및 코드 재사용을 위해 컨트롤러에서 관리)
        import components as dogdog
        self.food_picker_field = dogdog.picker_field(
            text="현재 급여 중인 상품을 선택해주세요.",
            on_click=self.open_food_bottom_sheet_ui,
            icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        )
        self.product_weight_list = dogdog.dropdown_menu(
            label="사료의 용량을 선택해주세요.",
            event=lambda e: self.food_product_weight_set(e, self.product_weight_list),
            options=[],
        )

    def open_food_bottom_sheet_ui(self, e):
        """
        내부 관리 필드(food_picker_field)를 사용하여 사료 검색 팝업을 엽니다.
        """
        import components as dogdog
        
        # 검색 필드와 리스트 컬럼을 팝업용으로 생성
        food_list_column = ft.Column(
            height=(self.page.height / 7) * 2,
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        
        def select_food_wrapper(product_detail_id, product_name):
            self.page.run_task(self.select_food, product_detail_id, product_name, self.food_picker_field, self.product_weight_list)

        food_search_field = dogdog.list_input_textfield(
            hint_text="Search", 
            on_change=lambda ev: self.page.run_task(self.on_food_search_change, ev, food_list_column, select_food_wrapper)
        )
        food_search_field.autofocus = True

        # 팝업 내용 조립
        food_bottom_sheet_contents = self.popup.bottom_sheet_controls
        food_bottom_sheet_contents.clear()
        food_bottom_sheet_contents.append(dogdog.basic_text(value="사료 검색", size=25, weight="bold"))
        food_bottom_sheet_contents.append(ft.Divider())
        food_bottom_sheet_contents.append(food_search_field)
        food_bottom_sheet_contents.append(food_list_column)

        # 기존 로직 호출
        self.open_food_bottom_sheet(e, food_search_field, food_list_column, select_food_wrapper)

    def open_food_bottom_sheet(self, e, food_search_field, food_list_column, select_food_callback):
        food_search_field.value = ""
        food_list_column.controls.clear()
        
        food_bottom_sheet = self.popup.bottom_sheet_popup
        if food_bottom_sheet not in self.page.overlay:
            self.page.overlay.append(food_bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(food_bottom_sheet)
        food_bottom_sheet.open = True
        
        # 팝업 오픈 시 기본 사료 리스트 로딩 (초기화)
        self.page.run_task(self.fetch_initial_food_list, food_list_column, select_food_callback)
        self.page.update()

    async def fetch_initial_food_list(self, food_list_column, select_food_callback):
        import components as dogdog
        food_list_column.controls.clear()
        food_list_column.controls.append(dogdog.basic_text(value="사료 목록을 불러오는 중...", size=14))
        self.page.update()

        try:
            api_client = ApiClient(self.page)
            # 파라미터 없이 호출하여 전체/기본 사료 목록을 가져옴
            res = await api_client.get("/products/name", params={"keyword": ""})
            
            if res.status_code != 200:
                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="기본 사료 목록을 가져올 수 없습니다.", size=14))
                self.page.update()
                return

            products = res.json().get("data", [])
            if not products:
                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="사료 목록이 없습니다.", size=14))
                self.page.update()
                return

            search_list = [[str(p.get("product_detail_id")), p.get("product_name")] for p in products]

            dogdog.update_item_list(
                list_column=food_list_column,
                search_data=search_list,
                select_key=self.selected_product_detail_id,
                select_value=select_food_callback,
                keyword="",
            )
            self.page.update()
        except Exception as err:
            print(f"[API Error] 기본 사료 목록 조회 실패: {err}")
            food_list_column.controls.clear()
            food_list_column.controls.append(dogdog.basic_text(value="서버 오류가 발생했습니다.", size=14))
            self.page.update()

    async def on_food_search_change(self, e, food_list_column, select_food_callback):
        import asyncio
        import components as dogdog
        
        keyword = e.control.value

        if self._search_task:
            self._search_task.cancel()

        async def search_with_debounce():
            try:
                await asyncio.sleep(0.5)

                if not keyword or len(keyword) < 1:
                    # 검색어가 없으면 다시 기본 리스트로 복귀
                    await self.fetch_initial_food_list(food_list_column, select_food_callback)
                    return

                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="검색 중...", size=14))
                self.page.update()

                api_client = ApiClient(self.page)
                res_name = await api_client.get("/products/name", params={"keyword": keyword})
                
                if res_name.status_code != 200:
                    food_list_column.controls.clear()
                    food_list_column.controls.append(dogdog.basic_text(value="검색 결과를 가져올 수 없습니다.", size=14))
                    self.page.update()
                    return

                products = res_name.json().get("data", [])
                if not products:
                    food_list_column.controls.clear()
                    food_list_column.controls.append(dogdog.basic_text(value="검색 결과가 없습니다.", size=14))
                    self.page.update()
                    return

                search_list = [[str(p.get("product_detail_id")), p.get("product_name")] for p in products]

                dogdog.update_item_list(
                    list_column=food_list_column,
                    search_data=search_list,
                    select_key=self.selected_product_detail_id,
                    select_value=select_food_callback,
                    keyword=keyword,
                )
                self.page.update()

            except asyncio.CancelledError:
                pass
            except Exception as err:
                print(f"[API Error] 사료 이름 검색 실패: {err}")
                food_list_column.controls.clear()
                food_list_column.controls.append(dogdog.basic_text(value="서버 오류가 발생했습니다.", size=14))
                self.page.update()

        self._search_task = asyncio.create_task(search_with_debounce())

    async def select_food(self, product_detail_id, product_name, food_picker_field, product_weight_list):
        if not product_detail_id:
            return

        import components as dogdog
        try:
            self.selected_product_detail_id = product_detail_id
            self.popup.bottom_sheet_popup.open = False
            self.page.update()

            food_picker_field.content.controls[0].value = f"{product_name} (용량 확인 중...)"
            self.page.update()

            api_client = ApiClient(self.page)
            res_w = await api_client.get("/products/weights", params={"product_detail_id": product_detail_id})

            if res_w.status_code == 200:
                weights_data = res_w.json().get("data", [])
                if not weights_data:
                    food_picker_field.content.controls[0].value = f"{product_name} (선택 가능한 용량 없음)"
                    product_weight_list.visible = False
                    self.page.update()
                    return

                product_weight_list.options = [
                    dogdog.dropdown_menu_option(
                        key=str(w.get("product_id")), # [QA 수정] 실제 특정 옵션 ID를 key로 사용
                        text=f"{int(float(w.get('weight')))}g"
                    )
                    for w in weights_data if w.get("active")
                ]
                
                food_picker_field.content.controls[0].value = product_name
                self.storage.set("food_text", product_name)
                # [QA 수정] 사료 고유 ID(product_detail_id)를 세션에 정확히 저장
                self.storage.set("product_id", int(product_detail_id))
                product_weight_list.visible = True
                product_weight_list.value = None
                self.page.update()
            else:
                food_picker_field.content.controls[0].value = f"{product_name} (정보 조회 실패)"
                self.page.update()
        except Exception as e:
            print(f"[UI Error] 사료 상세 조회 처리 실패: {e}")

    def food_product_weight_set(self, e, product_weight_list):
        selected_weight_key = e.control.value
        if not selected_weight_key:
            return

        # [QA 수정] 용량 드롭다운에서 선택된 '진짜 상품 고유 ID'와 '중량'을 각각 저장
        try:
            selected_id = int(selected_weight_key)
            self.storage.set("product_id", selected_id)
            
            # 선택된 텍스트에서 숫자만 추출하여 weight 저장 (예: "1600g" -> 1600)
            selected_option = next((opt for opt in e.control.options if opt.key == selected_weight_key), None)
            if selected_option:
                weight_val = int(selected_option.text.replace("g", ""))
                self.storage.set("food_weight", weight_val)
                self.storage.set("product_weight", weight_val)
        except (ValueError, TypeError):
            pass
        self.page.update()

    def update_field(self, key: str, value):
        if value is None or str(value).strip() == "":
            self.storage.remove(key)
        else:
            self.storage.set(key, value)
