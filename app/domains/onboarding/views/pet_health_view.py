# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog

# -------------------------------------------------------------------------------------------------------
def pet_health_view(page: ft.Page, controller):
    """
    [View] pet_health_view
    - 순수 Dumb Component: 컨트롤러를 주입받아 상태 변경 이벤트를 전달합니다.
    """
    storage = page.session.store
    
    allergy = dogdog.input_textfield(
        hint_text="반려동물의 알레르기를 적어주세요", 
        max_length=None, # type: ignore
        on_change=lambda e: controller.update_field("allergy", e.control.value)
    )
    
    def on_allergy_radio_change(e):
        if e.control.value == "yes":
            allergy.visible = True
        else:
            allergy.visible = False
            controller.update_field("allergy", None)
        page.update()

    allergy_radio = dogdog.radio_group(
        value="yes" if storage.get("allergy") else "no",
        on_change=on_allergy_radio_change,
        contents=[
            ft.Radio(value="yes", label="있어요"),
            ft.Radio(value="no", label="없어요"),
        ]
    )
    
    if storage.get("allergy"):
        allergy.visible = True
        allergy.value = storage.get("allergy") # type: ignore
    else: 
        allergy.visible = False

    disease = dogdog.input_textfield(
        hint_text="반려동물의 질병을 적어주세요", 
        max_length=None, # type: ignore
        on_change=lambda e: controller.update_field("disease", e.control.value) 
    )
    
    def on_disease_radio_change(e):
        if e.control.value == "yes":
            disease.visible = True
        else:
            disease.visible = False
            controller.update_field("disease", None)
        page.update()

    disease_radio = dogdog.radio_group(
        value="yes" if storage.get("disease") else "no",
        on_change=on_disease_radio_change,
        contents=[
            ft.Radio(value="yes", label="있어요"),
            ft.Radio(value="no", label="없어요"),
        ]
    )
    
    if storage.get("disease"):
        disease.visible = True
        disease.value = storage.get("disease") # type: ignore
    else: 
        disease.visible = False

    content_column = [
        dogdog.basic_text(value="알레르기", weight="bold"),
        allergy_radio,
        allergy,
        ft.Container(height=10),
        dogdog.basic_text(value="질병", weight="bold"),
        disease_radio,
        disease
    ]
    return content_column