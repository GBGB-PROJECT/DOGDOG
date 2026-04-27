# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import domains.onboarding.views.pet_food_view as pet_food_view


# -------------------------------------------------------------------------------------------------------
def feeding_add_edit(page: ft.Page, view):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    popup = dogdog.Popup(page=page)
    storage = page.session.store
    if storage.get("food_text"):
        storage.remove("food_text")
    if storage.get("product_id"):
        storage.remove("product_id")
    if storage.get("food_id"):
        storage.remove("food_id")
    feeding_data: dict = (
        storage.get("select_feeding_data") if storage.get("select_feeding_data") else {}
    )  # type: ignore

    # ---------------------------------------------------------------------------------------------------
    # Test Dialog
    # ---------------------------------------------------------------------------------------------------
    def show_error(text:str): page.show_dialog(
        ft.SnackBar(content=ft.Text(value=text), open=True, behavior=ft.SnackBarBehavior.FLOATING))
    # ---------------------------------------------------------------------------------------------------
    # Test Dialog
    # ---------------------------------------------------------------------------------------------------        
    delete_popup = popup.event_popup
    delete_popup.title = dogdog.basic_text("제품 삭제")
    delete_popup.content = dogdog.basic_text("등록하신 제품을 삭제하시겠습니까?")
    delete_popup.actions = [
        ft.TextButton("네", on_click=lambda e: delete_popup_close(e, options=True)),
        ft.TextButton("아니요", on_click=lambda e: delete_popup_close(e))
    ]
    def delete_popup_close(e, options=None):
        delete_popup.open = False
        if options: print(e)
        page.update()
    # ---------------------------------------------------------------------------------------------------
    # Input Field Change Event
    # ---------------------------------------------------------------------------------------------------
    def on_change(e):
        try:
            storage.set("food_weight", int(e.control.value))
        except ValueError:
            pass

    # ---------------------------------------------------------------------------------------------------
    # Button Push Event
    # ---------------------------------------------------------------------------------------------------
    def button_event(e, call):
        if storage.get(f"customer_feeding_{call}_data"):
            storage.remove(f"customer_feeding_{call}_data")
        data = {}

        # -----------------------------------------------------------------------------------------------
        def delete_event(e):
            data.update(
                {"customer_feeding_food_id": storage.get("select_customer_food_id")}
            )
            page.go("/feeding")
            popup.show_popup_close(e)
            storage.set(f"customer_feeding_{call}_data", data)
            show_error(
                f"customer_feeding_{call}_data: {storage.get(f'customer_feeding_{call}_data')}"
            )

        # -----------------------------------------------------------------------------------------------
        if call == "delete":
            if delete_popup not in page.overlay:
                page.overlay.append(delete_popup)
            else:
                page.overlay.clear()
                page.overlay.append(delete_popup)
            delete_popup.open = True
        else:
            if storage.get("product_id"):
                data.update({"product_id": storage.get("product_id")})
            else:
                show_error("상품을 선택해주세요.")
                return
            if storage.get("food_weight"):
                data.update({"product_left_intake": storage.get("food_weight")})
            else:
                show_error("사료의 잔여량을 입력해주세요.")
                return
            if not call == "add_save":
                data.update(
                    {"customer_feeding_food_id": storage.get("select_customer_food_id")}
                )
            storage.set(f"customer_feeding_{call}_data", data)
            show_error(
                f"customer_feeding_{call}_data: {storage.get(f'customer_feeding_{call}_data')}"
            )
            page.go("/feeding")
        page.update()

    # ---------------------------------------------------------------------------------------------------
    # View Page
    # ---------------------------------------------------------------------------------------------------
    if view == "edit":
        if not (
            storage.get("select_customer_food_id" or storage.get("select_feeding_data"))
        ):
            page.go("/feeding")
            show_error("정상적이지 않은 접근입니다.")
            return ft.Container(
                padding=ft.Padding.only(left=20, right=20, top=20), bgcolor="#ffffff"
            )
        storage.set(
            key="food_text",
            value=f"{feeding_data['brand']} {feeding_data['product_name']}",
        )
        storage.set(key="product_id", value=feeding_data["product_id"])
        storage.set(key="food_id", value=feeding_data["product_detail_id"])
        feeding_start_date = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            controls=[
                ft.Icon(
                    icon=ft.Icons.CALENDAR_MONTH, color=ft.Colors.GREY_600, size=16
                ),
                dogdog.basic_text(
                    value=f"급여 시작일 : {feeding_data['feeding_start']}",
                    color=ft.Colors.GREY_600,
                ),
            ],
        )
    # ---------------------------------------------------------------------------------------------------
    food_controller = pet_food_view.PetfoodController(page=page, popup=popup)
    food_select_field = food_controller.food_picker_field.content.controls[0] # type: ignore
    product_weight_field = food_controller.product_weight_list
    # ---------------------------------------------------------------------------------------------------
    # View Page
    # ---------------------------------------------------------------------------------------------------
    if view == "edit":
        column_text = "현재 급여 중인 사료"
        feeding_setting_content = [
            dogdog.flat_button(
                text="삭제",
                scale=1,
                disabled=False,
                on_click=lambda e, content="delete": button_event(e, content),
            ),
            dogdog.flat_button(
                bgcolor="#FEF3B9",  # type: ignore
                text="수정",
                scale=1,
                disabled=False,
                on_click=lambda e, content="edit": button_event(e, content),
            ),
            dogdog.flat_button(
                bgcolor="#FEF3B9",  # type: ignore
                text="저장",
                scale=1,
                disabled=False,
                on_click=lambda e, content="save": button_event(e, content),
            ),
        ]
        food_select_field.color = ft.Colors.BLACK
    # ---------------------------------------------------------------------------------------------------
    elif view == "add":
        column_text = "신규 등록 사료"
        feeding_setting_content = [
            dogdog.flat_button(
                bgcolor="#FEF3B9",  # type: ignore
                text="저장",
                scale=1,
                disabled=False,
                on_click=lambda e, content="add_save": button_event(e, content),
            )
        ]
        food_select_field.value = "사료를 선택해주세요."
    selected_food_weight = dogdog.input_textfield(
        hint_text="사료의 잔여량을 적어주세요",
        input_type="int",
        suffix="g",
        on_change=on_change,
    )
    feeding_setting = ft.Row(
        margin=ft.margin.only(top=10),
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=feeding_setting_content,
    )  # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Feeding Edit Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value=column_text, weight="bold"),
        food_controller.food_picker_field,
        food_controller.product_weight_list,
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight,
    ]
    if view == "edit":
        content_column.append(feeding_start_date)
    content_column.append(feeding_setting)
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column  # type: ignore
        ),
    )
