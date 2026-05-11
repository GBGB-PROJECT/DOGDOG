import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_layout_tokens import CARD_RADIUS
from components.common.jun_colors import (
    TEXT_PRIMARY,
    SURFACE_WHITE,
)


MENU_BOX_WIDTH = 100
MENU_BOX_HEIGHT = 86
MENU_ICON_SIZE = 38
MENU_BOX_SHADOW_OPACITY = 0.08
MENU_BOX_SHADOW_BLUR = 15
MENU_BOX_SHADOW_OFFSET_Y = 4


def menu_box(image_src, title, on_click=None):
    return ft.Container(
        width=MENU_BOX_WIDTH,
        height=MENU_BOX_HEIGHT,
        bgcolor=SURFACE_WHITE,
        border_radius=CARD_RADIUS,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        shadow=ft.BoxShadow(
            blur_radius=MENU_BOX_SHADOW_BLUR,
            spread_radius=0,
            color=ft.Colors.with_opacity(MENU_BOX_SHADOW_OPACITY, ft.Colors.BLACK),
            offset=ft.Offset(0, MENU_BOX_SHADOW_OFFSET_Y),
        ),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=6,
            controls=[
                ft.Image(
                    src=image_src,
                    width=MENU_ICON_SIZE,
                    height=MENU_ICON_SIZE,
                    fit=ft.BoxFit.CONTAIN,
                ),
                Txt(
                    title,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_PRIMARY,
                ),
            ],
        ),
    )