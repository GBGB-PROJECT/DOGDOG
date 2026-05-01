import flet as ft
import api.breed_data as Breed
import datetime

class PetInfoController:
    """
    [Controller] PetInfoController
    역할: 반려견 정보 입력 단계의 복잡한 UI 이벤트(이미지 선택, 견종 검색/선택, 생일 선택)와 상태 저장을 처리합니다.
    """
    def __init__(self, page: ft.Page, popup):
        self.page = page
        self.popup = popup
        self.storage = page.session.store
        self.selected_breed_id = None

    def update_field(self, key: str, value):
        if value is None or str(value).strip() == "":
            self.storage.remove(key)
        else:
            self.storage.set(key, value)

    async def pick_profile_image(self, e, image_picker_field, image_container):
        file_picker = ft.FilePicker()
        if file_picker not in self.page.overlay:
            self.page.overlay.append(file_picker)
            self.page.update()

        files = await file_picker.pick_files(
            allow_multiple=False,
            file_type=ft.FilePickerFileType.IMAGE,
        )
        if files:
            file = files[0]
            try:
                if file.path is None:
                    image_picker_field.content.controls[0].value = "파일 경로를 가져올 수 없습니다."
                    self.page.update()
                    return
                self.storage.set("image_path", file.path)
                self.storage.set("image_name", file.name)
                image_picker_field.content.controls[0].value = file.name
                image_container.visible = True
                image_container.image.src = file.path
            except:
                pass
        else:
            if self.storage.get("image_path"):
                self.storage.remove("image_path")
                self.storage.remove("image_name")
            image_container.visible = False
            image_container.image = None
        self.page.update()

    def open_breed_bottom_sheet(self, e, breed_search_field, breed_list_column, select_breed_callback):
        breed_search_field.value = ""
        import components as dogdog
        dogdog.update_item_list(
            list_column=breed_list_column, 
            search_data=Breed.BREED_LIST,
            select_key=self.selected_breed_id, 
            select_value=select_breed_callback, 
            keyword=""
        )
        bottom_sheet = self.popup.bottom_sheet_popup
        if bottom_sheet not in self.page.overlay:
            self.page.overlay.append(bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(bottom_sheet)
        bottom_sheet.open = True
        self.page.update()

    def on_breed_search_change(self, e, breed_list_column, select_breed_callback):
        import components as dogdog
        dogdog.update_item_list(
            list_column=breed_list_column, 
            search_data=Breed.BREED_LIST,
            select_key=self.selected_breed_id, 
            select_value=select_breed_callback, 
            keyword=e.control.value
        )
        self.page.update()

    def select_breed(self, breed_id, breed_name, breed_picker_field):
        self.selected_breed_id = breed_id
        self.storage.set("breed_id", breed_id)
        breed_picker_field.content.controls[0].value = breed_name
        self.storage.set("breed_text", breed_name)
        self.popup.bottom_sheet_popup.open = False
        self.page.update()

    def change_birth_mode(self, e, birthday_picker_field, birthday_dropdown, year_dropdown, month_dropdown):
        birth_input_mode = e.control.value
        self.storage.set("birth_input_mode", birth_input_mode)

        if birth_input_mode == "birthday":
            # '생년월일을 알아요' 선택 시: 달력 창 보이게, 나이 드롭다운 숨김
            birthday_picker_field.visible = True
            birthday_dropdown.visible = False
            
            # 기존 나이 데이터 초기화
            year_dropdown.value = "년 선택"
            month_dropdown.value = "개월 선택"
            if self.storage.get("pet_age_year"): self.storage.remove("pet_age_year")
            if self.storage.get("pet_age_month"): self.storage.remove("pet_age_month")
            
        elif birth_input_mode == "age":
            # '대략적인 나이만 알고 있어요' 선택 시: 달력 창 숨김, 나이 드롭다운 보임
            birthday_picker_field.visible = False
            birthday_dropdown.visible = True
            
            # 기존 생년월일 데이터 초기화
            birthday_picker_field.content.controls[0].value = "생년월일을 선택해주세요."
            if self.storage.get("pet_birth_day"): self.storage.remove("pet_birth_day")
        
        # 컴포넌트 개별 업데이트 및 페이지 갱신
        birthday_picker_field.update()
        birthday_dropdown.update()
        self.page.update()

    def on_date_change(self, e, birthday_picker_field):
        if e.control.value:
            birth_day = (e.control.value + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
            self.storage.set("pet_birth_day", birth_day)
            birthday_picker_field.content.controls[0].value = birth_day
            self.page.update()
