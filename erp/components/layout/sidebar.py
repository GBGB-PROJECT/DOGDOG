from ..common import color as c
from ..common import home_content_move as hcm
import flet as ft

# ☑️ 추가: 확장 패널 색상
EXPANDED_PANEL_BG = "#E9EAF2"
EXPANDED_TEXT_COLOR = "#111111"
EXPANDED_ACTIVE_BG = "#004C8C"
EXPANDED_ACTIVE_TEXT = ft.Colors.WHITE

# ☑️ 추가: 폭 설정
BASE_SIDEBAR_WIDTH = 220

# ☑️ 추가: 재고관리 1차 메뉴
INVENTORY_MAIN_ITEMS = [
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
]

# ☑️ 추가: 상품 재고 관리 2차 메뉴
INVENTORY_PRODUCT_ITEMS = [
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]

# ☑️ 추가: 재고관리 관련 상태 전체 묶음
INVENTORY_ALL_ITEMS = [
    "재고관리",
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]

# ☑️ 추가: 상품관리 1차 메뉴
MERCHANDISE_MAIN_ITEMS = [
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# ☑️ 추가: 상품관리 전체 묶음
MERCHANDISE_ALL_ITEMS = [
    "상품관리",
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# ☑️ 추가: 생산관리 1차 메뉴
PRODUCTION_MAIN_ITEMS = [
    "생산실적",
    "생산입고",
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]

# ☑️ 추가: 생산관리 전체 묶음
PRODUCTION_ALL_ITEMS = [
    "생산관리",
    "생산실적",
    "생산입고",
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]


# ☑️ 수정: 기존 함수 확장
def _menu_item(
    text: str,
    selected_menu: str,
    on_menu_click,
    text_color: str = ft.Colors.WHITE,
    active_color: str = c.ACTIVE_COLOR,
    left_padding: int = 22,
    active_bgcolor: str | None = None,
    selected_weight: ft.FontWeight = ft.FontWeight.W_600,
    is_forced_selected: bool = False,
):
    is_selected = text == selected_menu or is_forced_selected

    return ft.Container(
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=active_bgcolor if is_selected else ft.Colors.TRANSPARENT,
        on_click=lambda e, menu=text: on_menu_click(menu), # 🔥
        content=ft.Container(
            padding=ft.padding.only(left=left_padding, top=10, bottom=10, right=12),
            content=ft.Text(
                value=text,
                size=14,
                weight=selected_weight if is_selected else ft.FontWeight.W_600,
                color=active_color if is_selected else text_color, # 🔥
            ),
        ),
    )


# ☑️ 추가: 기본 파란 로고 영역
def _sidebar_brand_header():
    return ft.Container(
        bgcolor=c.MAIN_COLOR,
        padding=ft.padding.only(top=18, bottom=18),
        content=ft.Container(
            padding=ft.padding.only(left=22),
            content=ft.Text(
                value="GAEBOBGAEBOB",
                size=22,
                weight=ft.FontWeight.BOLD,
                color=ft.Colors.WHITE,
            ),
        ),
    )


# ☑️ 추가: 확장 패널 헤더
def _section_header(title: str, on_menu_click):
    return ft.Container(
        padding=ft.padding.only(left=12, right=12, bottom=18),
        content=ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                    icon_color=EXPANDED_TEXT_COLOR,
                    icon_size=18,
                    style=ft.ButtonStyle(
                        padding=0,
                        overlay_color=ft.Colors.TRANSPARENT,
                    ),
                    on_click=lambda e: on_menu_click("홈"),
                ),
                ft.Text(
                    value=title,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color=EXPANDED_TEXT_COLOR,
                ),
            ],
        ),
    )


