# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def pet_activity_view(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    # ---------------------------------------------------------------------------------------------------
    # Feeding Time Selected Check Box
    # ---------------------------------------------------------------------------------------------------
    def breakfast_on_change(e):
        if e.control.value:
            storage.set(key="breakfast", value=e.control.value)
        else:
            storage.remove(key="breakfast")
    breakfast = ft.Checkbox(label="아침", on_change=breakfast_on_change)
    if storage.get(key="breakfast"):
        breakfast.value = storage.get(key="breakfast")
    def lunch_on_change(e):
        if e.control.value:
            storage.set(key="lunch", value=e.control.value)
        else:
            storage.remove(key="lunch")
    lunch = ft.Checkbox(label="점심", on_change=lunch_on_change)
    if storage.get(key="lunch"):
        lunch.value = storage.get(key="lunch")
    def dinner_on_change(e):
        if e.control.value:
            storage.set(key="dinner", value=e.control.value)
        else:
            storage.remove(key="dinner")
    dinner = ft.Checkbox(label="저녁", on_change=dinner_on_change)
    if storage.get(key="dinner"):
        dinner.value = storage.get(key="dinner")
    # ---------------------------------------------------------------------------------------------------
    # Daily Work Time Selected Radio
    # ---------------------------------------------------------------------------------------------------
    def radio_on_change(e):
        storage.set(key="radio_time", value=e.control.value)
    radio_time = dogdog.radio_group(
        value=None,
        on_change=radio_on_change,
        layout_type="column",
        spacing=12,
        contents=[
            ft.Radio(value="1", label="하루 30분 이하"),
            ft.Radio(value="2", label="하루 30분 이상"),
            ft.Radio(value="3", label="하루 1시간 이상"),
        ]
    )
    if storage.get(key="radio_time"):
        radio_time.value = storage.get(key="radio_time")
    # ---------------------------------------------------------------------------------------------------
    # Pet Activity Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="급여 시간", weight="bold"),
        breakfast,
        lunch,
        dinner,
        ft.Container(height=10),
        dogdog.basic_text(value="산책 시간", weight="bold"),
        radio_time,
    ]
    return content_column