import flet as ft


SIDEBAR_BG = "#004C8C"
ACTIVE_COLOR = "#22C7E8"
TEXT_COLOR = ft.Colors.WHITE
DIVIDER_COLOR = "#2A679B"

MENU_ITEMS = [
    "홈",
    "매출관리",
    "원가관리",
    "구매관리",
    "상품관리",
    "생산관리",
    "재고관리",
    "물류관리",
    "고객관리",
    "영업관리",
    "회계관리",
    "인사관리",
    "시스템관리",
]


def _menu_item(text: str, selected_menu: str, on_menu_click):
    is_selected = text == selected_menu

    return ft.Container(
        padding=ft.padding.only(left=22, top=10, bottom=10, right=12),
        content=ft.Text(
            value=text,
            size=14,
            weight=ft.FontWeight.W_600,
            color=ACTIVE_COLOR if is_selected else TEXT_COLOR, # 🔥
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
        for item in MENU_ITEMS
    ]

    return ft.Container(
        width=220,
        bgcolor=SIDEBAR_BG,
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
                        color=TEXT_COLOR,
                    ),
                ),
                # ft.Divider(height=1, color=DIVIDER_COLOR),
                ft.Container(height=8),
                *menu_controls,
            ],
        ),
    )