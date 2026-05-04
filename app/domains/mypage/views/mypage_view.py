import asyncio
import flet as ft

import components as dogdog
from components.common.jun_layout_tokens import (
    CONTENT_WIDTH,
    CARD_RADIUS,
    OUTER_PAGE_PADDING,
    LARGE_GAP,
    MEDIUM_GAP,
)
from components.common.jun_colors import (
    TEXT_PRIMARY,
    SURFACE_WHITE,
    BORDER_LIGHT,
)


MENU_ITEMS = [
    ("내 정보", ft.Icons.PERSON_OUTLINE),
    ("마이 쇼핑", ft.Icons.STOREFRONT_OUTLINED),
    ("공지사항", ft.Icons.NOTIFICATIONS_NONE),
    ("문의하기", ft.Icons.HELP_OUTLINE),
]


def white_long_box(
    text,
    left_icon=None,
    bgcolor=SURFACE_WHITE,
    text_color=TEXT_PRIMARY,
    on_click=None,
    show_left_icon=True,
    show_chevron=True,
    show_border=True, # 👉 추가: 테두리 표시 여부 제어
):
    left_controls = []

    if show_left_icon:
        left_controls.append(
            ft.Icon(left_icon, color=text_color, size=20)
        )

    left_controls.append(
        dogdog.Txt(
            text,
            size=14,
            weight=ft.FontWeight.W_500,
            color=text_color,
        )
    )

    return ft.Container(
        height=64,
        bgcolor=bgcolor,
        border=ft.border.all(1, BORDER_LIGHT) if show_border else None, # 👉 추가: 조건부 border
        border_radius=CARD_RADIUS,
        padding=ft.padding.symmetric(horizontal=16),
        on_click=on_click,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=left_controls,
                ),
                ft.Icon(
                    ft.Icons.CHEVRON_RIGHT,
                    color=text_color,
                    size=22,
                ) if show_chevron else ft.Container(width=22),
            ],
        ),
    )


def mypage_view(page: ft.Page, controller=None):
    selected_banner = {"index": None}
    banner_area = ft.Column(
        margin=ft.margin.only(top=10),
        spacing=MEDIUM_GAP,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    def change_selected_banner(index):
        selected_banner["index"] = index
        banner_area.controls = build_banners()
        page.update()

    def select_banner(index):
        def handler(e):
            change_selected_banner(index)
        return handler

    async def select_and_open_food_remain(e):
        change_selected_banner(1)
        await asyncio.sleep(0.3)
        # [수정] 컨트롤러가 있으면 컨트롤러의 메서드 호출, 없으면 직접 이동
        if controller:
            controller.go_to_feeding()
        else:
            page.go("/feeding")

    def build_banners():
        return [
            dogdog.banner(
                image_src="dogclay.png",
                text="내 반려동물 정보",
                selected=(selected_banner["index"] == 0),
                on_click=select_banner(0),
            ),
            dogdog.banner(
                text="급여 중인 상품 보러가기",
                selected=(selected_banner["index"] == 1),
                on_click=select_and_open_food_remain,
            ),
        ]

    def build_menu_controls():
        controls = []

        for text, icon in MENU_ITEMS:
            controls.append(
                white_long_box(
                    text,
                    left_icon=icon,
                    show_border=False,  # 👉 추가: 메뉴 전부 테두리 제거
                )
            )
            controls.append(ft.Container(height=6))

        return ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls
        )

    banner_area.controls = build_banners()

    return [
        banner_area,
        build_menu_controls(),
        white_long_box(
            "로그아웃",
            text_color=ft.Colors.GREY_300,
            show_left_icon=False,
            show_chevron=False,
            show_border=False, # 👉 추가: 로그아웃은 테두리 제거
        ),
    ]