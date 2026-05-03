from components import common as com
import flet as ft

# ☑️ 추가: 폭 설정
BASE_SIDEBAR_WIDTH = 220

# 🔥 수정: topbar.py의 height=68과 정확히 동일하게 맞춤
SIDEBAR_HEADER_HEIGHT = 68


# ☑️ 수정: 기존 함수 확장
def _menu_item(
    text: str,
    selected_menu: str,
    on_menu_click,
    text_color: str = ft.Colors.WHITE,
    active_color: str = com.ACTIVE_COLOR,
    left_padding: int = 22,
    active_bgcolor: str | None = None,
    selected_weight: ft.FontWeight = ft.FontWeight.W_600,
    is_forced_selected: bool = False,
    is_disabled: bool = False,
):
    is_selected = text == selected_menu or is_forced_selected

    # 🔥 수정: 비활성 메뉴도 글자색은 그대로 두고 클릭만 막는다.
    final_text_color = active_color if is_selected else text_color

    return ft.Container(
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=active_bgcolor if is_selected else ft.Colors.TRANSPARENT,
        # 🔥 수정: Flet 0.81.0 Container에는 mouse_cursor 인자가 없어서 제거
        # - 비활성 메뉴는 on_click 자체를 None으로 빼서 클릭 자체를 막는다.
        on_click=None if is_disabled else lambda e, menu=text: on_menu_click(menu),
        content=ft.Container(
            padding=ft.padding.only(left=left_padding, top=10, bottom=10, right=12),
            content=ft.Text(
                value=text,
                size=14,
                weight=selected_weight if is_selected else ft.FontWeight.W_600,
                color=final_text_color,
            ),
        ),
    )


# 🔥 수정: 파란 로고 영역 높이를 오른쪽 topbar 높이와 동일하게 맞춤
def _sidebar_brand_header(page: ft.Page):
    return ft.Container(
        height=SIDEBAR_HEADER_HEIGHT,
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=com.MAIN_COLOR,
        padding=ft.padding.only(left=22),
        alignment=ft.Alignment(-1, 0),
        on_click=lambda _: page.go("/home"),
        content=ft.Text(
            value="GAEBOBGAEBOB",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
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
                    icon_color=com.EXPANDED_TEXT_COLOR,
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
                    color=com.EXPANDED_TEXT_COLOR,
                ),
            ],
        ),
    )