# ☑️ 추가: 확장형 공통 렌더
def _build_expanded_sidebar(header_control, menu_controls):
    return ft.Container(
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=c.MAIN_COLOR,
        content=ft.Column(
            spacing=0,
            controls=[
                _sidebar_brand_header(),
                ft.Container(
                    expand=True,
                    bgcolor=EXPANDED_PANEL_BG,
                    padding=ft.padding.only(top=18, bottom=20),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            header_control,
                            ft.Container(height=8),
                            *menu_controls,
                        ],
                    ),
                ),
            ],
        ),
    )


# ☑️ 추가: 확장 메뉴 공통 생성
def _build_expanded_menu_controls(items, selected_menu, on_menu_click):
    return [
        _menu_item(
            text=item,
            selected_menu=selected_menu,
            on_menu_click=on_menu_click,
            text_color=EXPANDED_TEXT_COLOR,
            active_color=EXPANDED_ACTIVE_TEXT,
            active_bgcolor=EXPANDED_ACTIVE_BG,
        )
        for item in items
    ]


def build_erp_sidebar(selected_menu: str, on_menu_click):
    # ☑️ 추가: 재고관리 확장형
    if selected_menu in INVENTORY_ALL_ITEMS:
        is_product_open = selected_menu in ["상품 재고 관리"] + INVENTORY_PRODUCT_ITEMS

        inventory_controls = [
            _menu_item(
                text="창고관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=EXPANDED_TEXT_COLOR,
                active_color=EXPANDED_ACTIVE_TEXT,
                active_bgcolor=EXPANDED_ACTIVE_BG,
            ),
            _menu_item(
                text="원자재 재고 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=EXPANDED_TEXT_COLOR,
                active_color=EXPANDED_ACTIVE_TEXT,
                active_bgcolor=EXPANDED_ACTIVE_BG,
            ),
            _menu_item(
                text="상품 재고 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=EXPANDED_TEXT_COLOR,
                active_color=EXPANDED_ACTIVE_TEXT,
                active_bgcolor=EXPANDED_ACTIVE_BG,
                is_forced_selected=selected_menu in INVENTORY_PRODUCT_ITEMS,
            ),
        ]

        if is_product_open:
            inventory_controls.extend(
                [
                    _menu_item(
                        text=item,
                        selected_menu=selected_menu,
                        on_menu_click=on_menu_click,
                        text_color=EXPANDED_TEXT_COLOR,
                        active_color=EXPANDED_ACTIVE_BG,
                        active_bgcolor=None,
                        selected_weight=ft.FontWeight.BOLD,
                        left_padding=40,
                    )
                    for item in INVENTORY_PRODUCT_ITEMS
                ]
            )

        inventory_controls.append(
            _menu_item(
                text="상품 부자재 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=EXPANDED_TEXT_COLOR,
                active_color=EXPANDED_ACTIVE_TEXT,
                active_bgcolor=EXPANDED_ACTIVE_BG,
            )
        )

        return _build_expanded_sidebar(
            header_control=_section_header("재고관리", on_menu_click),
            menu_controls=inventory_controls,
        )

    # ☑️ 추가: 상품관리 확장형
    if selected_menu in MERCHANDISE_ALL_ITEMS:
        merchandise_controls = _build_expanded_menu_controls(
            MERCHANDISE_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
        )

        return _build_expanded_sidebar(
            header_control=_section_header("상품관리", on_menu_click),
            menu_controls=merchandise_controls,
        )

    # ☑️ 추가: 생산관리 확장형
    if selected_menu in PRODUCTION_ALL_ITEMS:
        production_controls = _build_expanded_menu_controls(
            PRODUCTION_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
        )

        return _build_expanded_sidebar(
            header_control=_section_header("생산관리", on_menu_click),
            menu_controls=production_controls,
        )

    menu_controls = [
        _menu_item(
            text=item,
            selected_menu=selected_menu, 
            on_menu_click=on_menu_click,
        )
        for item in hcm.MENU_ITEMS
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
                ft.Container(height=8),
                *menu_controls,
            ],
        ),
    )