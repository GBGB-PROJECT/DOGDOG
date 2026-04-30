# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog

# -------------------------------------------------------------------------------------------------------
def pet_activity_view(page: ft.Page, controller):
    """
    [View] pet_activity_view
    - 순수 Dumb Component: UI만 렌더링하고 상태 변경은 모두 controller에 위임합니다.
    """
    storage = page.session.store

    breakfast = ft.Checkbox(
        label="아침", 
        on_change=lambda e: controller.update_field("breakfast", e.control.value),
        value=storage.get("breakfast") or False
    )
    lunch = ft.Checkbox(
        label="점심", 
        on_change=lambda e: controller.update_field("lunch", e.control.value),
        value=storage.get("lunch") or False
    )
    dinner = ft.Checkbox(
        label="저녁", 
        on_change=lambda e: controller.update_field("dinner", e.control.value),
        value=storage.get("dinner") or False
    )

    radio_time = dogdog.radio_group(
        value=storage.get("radio_time"),
        on_change=lambda e: controller.update_field("radio_time", e.control.value),
        layout_type="column",
        spacing=12,
        contents=[
            ft.Radio(value="1", label="하루 30분 이하"),
            ft.Radio(value="2", label="하루 30분 이상"),
            ft.Radio(value="3", label="하루 1시간 이상"),
        ]
    )

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