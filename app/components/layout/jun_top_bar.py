import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_layout_tokens import CONTENT_WIDTH, TOP_BAR_HEIGHT
from components.common.jun_colors import (
    TOP_VANILLA,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_TERTIARY,
    SURFACE_WHITE,
)

DOG_NAME = "츄츄"
DOG_INFO_TEXT = "(4년 9개월,♀)"


def dog_name_list(dog_text):
    return ft.MenuItemButton(
        width=200,
        content=Txt(
            dog_text,
            size=15,
            color=TEXT_PRIMARY,
            weight=ft.FontWeight.W_500,
        ),
        style=ft.ButtonStyle(
            bgcolor={
                ft.ControlState.DEFAULT: SURFACE_WHITE,
                ft.ControlState.HOVERED: ft.Colors.GREY_100,
            },
            color={
                ft.ControlState.DEFAULT: TEXT_PRIMARY,
                ft.ControlState.HOVERED: TEXT_PRIMARY,
            },
            elevation=0,
            shadow_color=ft.Colors.TRANSPARENT,
            padding=ft.padding.symmetric(horizontal=12, vertical=14),
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
    )


def dog_menubar():
    dog_names = [DOG_NAME]

    return ft.Column(
        spacing=2,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        controls=[
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=50,
                        height=50,
                        border_radius=25,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src="dogclay.png",
                            width=50,
                            height=50,
                            fit=ft.BoxFit.COVER,
                        ),
                    ),
                    ft.MenuBar(
                        expand=True,
                        style=ft.MenuStyle(
                            alignment=ft.Alignment(-1, 0),
                            bgcolor=ft.Colors.TRANSPARENT,
                            elevation=0,
                            shadow_color=ft.Colors.TRANSPARENT,
                        ),
                        controls=[
                            ft.SubmenuButton(
                                width=220,
                                menu_style=ft.MenuStyle(
                                    bgcolor=SURFACE_WHITE,
                                    shadow_color=ft.Colors.with_opacity(
                                        0.10, ft.Colors.BLACK
                                    ),
                                    elevation=6,
                                ),
                                content=ft.Column(
                                    spacing=2,
                                    horizontal_alignment=ft.CrossAxisAlignment.START,
                                    controls=[
                                        ft.Row(
                                            spacing=2,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                Txt(
                                                    DOG_NAME,
                                                    size=16,
                                                    color=TEXT_TERTIARY,
                                                    weight=ft.FontWeight.W_600,
                                                ),
                                                ft.Icon(
                                                    ft.Icons.KEYBOARD_ARROW_DOWN,
                                                    size=25,
                                                    color=TEXT_TERTIARY,
                                                ),
                                            ],
                                        ),
                                        Txt(
                                            DOG_INFO_TEXT,
                                            size=11,
                                            color=TEXT_SECONDARY,
                                            weight=ft.FontWeight.W_500,
                                        ),
                                    ],
                                ),
                                controls=[
                                    dog_name_list(name)
                                    for name in dog_names
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def vanilla_roof(content):
    return ft.Container(
        width=float("inf"),  # 이게 없으면 지붕 흐트러짐
        height=TOP_BAR_HEIGHT,
        bgcolor=TOP_VANILLA,
        border_radius=ft.border_radius.only(
            bottom_left=34,
            bottom_right=34,
        ),
        padding=ft.padding.only(top=52, left=20, right=20, bottom=14),
        content=ft.Container(
            width=CONTENT_WIDTH,
            alignment=ft.Alignment(0, 0),
            content=content,
        ),
    )


def build_home_top_bar():
    return ft.Column(
        spacing=0,
        controls=[
            vanilla_roof(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(width=0, height=40),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment(-1, 0),
                            content=dog_menubar(),
                        ),
                        ft.Container(
                            width=40,
                            height=40,
                            alignment=ft.Alignment(1, 0),
                            content=ft.IconButton(
                                icon=ft.Icons.NOTIFICATIONS_NONE_ROUNDED,
                                icon_color=TEXT_TERTIARY,
                                icon_size=28,
                            ),
                        ),
                    ],
                )
            )
        ],
    )


def build_title_top_bar(title_text, on_back=None):
    return ft.Column(
        spacing=0,
        controls=[
            vanilla_roof(
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=40,
                            height=40,
                            alignment=ft.Alignment(-1, 0),
                            content=ft.IconButton(
                                icon=ft.Icons.ARROW_BACK_IOS_NEW,
                                icon_color=TEXT_TERTIARY,
                                icon_size=20,
                                style=ft.ButtonStyle(
                                    padding=0,
                                ),
                                on_click=on_back or (lambda e: e.page.open_back()),
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            alignment=ft.Alignment(0, 0),
                            content=Txt(
                                title_text,
                                size=18,
                                color=TEXT_TERTIARY,
                                weight=ft.FontWeight.W_600,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ),
                        ft.Container(
                            width=40,
                            height=40,
                        ),
                    ],
                )
            )
        ],
    )


def top_bar(title_text=None, on_back=None):
    if not title_text:
        return build_home_top_bar()

    return build_title_top_bar(title_text, on_back)