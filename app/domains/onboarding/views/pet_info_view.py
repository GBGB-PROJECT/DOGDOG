# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import api.breed_data as Breed
import datetime
# -------------------------------------------------------------------------------------------------------
class PetInfoController:
    def __init__(self, page: ft.Page):
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        storage = page.session.store
        # -----------------------------------------------------------------------------------------------
        # Image View and Selected Picker
        # -----------------------------------------------------------------------------------------------
        self.image_container = dogdog.image_circle(event=self.pick_profile_image, size=200)
        self.image_container.visible = False
        self.image_picker_field = dogdog.picker_field(
            text="이미지를 등록해주세요.",
            on_click=self.pick_profile_image,
            icon=ft.Icons.UPLOAD_FILE,
        )
        if storage.get(key="image_path"):
            self.image_picker_field.content.controls[0].value = ( # type: ignore
                storage.get(key="image_name")
            )
            self.image_container.visible = True
            self.image_container.image.src = ( # type: ignore
                storage.get(key="image_path")
            )
        # -----------------------------------------------------------------------------------------------
        # Breed List Selected Picker and Bottom Sheet
        # -----------------------------------------------------------------------------------------------
        self.selected_breed_id = None
        self.breed_list_column = ft.Column(
            expand=True,
            spacing=6,
            scroll=ft.ScrollMode.AUTO,
        )
        self.breed_search_field = dogdog.list_input_textfield(
            hint_text="견종 검색", on_change=self.on_breed_search_change
        )
        # self.breed_search_field.autofocus = True
        self.breed_bottom_sheet = dogdog.bottom_sheet(
            content=[
                dogdog.basic_text(value="우리 아이의 견종은?", size=25, weight="bold"),
                ft.Divider(),
                self.breed_search_field,
                self.breed_list_column
            ]
        )
        if self.breed_bottom_sheet not in page.overlay:
            page.overlay.append(self.breed_bottom_sheet)
        self.breed_picker_field = dogdog.picker_field(
            text="반려동물 품종을 선택해주세요.",
            on_click=self.open_breed_bottom_sheet,
            icon=ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
        )
        if storage.get(key="breed_text"):
            self.breed_picker_field.content.controls[0].value = ( # type: ignore
                storage.get(key="breed_text")
            )
        self.breed_list = dogdog.update_item_list(
            list_column=self.breed_list_column, 
            search_data=Breed.BREED_LIST,
            select_key=self.selected_breed_id, 
            select_value=self.select_breed, 
            keyword=""
        )
        # -----------------------------------------------------------------------------------------------
        # Pet Birth Day Selected Picker and Dropdown Menu
        # -----------------------------------------------------------------------------------------------
        self.birth_input_mode = dogdog.radio_group(
            value=None,
            on_change=self.change_birth_mode,
            layout_type="column",
            contents=[
                ft.Radio(value="birthday", label="생년월일을 알아요"),
                ft.Radio(value="age", label="대략적인 나이만 알고 있어요")
        ])
        self.date_picker = ft.DatePicker(
            first_date=datetime.datetime(year=2000, month=1, day=1),
            last_date=datetime.datetime.now(),
            on_change=self.on_date_change,
        )
        if self.date_picker not in page.overlay:
            page.overlay.append(self.date_picker)
        self.birthday_picker_field = dogdog.picker_field(
            text="생년월일을 선택해주세요.",
            on_click=self.open_date_picker,
            icon=ft.Icons.CALENDAR_MONTH,
        )
        if storage.get(key="pet_birth_day"):
            self.birth_input_mode.value = "birthday"
            self.birthday_picker_field.visible = True
            self.birthday_picker_field.content.controls[0].value = ( # type: ignore
                storage.get(key="pet_birth_day"))
            self.page.update()
        else: self.birthday_picker_field.visible = False
        self.year_dropdown = dogdog.dropdown_menu(
            label="년 선택",
            event=self.age_year_event,
            options=[dogdog.dropdown_menu_option(text=f"{year} 년") for year in range(0, 31)],
        )
        self.month_dropdown = dogdog.dropdown_menu(
            label="개월 선택",
            event=self.age_month_event,
            options=[dogdog.dropdown_menu_option(text=f"{month} 개월") for month in range(0, 12)],
        )
        self.birthday_dropdown = ft.Row(
            height=48,
            controls=[
                self.year_dropdown,
                self.month_dropdown,
            ],
        )
        if storage.get(key="pet_age_year") and storage.get(key="pet_age_month"):
            self.birth_input_mode.value = "age"
            self.birthday_dropdown.visible = True
            self.year_dropdown.value = storage.get(key="pet_age_year")
            self.month_dropdown.value = storage.get(key="pet_age_month")
            self.page.update()
        else: self.birthday_dropdown.visible = False
    # ---------------------------------------------------------------------------------------------------
    # Image Selected Picker Event
    # ---------------------------------------------------------------------------------------------------
    async def pick_profile_image(self, e):
        storage = self.page.session.store
        file_picker = ft.FilePicker()
        files = await file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        if files:
            file = files[0]
            try:
                if file.path is None:
                    print("\n"
                        "☆ -------------------------------------------------------------------------- ☆\n"
                        "☆ ----- Pick Profile Image Path Error: 파일 경로를 가져올 수 없습니다. ----- ☆\n"
                        "☆ -------------------------------------------------------------------------- ☆"
                    )
                    self.image_picker_field.content.controls[0].value = ( # type: ignore
                        "파일 경로를 가져올 수 없습니다."
                    )
                    return
                storage.set(key="image_path", value=file.path)
                storage.set(key="image_name", value=file.name)
                self.image_picker_field.content.controls[0].value = file.name # type: ignore
                self.image_container.visible = True
                self.image_container.image.src = file.path # type: ignore
            except:
                pass
        else:
            if storage.get(key="image_path"):
                storage.remove(key="image_path")
                storage.remove(key="image_name")
            self.image_container.visible = False
            self.image_container.image = None
    # ---------------------------------------------------------------------------------------------------
    # Breed List Picker Event
    # ---------------------------------------------------------------------------------------------------
    def open_breed_bottom_sheet(self, e):
        self.breed_search_field.value = ""
        self.breed_list
        self.breed_bottom_sheet.open = True
        self.page.update() # Overlay Error 방지
    def on_breed_search_change(self, e):
        self.breed_list = dogdog.update_item_list(
            list_column=self.breed_list_column, 
            search_data=Breed.BREED_LIST,
            select_key=self.selected_breed_id, 
            select_value=self.select_breed, 
            keyword=e.control.value)
    def select_breed(self, breed_id, breed_name):
        storage = self.page.session.store
        self.selected_breed_id = breed_id
        storage.set(key="breed_id", value=breed_id)
        self.breed_picker_field.content.controls[0].value = breed_name # type: ignore
        storage.set(key="breed_text", value=breed_name)
        self.breed_bottom_sheet.open = False
        self.page.update() # Overlay Error 방지
    # ---------------------------------------------------------------------------------------------------
    # Birth Day Picker Event
    # ---------------------------------------------------------------------------------------------------
    def open_date_picker(self, e):
        self.date_picker.open = True
        self.page.update() # Overlay Error 방지
    def change_birth_mode(self, e):
        storage = self.page.session.store
        birth_input_mode = e.control.value
        storage.set(key="birth_input_mode", value=birth_input_mode)
        if birth_input_mode == "age":
            self.birthday_dropdown.visible = True
            self.birthday_picker_field.visible = False
            self.birthday_picker_field.content.controls[0].value = "생년월일을 선택해주세요." # type: ignore
            if storage.get(key="pet_birth_day"):
                storage.remove(key="pet_birth_day")
        else:
            self.birthday_dropdown.visible = False
            self.birthday_picker_field.visible = True
            self.year_dropdown.value = "년 선택"
            self.month_dropdown.value = "개월 선택"
            if storage.get(key="pet_age_year"):
                storage.remove(key="pet_age_year")
            if storage.get(key="pet_age_month"):
                storage.remove(key="pet_age_month")
        self.page.update() # Overlay Error 방지
    def on_date_change(self, e):
        storage = self.page.session.store
        if e.control.value:
            birth_day = (e.control.value + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
            storage.set(key="pet_birth_day", value=birth_day)
            self.birthday_picker_field.content.controls[0].value = birth_day # type: ignore
    def age_year_event(self, e): self.page.session.store.set(key="pet_age_year", value=e.control.value)
    def age_month_event(self, e): self.page.session.store.set(key="pet_age_month", value=e.control.value)
# -------------------------------------------------------------------------------------------------------


def pet_info_view(page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value Class
    # ---------------------------------------------------------------------------------------------------
    pet_info_controller = PetInfoController(page=page)
    storage = page.session.store
    # ---------------------------------------------------------------------------------------------------
    # Pet Name Input Field
    # ---------------------------------------------------------------------------------------------------
    def petname_on_change(e):
        storage.set("pet_name", e.control.value)
    pet_name_field = dogdog.input_textfield(hint_text="이름을 입력해주세요.", on_change=petname_on_change)
    if storage.get("pet_name"):
        pet_name_field.value = storage.get("pet_name")
    # --------------------------------------------------------------------------------------------------- 
    # Pet Gender Dropdown Menu
    # ---------------------------------------------------------------------------------------------------
    def gender_event(e):
        storage.set("pet_gender", e.control.value)
    pet_gender_dropdown = dogdog.dropdown_menu(
        label="성별 / 중성화",
        event=gender_event,
        options=[
            dogdog.dropdown_menu_option(text="수컷", icon=ft.Icons.MALE, icon_color=ft.Colors.BLUE),
            dogdog.dropdown_menu_option(text="수컷 (중성화)", icon=ft.Icons.CUT, icon_color=ft.Colors.BLUE),
            dogdog.dropdown_menu_option(text="암컷", icon=ft.Icons.FEMALE, icon_color=ft.Colors.PINK),
            dogdog.dropdown_menu_option(text="암컷 (중성화)", icon=ft.Icons.CUT, icon_color=ft.Colors.PINK),
    ])
    if storage.get("pet_gender"):
        pet_gender_dropdown.value = storage.get("pet_gender")
    # ---------------------------------------------------------------------------------------------------
    # Pet Weight Input Field
    # ---------------------------------------------------------------------------------------------------
    def weight_event(e):
        try: storage.set("pet_weight", e.control.value)
        except: pass
    pet_weight_field = dogdog.input_textfield(
        hint_text="무게를 입력해주세요.", suffix="Kg", input_type="int", on_change=weight_event,
        text_filter = ft.InputFilter(regex_string=r"^[0-9.]*$", replacement_string="")
    )
    if storage.get("pet_weight"):
        pet_weight_field.value = storage.get("pet_weight") # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Pet Info Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="이름", weight="bold"),
        pet_name_field,
        ft.Container(
            content=pet_info_controller.image_container, 
            alignment=ft.Alignment.CENTER
        ),
        dogdog.basic_text(value="프로필 이미지", weight="bold"),
        pet_info_controller.image_picker_field,
        ft.Container(height=8),
        dogdog.basic_text(value="품종", weight="bold"),
        pet_info_controller.breed_picker_field,
        ft.Container(height=8),
        dogdog.basic_text(value="생년월일", weight="bold"),
        pet_info_controller.birth_input_mode,
        pet_info_controller.birthday_picker_field,
        pet_info_controller.birthday_dropdown,
        ft.Container(height=8),
        dogdog.basic_text(value="성별", weight="bold"),
        pet_gender_dropdown,
        ft.Container(height=8),
        dogdog.basic_text(value="무게", weight="bold"),
        pet_weight_field,
        ft.Container(height=8),
    ]
    return content_column