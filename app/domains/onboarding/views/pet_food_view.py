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
        self.selected_product_detail_id = None  # Step 1에서 선택된 제품 이름 ID

        self.food_list_column = ft.Column(
            height=(self.page.height / 7) * 2,  # type: ignore
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
        self.food_bottom_sheet_contents.append(
            dogdog.basic_text(value="사료 검색", size=25, weight="bold")
        )
        self.food_bottom_sheet_contents.append(ft.Divider())
        self.food_bottom_sheet_contents.append(self.food_search_field)
        self.food_bottom_sheet_contents.append(self.food_list_column)
        self.food_picker_field = dogdog.picker_field(
            text="현재 급여 중인 사료를 선택해주세요.",
            on_click=self.open_food_bottom_sheet,
            icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        )

        if self.storage.get(key="food_text"):
            self.food_picker_field.content.controls[0].value = self.storage.get(
                key="food_text"
            )

        dogdog.update_item_list(
            list_column=self.food_list_column,
            search_data=[],
            select_key=None,
            select_value=lambda k, v: self.page.run_task(self.select_food, k, v),
            keyword="",
        )

        # Step 2: 용량 선택 드롭다운 (초기엔 숨김)
        self.product_weight_list = dogdog.dropdown_menu(
            label="사료의 용량을 선택해주세요.",
            event=self.food_product_weight_set,
            options=[],
        )

        if self.storage.get(key="product_id"):
            self.product_weight_list.visible = True
            # 기존에 선택된 무게 옵션을 보여주기 위해 product_id 세팅
            self.product_weight_list.value = str(self.storage.get(key="product_id"))
        else:
            self.product_weight_list.visible = False

    # ---------------------------------------------------------------------------------------------------
    # Food List Picker Event
    # ---------------------------------------------------------------------------------------------------
    def open_food_bottom_sheet(self, e):
        self.food_search_field.value = ""
        self.food_list_column.controls.clear()
        if self.food_bottom_sheet not in self.page.overlay:
            self.page.overlay.append(self.food_bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(self.food_bottom_sheet)
        self.food_bottom_sheet.open = True
        self.page.update()

    async def on_food_search_change(self, e):
        """Step 1: 검색어 기반 제품 이름 목록 조회 (디바운싱 적용)"""
        keyword = e.control.value
        import asyncio

        if self._search_task:
            self._search_task.cancel()

        async def search_with_debounce():
            try:
                await asyncio.sleep(0.5)

                if not keyword or len(keyword) < 1:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(
                        dogdog.basic_text(value="검색어를 입력해 주세요.", size=14)
                    )
                    self.page.update()
                    return

                self.food_list_column.controls.clear()
                self.food_list_column.controls.append(
                    dogdog.basic_text(value="검색 중...", size=14)
                )
                self.page.update()

                api_client = ApiClient(self.page)

                # 1. 상품명만 검색 (/api/v1/products/name)
                res_name = await api_client.get(
                    "/products/name", params={"keyword": keyword}
                )
                if res_name.status_code != 200:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(
                        dogdog.basic_text(
                            value="검색 결과를 가져올 수 없습니다.", size=14
                        )
                    )
                    self.page.update()
                    return

                products = res_name.json().get("data", [])
                if not products:
                    self.food_list_column.controls.clear()
                    self.food_list_column.controls.append(
                        dogdog.basic_text(value="검색 결과가 없습니다.", size=14)
                    )
                    self.page.update()
                    return

                # UI 데이터 매핑 (ID | 이름)
                search_list = [
                    [str(p.get("product_detail_id")), p.get("product_name")]
                    for p in products
                ]

                # UI 바인딩
                dogdog.update_item_list(
                    list_column=self.food_list_column,
                    search_data=search_list,
                    select_key=self.selected_product_detail_id,
                    select_value=lambda k, v: self.page.run_task(self.select_food, k, v),
                    keyword=keyword,
                )
                self.page.update()

            except asyncio.CancelledError:
                pass
            except Exception as err:
                print(f"[API Error] 사료 이름 검색 실패: {err}")
                self.food_list_column.controls.clear()
                self.food_list_column.controls.append(
                    dogdog.basic_text(value="서버 오류가 발생했습니다.", size=14)
                )
                self.page.update()

        self._search_task = asyncio.create_task(search_with_debounce())

    async def select_food(self, product_detail_id, product_name):
        """Step 2: 이름 선택 시 해당 제품의 무게(용량) 옵션 조회"""
        if not product_detail_id:
            return

        try:
            print(f"[DEBUG] 제품 선택됨: {product_name} (ID: {product_detail_id})")
            self.selected_product_detail_id = product_detail_id

            # 검색 바텀시트 닫기
            self.food_bottom_sheet.open = False
            self.page.update()

            # 무게 정보 조회 전 로딩 표시 (필요 시)
            self.food_picker_field.content.controls[
                0
            ].value = f"{product_name} (용량 확인 중...)"
            self.page.update()

            api_client = ApiClient(self.page)

            # 2. 해당 제품의 무게 옵션 조회 (/api/v1/products/weights)
            res_w = await api_client.get(
                "/products/weights", params={"product_detail_id": product_detail_id}
            )

            if res_w.status_code == 200:
                weights_data = res_w.json().get("data", [])

                if not weights_data:
                    self.food_picker_field.content.controls[
                        0
                    ].value = f"{product_name} (선택 가능한 용량 없음)"
                    self.product_weight_list.visible = False
                    self.page.update()
                    return

                # 드롭다운 옵션 구성 (product_id | weight)
                self.product_weight_list.options = [
                    dogdog.dropdown_menu_option(
                        key=str(w.get("product_id")), text=f"{w.get('weight')}g"
                    )
                    for w in weights_data
                    if w.get("active")
                ]

                # UI 업데이트: 제품명 표시 및 용량 드롭다운 활성화
                self.food_picker_field.content.controls[0].value = product_name
                self.storage.set(key="food_text", value=product_name)

                self.product_weight_list.visible = True
                self.product_weight_list.value = None  # 초기화
                self.page.update()

            else:
                print(f"[API Error] 무게 정보 조회 실패: {res_w.status_code}")
                self.food_picker_field.content.controls[
                    0
                ].value = f"{product_name} (정보 조회 실패)"
                self.page.update()

        except Exception as e:
            print(f"[UI Error] 사료 상세 조회 처리 실패: {e}")

    def food_product_weight_set(self, e):
        """최종 무게 선택 시 세션 저장"""
        selected_product_id = e.control.value
        if not selected_product_id:
            return

        self.storage.set(key="product_id", value=int(selected_product_id))

        # 선택된 옵션에서 무게 값 추출
        selected_option = next(
            (
                opt
                for opt in self.product_weight_list.options
                if opt.key == selected_product_id
            ),
            None,
        )
        if selected_option:
            try:
                weight_val = selected_option.text.replace("g", "")
                self.storage.set(key="product_weight", value=int(float(weight_val)))
                print(
                    f"[DEBUG] 최종 저장: ProductID={selected_product_id}, Weight={weight_val}g"
                )
            except (ValueError, TypeError):
                pass

        self.page.update()


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
            storage.set("food_weight", int(e.control.value))
        except ValueError:
            pass

    selected_food_weight = dogdog.input_textfield(
        hint_text="현재 급여 중인 사료의 잔여량을 적어주세요",
        input_type="int",
        suffix="g",
        on_change=on_food_weight_change,
    )
    if storage.get("food_weight"):
        selected_food_weight.value = storage.get("food_weight")  # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Pet Feeding Food Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="현재 급여 중인 사료", weight="bold"),
        pet_food_controller.food_picker_field,
        pet_food_controller.product_weight_list,  # Step 2 드롭다운
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight,
    ]
    return content_column
