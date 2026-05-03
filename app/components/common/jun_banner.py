import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_colors import (
    TOP_VANILLA,
    TEXT_PRIMARY,
    SURFACE_WHITE,
    BORDER_LIGHT,
)
from components.common.jun_layout_tokens import CONTENT_WIDTH, CARD_RADIUS


def banner(
    text="",
    image_src=None,
    selected=False,
    on_click=None,
):
    box_bgcolor = TOP_VANILLA if selected else SURFACE_WHITE
    arrow_bgcolor = SURFACE_WHITE if selected else TOP_VANILLA

    arrow_circle = ft.Container(
        width=40,
        height=40,
        bgcolor=arrow_bgcolor,
        border_radius=20,
        alignment=ft.Alignment(0, 0),
        content=ft.Icon(
            ft.Icons.ARROW_FORWARD,
            color=TEXT_PRIMARY,
            size=22,
        ),
    )

    left_slot = ft.Container(
        width=50,
        height=50,
        alignment=ft.Alignment(0, 0),
        content=(
            ft.Container(
                width=50,
                height=50,
                border_radius=25,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Image(
                    src=image_src,
                    width=50,
                    height=50,
                    fit=ft.BoxFit.COVER,
                ),
            )
            if image_src
            else None
        ),
    )
    left_slot.visible = False if image_src else True

    center_slot = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=Txt(
            text,
            size=16,
            weight=ft.FontWeight.W_600,
            color=TEXT_PRIMARY,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        ),
    )

    right_slot = ft.Container(
        width=50,
        height=50,
        alignment=ft.Alignment(0, 0),
        content=arrow_circle,
    )

    return ft.Container(
        # width=CONTENT_WIDTH,
        height=72,
        bgcolor=box_bgcolor,
        border=ft.border.all(1, BORDER_LIGHT),
        border_radius=CARD_RADIUS,
        padding=ft.padding.symmetric(horizontal=14),
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                left_slot,
                center_slot,
                right_slot,
            ],
        ),
    )