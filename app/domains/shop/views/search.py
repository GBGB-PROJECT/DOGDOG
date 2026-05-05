import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[3]
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

import flet as ft
import components as dogdog
from domains.shop.controller.shop_controller import ShopController


def search_products(page: ft.Page):
    product_image_size = page.width / 3.8  # type: ignore

    product_list = ft.Container(
        padding=10,
        content=ft.Column(
            controls=[
                dogdog.basic_text(
                    "검색어를 입력해 주세요.",
                    size=15,
                    color=ft.Colors.GREY_500,
                )
            ]
        ),
    )

    product_state = {
        "items": {},
        "offset": 0,
        "limit": 12,
        "sort": None,
        "keyword": None,
        "is_loading": False,
        "has_more": False,
    }

    more_button = dogdog.continue_button(
        value="더보기",
        bgcolor=ft.Colors.WHITE,
        text_color=ft.Colors.GREY_800,
        on_click=lambda e: page.run_task(
            ShopController.load_products,
            page,
            product_list,
            product_image_size,
            product_state,
            more_button,
            product_state["sort"],
            False,
        ),
    )
    more_button.visible = False
    '''
        OpdProductDetail.product_name.ilike(keyword_pattern),
        OpdProductDetail.brand.ilike(keyword_pattern),
        OpdProductDetail.function.ilike(keyword_pattern),
        OpdProductDetail.type.ilike(keyword_pattern),
        OpdProductDetail.life.ilike(keyword_pattern),
        OpdProductDetail.main_protein.ilike(keyword_pattern),
        OpdProductDetail.protein_type.ilike(keyword_pattern),
        OpdProductDetail.preservative.ilike(keyword_pattern)
    '''
    hint_texts = [
        "Tip: 브랜드로 검색해보세요!",
        "Tip: 성분으로 검색해보세요!",
        "Tip: 상품명으로 검색해보세요!",
        "Tip: 기능 키워드로 검색해보세요!",
        "Tip: 타입으로 검색해보세요!",
        "Tip: 연령대로 검색해보세요!",
    ]

    import random

    search_field = ft.TextField(
        hint_text=random.choice(hint_texts),
        border=ft.InputBorder.NONE,
        filled=True,
        bgcolor="#F1F2F5",
        # border_radius=36,
        height=58,
        text_size=17,
        content_padding=ft.padding.only(left=22, right=8, top=8),
    )

    def run_search():
        keyword = (search_field.value or "").strip()

        if not keyword:
            product_state["items"] = {}
            product_state["offset"] = 0
            product_state["keyword"] = None
            product_state["has_more"] = False
            product_list.content = ft.Column(
                controls=[
                    dogdog.basic_text(
                        "검색어를 입력해 주세요.",
                        size=14,
                        color=ft.Colors.GREY_500,
                    )
                ]
            )
            more_button.visible = False
            product_list.update()
            more_button.update()
            return

        page.run_task(
            ShopController.load_products,
            page,
            product_list,
            product_image_size,
            product_state,
            more_button,
            None,
            True,
            keyword,
        )

    search_field.on_submit = lambda e: run_search()

    return ft.Container(
        bgcolor="#FFFFFF",
        padding=ft.padding.only(left=20, right=20, top=0),
        content=ft.Column(
            spacing=14,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    # spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=True,
                            height=56,
                            bgcolor="#F1F2F5",
                            border_radius=999,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=search_field,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SEARCH,
                            icon_size=26,
                            icon_color=ft.Colors.BLACK,
                            on_click=lambda e: run_search(),
                        ),
                    ],
                ),
                product_list,
                more_button,
            ],
        ),
    )

if __name__ == "__main__":
    import webbrowser, os

    if os.getenv(key="FLET_NO_BROWSER"):
        webbrowser.open = lambda *args: None
    ft.run(
        main=search_products,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        port=34636,
        web_renderer=ft.WebRenderer.CANVAS_KIT,
    )
