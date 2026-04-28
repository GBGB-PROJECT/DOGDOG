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
            # Load from api internally later, keeping empty initially
            self.product_weight_list.value = str(storage.get(key="product_id"))
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
        keyword = e.control.value
        api_client = ApiClient(self.page)
        
        try:
            # API를 통해 사료 검색 수행
            res = await api_client.get("/products", params={"keyword": keyword})
            if res.status_code == 200:
                res_data = res.json().get("data", [])
                # update_item_list 규격에 맞춰 [ID, 이름] 리스트로 변환
                search_list = [[item.get("product_detail_id"), item.get("product_name", "")] for item in res_data]
            else:
                search_list = []
        except Exception as err:
            print(f"사료 검색 중 오류: {err}")
            search_list = []

        self.food_list = dogdog.update_item_list(
            list_column=self.food_list_column,
            search_data=search_list,
            select_key=self.selected_food_id, 
            select_value=self.select_food, 
            keyword=keyword
        )
        self.page.update()
            
    async def select_food(self, food_id, food_name):
        if not food_id:
            return
            
        storage = self.page.session.store
        self.selected_food_id = food_id
        self.storage.set(key="food_id", value=food_id)
        self.food_picker_field.content.controls[0].value = food_name # type: ignore
        self.storage.set(key="food_text", value=food_name)
        self.food_bottom_sheet.open = False
        self.page.update() # Overlay Error 방지
        
        self.product_weight_list.visible = True
        
        # Load weights API
        api_client = ApiClient(self.page)
        self.product_weight_list.options.clear()
        
        try:
            print(f"선택된 상품 디테일 ID: {food_id}")
            res = await api_client.get("/products/weights", params={"product_detail_id": food_id})
            res_json = res.json()
            print(f"가져온 무게 데이터: {res_json}")
            
            if res.status_code == 200:
                weights = res_json.get("data", [])
                for w in weights:
                    pid = w.get("product_id")
                    wt = w.get("weight")
                    self.product_weight_list.options.append(
                        ft.dropdown.Option(key=str(pid), text=f"{wt}g")
                    )
            else:
                self.product_weight_list.options.append(
                    ft.dropdown.Option(key="", text="조회 범위 오류")
                )
        except Exception as e:
            print(f"사료 무게 로드 중 오류: {e}")
            self.product_weight_list.options.append(
                ft.dropdown.Option(key="", text="네트워크 오류")
            )
            
        self.product_weight_list.value = None # Reset previous selection
        self.product_weight_list.update() # **가장 중요: 드롭다운만 확실하게 업데이트**

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