# 🔥 수정: 확장형 공통 렌더 - 오른쪽 흰 화면 시작선과 회색 패널 시작선 일치
def _build_expanded_sidebar(page: ft.Page, header_control, menu_controls):
    return ft.Container(
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=com.MAIN_COLOR,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[
                _sidebar_brand_header(page),

                # 🔥 수정: topbar 높이 68px 이후부터 회색 패널 시작
                ft.Container(
                    expand=True,
                    width=BASE_SIDEBAR_WIDTH,
                    bgcolor=com.EXPANDED_PANEL_BG,
                    padding=ft.padding.only(top=22, bottom=20),
                    content=ft.Column(
                        spacing=4,
                        expand=True,
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
def _build_expanded_menu_controls(items, selected_menu, on_menu_click, disabled_items=None):
    disabled_items = disabled_items or []

    return [
        _menu_item(
            text=item,
            selected_menu=selected_menu,
            on_menu_click=on_menu_click,
            text_color=com.EXPANDED_TEXT_COLOR,
            active_color=com.PAGE_BG,
            active_bgcolor=com.EXPANDED_ACTIVE_BG,
            # 🔥 추가: 화면 없는 하위 메뉴는 클릭만 막고 글자색은 유지
            is_disabled=item in disabled_items,
        )
        for item in items
    ]


def build_erp_sidebar(page:ft.Page, selected_menu: str, on_menu_click):
    # ☑️ 추가: 재고관리 확장형
    if selected_menu in com.STOCK_ALL_ITEMS:
        is_product_open = selected_menu in ["상품 재고 관리"] + com.STOCK_PRODUCT_ITEMS

        stock_controls = [
            _menu_item(
                text="창고관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=com.EXPANDED_TEXT_COLOR,
                active_color=com.PAGE_BG,
                active_bgcolor=com.EXPANDED_ACTIVE_BG,
                # 🔥 추가: 창고관리는 글자색은 유지하고 클릭만 막는다.
                is_disabled="창고관리" in com.DISABLED_STOCK_MENU_ITEMS,
            ),
            _menu_item(
                text="원자재 재고 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=com.EXPANDED_TEXT_COLOR,
                active_color=com.PAGE_BG,
                active_bgcolor=com.EXPANDED_ACTIVE_BG,
                # 🔥 추가: 원자재 재고 관리는 글자색은 유지하고 클릭만 막는다.
                is_disabled="원자재 재고 관리" in com.DISABLED_STOCK_MENU_ITEMS,
            ),
            _menu_item(
                text="상품 재고 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=com.EXPANDED_TEXT_COLOR,
                active_color=com.PAGE_BG,
                active_bgcolor=com.EXPANDED_ACTIVE_BG,
                is_forced_selected=selected_menu in com.STOCK_PRODUCT_ITEMS,
            ),
        ]

        if is_product_open:
            stock_controls.extend(
                [
                    _menu_item(
                        text=item,
                        selected_menu=selected_menu,
                        on_menu_click=on_menu_click,
                        text_color=com.EXPANDED_TEXT_COLOR,
                        active_color=com.EXPANDED_ACTIVE_BG,
                        active_bgcolor=None,
                        selected_weight=ft.FontWeight.BOLD,
                        left_padding=40,
                    )
                    for item in com.STOCK_PRODUCT_ITEMS
                ]
            )

        stock_controls.append(
            _menu_item(
                text="상품 부자재 관리",
                selected_menu=selected_menu,
                on_menu_click=on_menu_click,
                text_color=com.EXPANDED_TEXT_COLOR,
                active_color=com.PAGE_BG,
                active_bgcolor=com.EXPANDED_ACTIVE_BG,
                # 🔥 추가: 상품 부자재 관리는 글자색은 유지하고 클릭만 막는다.
                is_disabled="상품 부자재 관리" in com.DISABLED_STOCK_MENU_ITEMS,
            )
        )

        return _build_expanded_sidebar(
            page=page,
            header_control=_section_header("재고관리", on_menu_click),
            menu_controls=stock_controls,
        )

    # ☑️ 추가: 상품관리 확장형
    if selected_menu in com.PRODUCT_ALL_ITEMS:
        product_controls = _build_expanded_menu_controls(
            com.PRODUCT_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
            # 🔥 추가: 상품 상세 정보 관리만 클릭 가능, 나머지 3개는 클릭 불가
            disabled_items=com.DISABLED_PRODUCT_MENU_ITEMS,
        )

        return _build_expanded_sidebar(
            page=page,
            header_control=_section_header("상품관리", on_menu_click),
            menu_controls=product_controls,
        )

    # ☑️ 추가: 생산관리 확장형
    if selected_menu in com.PRODUCTION_ALL_ITEMS:
        production_controls = _build_expanded_menu_controls(
            com.PRODUCTION_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
            # 🔥 수정: 생산현황/생산입고/불량 현황/발주 관리/거래처 관리는 클릭 가능
            # 🔥 품질 및 이력 관리는 클릭 불가
            disabled_items=com.DISABLED_PRODUCTION_MENU_ITEMS,
        )

        return _build_expanded_sidebar(
            page=page,
            header_control=_section_header("생산관리", on_menu_click),
            menu_controls=production_controls,
        )

    # 🔥 추가: 고객관리 확장형
    if selected_menu in com.CUSTOMER_ALL_ITEMS:
        customer_controls = _build_expanded_menu_controls(
            com.CUSTOMER_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
            # 🔥 추가: 고객 정보/주문/구독 관리만 클릭 가능
            # 🔥 고객 문의 관리, 고객 센터 관리는 클릭 불가
            disabled_items=com.DISABLED_CUSTOMER_MENU_ITEMS,
        )

        return _build_expanded_sidebar(
            page=page,
            header_control=_section_header("고객관리", on_menu_click),
            menu_controls=customer_controls,
        )

    # 🔥 추가: 인사관리 확장형
    # - 인사관리 대분류 클릭 시에도 사원 관리가 선택된 상태로 열린다.
    if selected_menu in com.HR_ALL_ITEMS:
        hr_controls = _build_expanded_menu_controls(
            com.HR_MAIN_ITEMS,
            selected_menu,
            on_menu_click,
        )

        return _build_expanded_sidebar(
            page,page,
            header_control=_section_header("인사관리", on_menu_click),
            menu_controls=hr_controls,
        )

    menu_controls = [
        _menu_item(
            text=item,
            selected_menu=selected_menu,
            on_menu_click=on_menu_click,
            # 🔥 추가: 의미 없는 빈 화면/준비중 화면만 뜨는 메뉴는 클릭 불가 처리
            is_disabled=item in com.DISABLED_MAIN_MENU_ITEMS,
        )
        for item in com.ERP_MAIN_MENU_ITEMS
    ]

    return ft.Container(
        width=BASE_SIDEBAR_WIDTH,
        bgcolor=com.MAIN_COLOR,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            spacing=0,
            expand=True,
            controls=[
                # 🔥 수정: 기본 사이드바도 확장 사이드바와 같은 높이 사용
                _sidebar_brand_header(page),

                ft.Container(
                    expand=True,
                    width=BASE_SIDEBAR_WIDTH,
                    bgcolor=com.MAIN_COLOR,
                    padding=ft.padding.only(top=12, bottom=20),
                    content=ft.Column(
                        spacing=4,
                        controls=[
                            *menu_controls,
                        ],
                    ),
                ),
            ],
        ),
    )