# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime

# -------------------------------------------------------------------------------------------------------
def pet_info_view(page: ft.Page, popup, controller):
    """
    [View] pet_info_view
    - 순수 Dumb Component: 외부에서 주입된 controller를 사용하여 상태 관리를 위임합니다.
    """
    storage = page.session.store
    
    # ---------------------------------------------------------------------------------------------------
    # Pet Name Input Field
    # ---------------------------------------------------------------------------------------------------
    pet_name_field = dogdog.input_textfield(
        hint_text="이름을 입력해주세요.", 
        on_change=lambda e: controller.update_field("pet_name", e.control.value)
    )
    if storage.get("pet_name"):
        pet_name_field.value = storage.get("pet_name")
        
    # ---------------------------------------------------------------------------------------------------
    # Image View and Picker
    # ---------------------------------------------------------------------------------------------------
    image_container = dogdog.image_circle(event=lambda e: page.run_task(controller.pick_profile_image, e, image_picker_field, image_container), size=200)
    image_container.visible = False
    
    image_picker_field = dogdog.picker_field(
        text="이미지를 등록해주세요.",
        on_click=lambda e: page.run_task(controller.pick_profile_image, e, image_picker_field, image_container),
        icon=ft.Icons.UPLOAD_FILE,
    )
    
    if storage.get("image_path"):
        image_picker_field.content.controls[0].value = storage.get("image_name") # type: ignore
        image_container.visible = True
        image_container.image.src = storage.get("image_path") # type: ignore

    # ---------------------------------------------------------------------------------------------------
    # Breed List Picker and Bottom Sheet
    # ---------------------------------------------------------------------------------------------------
    breed_list_column = ft.Column(
        height=(page.height/7)*2, # type: ignore
        spacing=6,
        scroll=ft.ScrollMode.HIDDEN
    )
    
    def select_breed_wrapper(breed_id, breed_name):
        controller.select_breed(breed_id, breed_name, breed_picker_field)
        
    breed_search_field = dogdog.list_input_textfield(
        hint_text="견종 검색", 
        on_change=lambda e: controller.on_breed_search_change(e, breed_list_column, select_breed_wrapper)
    )
    breed_search_field.autofocus = True
    
    breed_bottom_sheet_contents = popup.bottom_sheet_controls
    breed_picker_field = dogdog.picker_field(
        text="반려동물 품종을 선택해주세요.",
        on_click=lambda e: _open_breed_bottom_sheet(e),
        icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
    )
    
    def _open_breed_bottom_sheet(e):
        breed_bottom_sheet_contents.clear()
        breed_bottom_sheet_contents.append(dogdog.basic_text(value="우리 아이의 견종은?", size=25, weight="bold"))
        breed_bottom_sheet_contents.append(ft.Divider())
        breed_bottom_sheet_contents.append(breed_search_field)
        breed_bottom_sheet_contents.append(breed_list_column)
        controller.open_breed_bottom_sheet(e, breed_search_field, breed_list_column, select_breed_wrapper)

    if storage.get("breed_text"):
        breed_picker_field.content.controls[0].value = storage.get("breed_text") # type: ignore

    # ---------------------------------------------------------------------------------------------------
    # Pet Birth Day Picker and Dropdown
    # ---------------------------------------------------------------------------------------------------
    year_dropdown = dogdog.dropdown_menu(
        label="년 선택",
        event=lambda e: controller.update_field("pet_age_year", e.control.value),
        options=[dogdog.dropdown_menu_option(text=f"{year} 년") for year in range(0, 31)],
    )
    
    month_dropdown = dogdog.dropdown_menu(
        label="개월 선택",
        event=lambda e: controller.update_field("pet_age_month", e.control.value),
        options=[dogdog.dropdown_menu_option(text=f"{month} 개월") for month in range(0, 12)],
    )
    
    birthday_dropdown = ft.Row(
        height=48,
        controls=[year_dropdown, month_dropdown],
    )
    
    birthday_picker_field = dogdog.picker_field(
        text="생년월일을 선택해주세요.",
        on_click=lambda e: _open_date_picker(e),
        icon=ft.Icons.CALENDAR_MONTH,
    )
    
    date_picker = ft.DatePicker(
        first_date=datetime.datetime(year=2000, month=1, day=1),
        last_date=datetime.datetime.now(),
        on_change=lambda e: controller.on_date_change(e, birthday_picker_field),
    )
    
    def _open_date_picker(e):
        if date_picker not in page.overlay:
            page.overlay.append(date_picker)
        date_picker.open = True
        page.update()

    birth_input_mode = dogdog.radio_group(
        value="birthday",
        on_change=lambda e: controller.change_birth_mode(e, birthday_picker_field, birthday_dropdown, year_dropdown, month_dropdown),
        layout_type="column",
        contents=[
            ft.Radio(value="birthday", label="생년월일을 알아요"),
            ft.Radio(value="age", label="대략적인 나이만 알고 있어요")
        ]
    )

    if storage.get("pet_birth_day"):
        birth_input_mode.value = "birthday"
        birthday_picker_field.visible = True
        birthday_dropdown.visible = False
        birthday_picker_field.content.controls[0].value = storage.get("pet_birth_day") # type: ignore
    elif storage.get("pet_age_year") and storage.get("pet_age_month"):
        birth_input_mode.value = "age"
        birthday_dropdown.visible = True
        birthday_picker_field.visible = False
        year_dropdown.value = storage.get("pet_age_year")
        month_dropdown.value = storage.get("pet_age_month")
    else:
        # 초기값 보완: 기본 선택인 'birthday' 모드에 맞춰 달력 창을 보이게 설정
        birth_input_mode.value = "birthday"
        birthday_picker_field.visible = True
        birthday_dropdown.visible = False

    # --------------------------------------------------------------------------------------------------- 
    # Pet Gender Dropdown Menu
    # ---------------------------------------------------------------------------------------------------
    pet_gender_dropdown = dogdog.dropdown_menu(
        label="성별 / 중성화",
        event=lambda e: controller.update_field("pet_gender", e.control.value),
        options=[
            dogdog.dropdown_menu_option(text="수컷", icon=ft.Icons.MALE, icon_color=ft.Colors.BLUE),
            dogdog.dropdown_menu_option(text="수컷 (중성화)", icon=ft.Icons.CUT, icon_color=ft.Colors.BLUE),
            dogdog.dropdown_menu_option(text="암컷", icon=ft.Icons.FEMALE, icon_color=ft.Colors.PINK),
            dogdog.dropdown_menu_option(text="암컷 (중성화)", icon=ft.Icons.CUT, icon_color=ft.Colors.PINK),
        ]
    )
    if storage.get("pet_gender"):
        pet_gender_dropdown.value = storage.get("pet_gender")

    # ---------------------------------------------------------------------------------------------------
    # Pet Weight Input Field
    # ---------------------------------------------------------------------------------------------------
    def weight_event(e):
        try: 
            if e.control.value:
                controller.update_field("pet_weight", float(e.control.value))
            else:
                controller.update_field("pet_weight", None)
        except: 
            pass
            
    pet_weight_field = dogdog.input_textfield(
        hint_text="무게를 입력해주세요.", suffix="Kg", input_type="float", on_change=weight_event
    )
    if storage.get("pet_weight"):
        pet_weight_field.value = storage.get("pet_weight") # type: ignore

    # ---------------------------------------------------------------------------------------------------
    # Pet Info Page Assembly
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="이름", weight="bold"),
        pet_name_field,
        ft.Container(
            content=image_container, 
            alignment=ft.Alignment.CENTER
        ),
        dogdog.basic_text(value="프로필 이미지", weight="bold"),
        image_picker_field,
        ft.Container(height=8),
        dogdog.basic_text(value="품종", weight="bold"),
        breed_picker_field,
        ft.Container(height=8),
        dogdog.basic_text(value="생년월일", weight="bold"),
        birth_input_mode,
        birthday_picker_field,
        birthday_dropdown,
        ft.Container(height=8),
        dogdog.basic_text(value="성별", weight="bold"),
        pet_gender_dropdown,
        ft.Container(height=8),
        dogdog.basic_text(value="무게", weight="bold"),
        pet_weight_field,
        ft.Container(height=8),
    ]
    return content_column