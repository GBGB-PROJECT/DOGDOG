import flet as ft
from components.common.jun_ui_boxes import mid_box, mid_box2
from components.common.jun_layout_tokens import ACTION_BAR_WIDTH
from components.common.jun_colors import SURFACE_WHITE


# ✅ 공통 하단 액션 버튼
def three_action_buttons(
    bottom_margin=30,
    vertical_padding=8,
    left_text="수정",
    middle_text="삭제",
    right_text="저장",
    on_left_click=None,
    on_middle_click=None,
    on_right_click=None,
):
    return ft.Container(
        width=ACTION_BAR_WIDTH,
        margin=ft.Margin.only(bottom=bottom_margin),
        padding=ft.padding.only(top=vertical_padding, bottom=vertical_padding),
        bgcolor=SURFACE_WHITE,
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            controls=[
                mid_box(left_text, on_click=on_left_click),
                mid_box(middle_text, on_click=on_middle_click),
                mid_box2(right_text, on_click=on_right_click),
            ],
        ),
    )