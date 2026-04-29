# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def pet_health_view(page: ft.Page):
    storage = page.session.store
    # ---------------------------------------------------------------------------------------------------
    # Pet Allergy Input Field and Radio
    # ---------------------------------------------------------------------------------------------------
    def on_allergy_change(e):
        try:
            storage.set(key="allergy", value=e.control.value)
        except:
            pass
    allergy = dogdog.input_textfield(
        hint_text="반려동물의 알레르기를 적어주세요", max_length=None, # type: ignore
        on_change=on_allergy_change
    )
    def on_allergy_radio_change(e):
        if e.control.value == "yes":
            allergy.visible = True
        else:
            allergy.visible = False
            if storage.get(key="allergy"):
                storage.remove(key="allergy")
    allergy_radio = dogdog.radio_group(
        value="no",
        on_change=on_allergy_radio_change,
        contents=[
            ft.Radio(value="yes", label="있어요"),
            ft.Radio(value="no", label="없어요"),
        ]
    )
    if storage.get(key="allergy"):
        allergy.visible = True
        allergy_radio.value = "yes"
        allergy.value = storage.get(key="allergy") # type: ignore
    else: allergy.visible = False
    # ---------------------------------------------------------------------------------------------------
    # Pet Disease Input Field and Radio
    # ---------------------------------------------------------------------------------------------------
    def on_disease_change(e):
        try:
            storage.set(key="disease", value=e.control.value)
        except:
            pass
    disease = dogdog.input_textfield(
        hint_text="반려동물의 질병을 적어주세요", max_length=None, on_change=on_disease_change # type: ignore
    )
    def on_disease_radio_change(e):
        if e.control.value == "yes":
            disease.visible = True
        else:
            disease.visible = False
            if storage.get(key="disease"):
                storage.remove(key="disease")
    disease_radio = dogdog.radio_group(
        value="no",
        on_change=on_disease_radio_change,
        contents=[
            ft.Radio(value="yes", label="있어요"),
            ft.Radio(value="no", label="없어요"),
        ]
    )
    if storage.get(key="disease"):
        disease.visible = True
        disease_radio.value = "yes"
        disease.value = storage.get(key="disease") # type: ignore
    else: disease.visible = False
    # ---------------------------------------------------------------------------------------------------
    # Pet Health Page
    # ---------------------------------------------------------------------------------------------------
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