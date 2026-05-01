import flet as ft
import components as dogdog

# -------------------------------------------------------------------------------------------------------
def pet_food_view(page: ft.Page, popup, controller):
    """
    [View] pet_food_view
    - 순수 Dumb Component: 외부에서 주입된 controller를 사용하여 사료 검색 및 용량 선택 로직을 위임합니다.
    """
    storage = page.session.store

    # ---------------------------------------------------------------------------------------------------
    # Food List Picker and Bottom Sheet
    # ---------------------------------------------------------------------------------------------------
    food_list_column = ft.Column(
        height=(page.height / 7) * 2,  # type: ignore
        spacing=6,
        scroll=ft.ScrollMode.AUTO,
    )
    
    def select_food_wrapper(product_detail_id, product_name):
        page.run_task(controller.select_food, product_detail_id, product_name, food_picker_field, product_weight_list)

    food_search_field = dogdog.list_input_textfield(
        hint_text="Search", 
        on_change=lambda e: page.run_task(controller.on_food_search_change, e, food_list_column, select_food_wrapper)
    )
    food_search_field.autofocus = True
    
    food_bottom_sheet_contents = popup.bottom_sheet_controls

    food_picker_field = dogdog.picker_field(
        text="현재 급여 중인 사료를 선택해주세요.",
        on_click=lambda e: _open_food_bottom_sheet(e),
        icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
    )

    def _open_food_bottom_sheet(e):
        food_bottom_sheet_contents.clear()
        food_bottom_sheet_contents.append(dogdog.basic_text(value="사료 검색", size=25, weight="bold"))
        food_bottom_sheet_contents.append(ft.Divider())
        food_bottom_sheet_contents.append(food_search_field)
        food_bottom_sheet_contents.append(food_list_column)
        controller.open_food_bottom_sheet(e, food_search_field, food_list_column, select_food_wrapper)

    if storage.get("food_text"):
        food_picker_field.content.controls[0].value = storage.get("food_text") # type: ignore

    dogdog.update_item_list(
        list_column=food_list_column,
        search_data=[],
        select_key=None,
        select_value=lambda k, v: select_food_wrapper(k, v),
        keyword="",
    )

    # ---------------------------------------------------------------------------------------------------
    # Food Weight Dropdown List
    # ---------------------------------------------------------------------------------------------------
    product_weight_list = dogdog.dropdown_menu(
        label="사료의 용량을 선택해주세요.",
        event=lambda e: controller.food_product_weight_set(e, product_weight_list),
        options=[],
    )

    if storage.get("product_id"):
        product_weight_list.visible = True
        product_weight_list.value = str(storage.get("product_id"))
    else:
        product_weight_list.visible = False

    # ---------------------------------------------------------------------------------------------------
    # Pet Food Weight Field
    # ---------------------------------------------------------------------------------------------------
    def on_food_weight_change(e):
        try:
            if e.control.value:
                controller.update_field("food_weight", int(e.control.value))
            else:
                controller.update_field("food_weight", None)
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
    # Pet Feeding Food Page Assembly
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="현재 급여 중인 사료", weight="bold"),
        food_picker_field,
        product_weight_list,
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight,
    ]
    return content_column
