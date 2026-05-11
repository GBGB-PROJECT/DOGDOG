import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_layout_tokens import WIDE_CONTENT_WIDTH, CARD_RADIUS
from components.common.jun_colors import (
    TEXT_PRIMARY,
    SURFACE_WHITE,
    BORDER_LIGHT,
    ACCENT_YELLOW,
)


def white_long_box3(
    text,
    time_text="오전 07:30",
    bgcolor=SURFACE_WHITE,
    text_color=TEXT_PRIMARY,
    time_color=TEXT_PRIMARY,
    on_click=None,
):
    return ft.Container(
        width=WIDE_CONTENT_WIDTH,
        height=70,
        bgcolor=bgcolor,
        border=ft.border.all(1, BORDER_LIGHT),
        border_radius=CARD_RADIUS,
        padding=ft.padding.symmetric(horizontal=16),
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                Txt(
                    text,
                    size=14,
                    weight=ft.FontWeight.W_500,
                    color=text_color,
                ),
                Txt(
                    time_text,
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=time_color,
                ),
            ],
        ),
    )


def mid_box(text, on_click=None):
    return ft.Container(
        width=72,
        height=40,
        alignment=ft.Alignment(0, 0),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        bgcolor=ACCENT_YELLOW,
        border_radius=10,
        on_click=on_click,
        content=Txt(
            text,
            size=13,
            weight=ft.FontWeight.W_600,
            color=TEXT_PRIMARY,
        ),
    )


def mid_box2(text, on_click=None):
    return ft.Container(
        width=72,
        height=40,
        alignment=ft.Alignment(0, 0),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        bgcolor=ft.Colors.GREY_100,
        border_radius=10,
        on_click=on_click,
        content=Txt(
            text,
            size=13,
            weight=ft.FontWeight.W_600,
            color=TEXT_PRIMARY,
        ),
    )