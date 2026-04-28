import flet as ft
import components as dogdog
from api_client import ApiClient
class PetfoodController:
    def __init__(self, page: ft.Page, popup):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self._search_task = None  # 디바운싱을 위한 태스크 변수
        # -----------------------------------------------------------------------------------------------
        # Food List Selected Picker and Bottom Sheet
        # -----------------------------------------------------------------------------------------------
        self.selected_food_id = None
        self.food_list_column = ft.Column(
            height=(self.page.height/7)*2, # type: ignore
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self.food_search_field = dogdog.list_input_textfield(
            hint_text="Search", on_change=self.on_food_search_change
        )
        self.food_search_field.autofocus = True
        self.food_bottom_sheet = self.popup.bottom_sheet_popup
        self.food_bottom_sheet_contents = self.popup.bottom_sheet_controls
        self.food_bottom_sheet_contents.clear()
        self.food_bottom_sheet_contents.append(dogdog.basic_text(value="사료 검색", size=25, weight="bold"))
        self.food_bottom_sheet_contents.append(ft.Divider())
        self.food_bottom_sheet_contents.append(self.food_search_field)
        self.food_bottom_sheet_contents.append(self.food_list_column)
        self.food_picker_field = dogdog.picker_field(
            text="현재 급여 중인 사료를 선택해주세요.",
            on_click=self.open_food_bottom_sheet,
            icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        )
        if self.storage.get(key="food_text"):
            self.food_picker_field.content.controls[0].value = ( # type: ignore
                self.storage.get(key="food_text")
            )
        self.food_list = dogdog.update_item_list(
            list_column=self.food_list_column, 
            search_data=[],
            select_key=self.selected_food_id, 
            select_value=self.select_food,
            keyword=""
        )
        self.product_weight_list = dogdog.dropdown_menu(
            label="사료의 용량을 선택해주세요.",
            event=self.food_product_weight_set,
            options=[]
        )
        if self.storage.get(key="product_id"):
            self.product_weight_list.visible = True
            self.product_weight_list.value = str(self.storage.get(key="product_id"))
        else: self.product_weight_list.visible = False
    # ---------------------------------------------------------------------------------------------------
    # Food List Picker Event
    # ---------------------------------------------------------------------------------------------------
    def open_food_bottom_sheet(self, e):
        self.food_search_field.value = ""
        self.food_list
        if self.food_bottom_sheet not in self.page.overlay:
            self.page.overlay.append(self.food_bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(self.food_bottom_sheet)
        self.food_bottom_sheet.open = True
        self.page.update()

    async def on_food_search_change(self, e):
        """디바운싱 로직이 적용된 2-Step API 사료 검색 핸들러"""
        keyword = e.control.value
        import asyncio

        # 이전 실행 중인 검색 작업이 있다면 취소 (디바운싱)
        if self._search_task:
            self._search_task.cancel()

        async def search_with_debounce():
            try:
                # 0.5초 대기
                await asyncio.sleep(0.5)
                
                if not keyword or len(keyword) < 1:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(dogdog.basic_text(value="검색어를 입력해 주세요.", size=14))
                    self.page.update()
                    return

                # UI에 검색 중임을 표시
                self.food_list_column.controls.clear()
                self.food_list_column.controls.append(dogdog.basic_text(value="검색 중...", size=14))
                self.page.update()

                api_client = ApiClient(self.page)
                
                # [Step 1] 상품명 검색 (/api/v1/products/name)
                res_name = await api_client.get("/products/name", params={"keyword": keyword})
                if res_name.status_code != 200:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(dogdog.basic_text(value="검색 결과를 가져올 수 없습니다.", size=14))
                    self.page.update()
                    return

                products = res_name.json().get("data", [])
                if not products:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(dogdog.basic_text(value="검색 결과가 없습니다.", size=14))
                    self.page.update()
                    return

                # [Step 2] 각 상품별 무게 옵션 병렬 조회 (/api/v1/products/weights)
                async def fetch_weights(product_detail_id, product_name):
                    try:
                        res_w = await api_client.get("/products/weights", params={"product_detail_id": product_detail_id})
                        if res_w.status_code == 200:
                            weights_data = res_w.json().get("data", [])
                            # 진짜 식별자인 product_id와 무게 정보를 페어링
                            return [
                                [
                                    f"{w.get('product_id')}|{w.get('weight')}", 
                                    f"{product_name} {w.get('weight')}g X1"
                                ] 
                                for w in weights_data if w.get("active")
                            ]
                    except Exception:
                        return []
                    return []

                # N+1 방어를 위해 asyncio.gather로 병렬 처리
                tasks = [fetch_weights(p.get("product_detail_id"), p.get("product_name")) for p in products]
                results = await asyncio.gather(*tasks)
                
                # 2차원 리스트 평탄화
                search_list = [item for sublist in results for item in sublist]

                if not search_list:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(dogdog.basic_text(value="선택 가능한 옵션이 없습니다.", size=14))
                    self.page.update()
                    return

                # UI 바인딩
                self.food_list = dogdog.update_item_list(
                    list_column=self.food_list_column,
                    search_data=search_list,
                    select_key=self.selected_food_id, 
                    select_value=self.select_food, 
                    keyword=keyword
                )
                self.page.update()

            except asyncio.CancelledError:
                pass
            except Exception as err:
                print(f"[API Error] 사료 검색 실패: {err}")
                self.food_list_column.controls.clear()
                self.food_list_column.controls.append(dogdog.basic_text(value="서버 오류가 발생했습니다.", size=14))
                self.page.update()

        # 새로운 검색 태스크 시작
        self._search_task = asyncio.create_task(search_with_debounce())
            
    async def select_food(self, compound_id, display_name):
        """항목 클릭 시 진짜 식별자인 product_id와 무게 정보를 세션에 저장"""
        if not compound_id or "|" not in compound_id:
            return
            
        try:
            product_id_str, weight_str = compound_id.split("|")
            product_id = int(product_id_str)
            weight = int(float(weight_str))

            # 온보딩 최종 저장에 필요한 진짜 데이터 저장
            self.storage.set(key="product_id", value=product_id)
            self.storage.set(key="product_weight", value=weight)
            self.food_picker_field.content.controls[0].value = display_name
            self.storage.set(key="food_text", value=display_name)
            
            # 검색창 닫기 및 UI 갱신
            self.food_bottom_sheet.open = False
            self.page.update()
            
            # 통합 선택이 완료되었으므로 이전의 무게 드롭다운은 숨김
            self.product_weight_list.visible = False
            self.product_weight_list.update()
            
        except Exception as e:
            print(f"[UI Error] 사료 선택 처리 실패: {e}")

    def food_product_weight_set(self, e):
        self.page.session.store.set(key="product_id", value=e.control.value)
        # Dropdown options contain the weight in their text
        selected_option = next((opt for opt in self.product_weight_list.options if opt.key == e.control.value), None)
        if selected_option:
            try:
                weight = selected_option.text.replace("g", "")
                self.page.session.store.set(key="product_weight", value=int(float(weight)))
            except (ValueError, TypeError):
                pass
# -------------------------------------------------------------------------------------------------------
def pet_food_view(page: ft.Page, popup):
    # ---------------------------------------------------------------------------------------------------
    # Default Value Class
    # ---------------------------------------------------------------------------------------------------
    pet_food_controller = PetfoodController(page=page, popup=popup)
    storage = page.session.store
    # ---------------------------------------------------------------------------------------------------
    # Pet Food Weight Field
    # ---------------------------------------------------------------------------------------------------
    def on_food_weight_change(e):
        try:
            page.session.store.set("food_weight", int(float(e.control.value)))
        except (ValueError, TypeError):
            pass
    selected_food_weight = dogdog.input_textfield(
        hint_text="현재 급여 중인 사료의 잔여량을 적어주세요", input_type="int", suffix="g",
        on_change=on_food_weight_change
    )
    if storage.get("food_weight"):
        selected_food_weight.value = storage.get("food_weight") # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Pet Feeding Food Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="현재 급여 중인 사료", weight="bold"),
        pet_food_controller.food_picker_field,
        pet_food_controller.product_weight_list,
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight
    ]
    return content_column
# -------------------------------------------------------------------------------------------------------
def pet_food_view(page: ft.Page, popup):
    # ---------------------------------------------------------------------------------------------------
    # Default Value Class
    # ---------------------------------------------------------------------------------------------------
    pet_food_controller = PetfoodController(page=page, popup=popup)
    storage = page.session.store
    # ---------------------------------------------------------------------------------------------------
    # Pet Food Weight Field
    # ---------------------------------------------------------------------------------------------------
    def on_food_weight_change(e):
        try:
            page.session.store.set("food_weight", int(float(e.control.value)))
        except (ValueError, TypeError):
            pass
    selected_food_weight = dogdog.input_textfield(
        hint_text="현재 급여 중인 사료의 잔여량을 적어주세요", input_type="int", suffix="g",
        on_change=on_food_weight_change
    )
    if storage.get("food_weight"):
        selected_food_weight.value = storage.get("food_weight") # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Pet Feeding Food Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="현재 급여 중인 사료", weight="bold"),
        pet_food_controller.food_picker_field,
        pet_food_controller.product_weight_list,
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight
    ]
    return content_column