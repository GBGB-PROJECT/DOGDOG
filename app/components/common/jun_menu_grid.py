import flet as ft
from components.common.jun_menu_box import menu_box
from components.common.jun_layout_tokens import (
    CONTENT_WIDTH,
    MENU_GRID_SIDE_PADDING,
    MENU_GRID_ROW_GAP,
    MENU_GRID_ITEM_GAP,
)


def menu_grid(
    page: ft.Page,
    content_width=CONTENT_WIDTH,
    top=6,
    bottom=8,
    on_feeding_click=None,
    on_water_click=None,
    on_activity_click=None,
    on_hygiene_click=None,
    on_health_click=None,
    on_note_click=None,
):
    menu_rows = [
        [
            menu_box(
                "dogbowl.png",
                "밥주기",
                on_feeding_click,
            ),
            menu_box(
                "waterdrop.png",
                "물주기",
                on_water_click,
            ),
            menu_box(
                "dogwalking.png",
                "활동기록",
                on_activity_click,
            ),
        ],
        [
            menu_box(
                "poop.png",
                "위생/배변",
                on_hygiene_click,
            ),
            menu_box(
                "injection.png",
                "건강기록",
                on_health_click,
            ),
            menu_box(
                "note.png",
                "상태기록",
                on_note_click,
            ),
        ],
    ]

    return ft.Container(  # 🔴◆ 이게 없으니 홈 화면이 죽고 회색으로 변함
        width=content_width,
        padding=ft.padding.only(
            left=MENU_GRID_SIDE_PADDING,
            right=MENU_GRID_SIDE_PADDING,
            top=top,
            bottom=bottom,
        ),
        content=ft.Column(
            spacing=MENU_GRID_ROW_GAP,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=MENU_GRID_ITEM_GAP,
                    controls=row_controls,  # 🔴◆ 이게 없으니 홈에서 메뉴 그리드가 사라짐
                )
                for row_controls in menu_rows  # 🔴◆ 이게 없으니 홈에서 메뉴 그리드가 사라짐
            ],
        ),
    )