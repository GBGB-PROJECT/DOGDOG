import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_colors import (
    TEXT_PRIMARY,
    SURFACE_WHITE,
    BORDER_LIGHT,
)


def nav_item_rules(icon, label, selected=False, on_click=None):
    return ft.Container(
        expand=True,
        height=74,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=3,
            controls=[
                ft.Icon(
                    icon,
                    color=TEXT_PRIMARY if selected else ft.Colors.GREY_400,
                    size=22,
                ),
                Txt(
                    label,
                    color=TEXT_PRIMARY if selected else ft.Colors.GREY_400,
                    size=10,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    no_wrap=True,
                ),
            ],
        ),
    )


def bottom_nav_items(selected_index, on_tab_change):
    tabs = [
        (ft.Icons.HOME, "Home"),
        (ft.Icons.CALENDAR_MONTH, "Log"),
        (None, None),  # 👉 FAB 자리
        (ft.Icons.MESSENGER_OUTLINE_ROUNDED, "Contents"),
        (ft.Icons.PERSON_OUTLINE, "MyPage"),
    ]

    controls = []

    for i, (icon, label) in enumerate(tabs):
        # 👉 가운데 FAB 자리
        if icon is None:
            controls.append(ft.Container(width=72))
            continue

        # 👉 실제 탭 index 계산
        tab_index = i if i < 2 else i - 1

        controls.append(
            nav_item_rules(
                icon,
                label,
                selected=(selected_index == tab_index),
                on_click=lambda e, idx=tab_index: on_tab_change(idx)
                if on_tab_change
                else None,
            )
        )

    return controls # 👉 이거 없으면 나브 아이템 전멸 


def custom_bottom_navbar(selected_index=0, on_tab_change=None):
    return ft.BottomAppBar(
        bgcolor=SURFACE_WHITE,
        elevation=0,
        padding=0,
        content=ft.Container(
            bgcolor=SURFACE_WHITE,
            height=82,
            padding=ft.padding.only(left=10, right=10, top=0, bottom=2),
            content=ft.Column(
                spacing=0,
                controls=[
                    # 상단 회색 선 전체 표시
                    ft.Container(
                        height=1,
                        bgcolor=BORDER_LIGHT,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=bottom_nav_items(selected_index, on_tab_change),
                        ),
                    ),
                ],
            ),
        ),
    )