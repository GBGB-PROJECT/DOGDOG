# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import api.product_data as Product
import api.product_weight_data as ProductWeight
# -------------------------------------------------------------------------------------------------------
class PetfoodController:
    def __init__(self, page: ft.Page):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.storage = page.session.store
        # -----------------------------------------------------------------------------------------------
        # Food List Selected Picker and Bottom Sheet
        # -----------------------------------------------------------------------------------------------
        self.selected_food_id = None
        self.food_list_column = ft.Column(
            expand=True,
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self.food_search_field = dogdog.list_input_textfield(
            hint_text="Search", on_change=self.on_food_search_change
        )
        # self.food_search_field.autofocus = True
        self.food_bottom_sheet = dogdog.bottom_sheet(
            content=[
                dogdog.basic_text(value="사료 검색", size=25, weight="bold"),
                ft.Divider(),
                self.food_search_field,
                self.food_list_column
            ]
        )
        if self.food_bottom_sheet not in page.overlay:
            page.overlay.append(self.food_bottom_sheet)
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
            search_data=Product.PRODUCT_LIST,
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
            self.load_product_weight_list = dogdog.dropdown_list(
                dropdown_menu=self.product_weight_list, search_data=ProductWeight.PRODUCT_WEIGHT_LIST, key=self.storage.get("food_id")
            )
            self.product_weight_list.value = self.storage.get(key="product_id")
        else: self.product_weight_list.visible = False
    # ---------------------------------------------------------------------------------------------------
    # Food List Picker Event
    # ---------------------------------------------------------------------------------------------------
    def open_food_bottom_sheet(self, e):
        self.food_search_field.value = ""
        self.food_list
        self.food_bottom_sheet.open = True
        self.page.update() # Overlay Error 방지
    def on_food_search_change(self, e):
        self.food_list = dogdog.update_item_list(
            list_column=self.food_list_column,
            search_data=Product.PRODUCT_LIST,
            select_key=self.selected_food_id, 
            select_value=self.select_food, 
            keyword=e.control.value)
    def select_food(self, food_id, food_name):
        self.selected_food_id = food_id
        self.storage.set(key="food_id", value=food_id)
        self.food_picker_field.content.controls[0].value = food_name # type: ignore
        self.storage.set(key="food_text", value=food_name)
        self.food_bottom_sheet.open = False
        self.page.update() # Overlay Error 방지
        self.product_weight_list.visible = True
        self.load_product_weight_list = dogdog.dropdown_list(
            dropdown_menu=self.product_weight_list, search_data=ProductWeight.PRODUCT_WEIGHT_LIST, key=food_id
        )
    def food_product_weight_set(self, e):
        self.storage.set(key="product_id", value=e.control.value)
        try:
            weight = e.control.text.split("g")[0]
            self.storage.set(key="product_weight", value=int(weight))
        except ValueError:
            pass
# -------------------------------------------------------------------------------------------------------
def pet_food_view(page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value Class
    # ---------------------------------------------------------------------------------------------------
    pet_food_controller = PetfoodController(page=page)
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