from ..common import color as c
from ..common import home_content_move as hcm
import flet as ft

def _menu_item(text: str, selected_menu: str, on_menu_click):
    is_selected = text == selected_menu

    return ft.Container(
        padding=ft.padding.only(left=22, top=10, bottom=10, right=12),
        content=ft.Text(
            value=text,
            size=14,
            weight=ft.FontWeight.W_600,
            color=c.ACTIVE_COLOR if is_selected else ft.Colors.WHITE, # 🔥
        ),
        on_click=lambda e, menu=text: on_menu_click(menu), # 🔥
    )


def build_erp_sidebar(selected_menu: str, on_menu_click):
    menu_controls = [
        _menu_item(
            text=item,
            selected_menu=selected_menu, 
            on_menu_click=on_menu_click,
        )
        for item in hcm.MENU_ITEMS[0]
    ]

    return ft.Container(
        width=220,
        bgcolor=c.MAIN_COLOR,
        padding=ft.padding.only(top=18, bottom=20),
        content=ft.Column(
            spacing=4,
            controls=[
                ft.Container(
                    padding=ft.padding.only(left=22, bottom=18),
                    content=ft.Text(
                        value="GAEBOBGAEBOB",
                        size=22,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                ),
                # ft.Divider(height=1, color=DIVIDER_COLOR),
                ft.Container(height=8),
                *menu_controls,
            ],
        ),
    )