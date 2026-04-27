import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_production_twin_chart

# 🔥 추가: 생산관리 메인 대시보드 DB 조회 service
from backend.erp.production.dashboard_service import fetch_production_dashboard


# ==============================
# ☑️ 공통 스타일
# ==============================
CARD_BG = "#F9FAFB"
CARD_INNER_BG = "#FFFFFF"
BORDER_COLOR = "#E5E7EB"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"
TEXT_ROW = "#374151"
ACTION_BLUE = "#2563EB"


# ==============================
# 🔥 DB 오류/빈 데이터 fallback
# - DB 연결 실패로 화면 자체가 죽는 것 방지
# ==============================
def _empty_dashboard_data():
    return {
        "current_month_text": "생산 현황",
        "status_box_data": [
            {
                "title": "생산 입고",
                "count_text": "0건",
                "subtitle": "최근 생산 내역",
                "rows": [],
            },
            {
                "title": "불량 내역",
                "count_text": "0건",
                "subtitle": "최근 불량 내역",
                "rows": [],
            },
        ],
        "chart_data": [(f"{month}월", 0, 0) for month in range(1, 13)],
        "top_production_section_data": {
            "title": "최근 발주 내역",
            "items": [],
        },
    }


# ==============================
# 🔥 생산관리 화면 본체
# ==============================
def erp_production_view():
    # ==============================
    # 🔥 데이터 영역
    # - 기존 더미 데이터 제거
    # - backend/erp/production/dashboard_service.py에서 실제 DB 데이터 조회
    # ==============================
    page_title = "생산관리"

    try:
        dashboard_data = fetch_production_dashboard()
    except Exception as exc:
        print(f"생산관리 대시보드 조회 실패: {exc}")
        dashboard_data = _empty_dashboard_data()

    current_month_text = dashboard_data.get("current_month_text", "생산 현황")
    status_box_data = dashboard_data.get("status_box_data", [])
    chart_data = dashboard_data.get("chart_data", [])
    top_production_section_data = dashboard_data.get(
        "top_production_section_data",
        {"title": "최근 발주 내역", "items": []},
    )

    def open_purchase_order_page(e):
        e.page.go("/production/order")

    # 🔥 최근 발주 카드의 상세 내역 클릭 시 발주관리 화면으로 이동
    def attach_purchase_item_click(items):
        new_items = []
        for item in items:
            copied = dict(item)
            copied["on_action_click"] = open_purchase_order_page
            new_items.append(copied)
        return new_items

    top_production_section_data = {
        **top_production_section_data,
        "items": attach_purchase_item_click(top_production_section_data.get("items", [])),
    }

    # ==============================
    # ☑️ 공통 함수
    # ==============================
    def build_text(
        value: str,
        size: int = 13,
        color: str = TEXT_PRIMARY,
        weight=ft.FontWeight.W_400,
        text_align: ft.TextAlign | None = None,
    ):
        return ft.Text(
            value=str(value or ""),
            size=size,
            color=color,
            weight=weight,
            text_align=text_align,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

    def build_base_box(
        content,
        expand=1,
        height=None,
        padding=16,
        border_radius=12,
        bgcolor=CARD_BG,
    ):
        return ft.Container(
            expand=expand,
            height=height,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            border=ft.border.all(1, BORDER_COLOR),
            content=content,
        )

    def build_info_row(left_text: str, right_text: str):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                build_text(left_text, size=13, color=TEXT_SECONDARY),
                build_text(
                    right_text,
                    size=13,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        )

    def build_box_header(title: str, right_text: str):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                build_text(
                    title,
                    size=16,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Row(
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        build_text(
                            right_text,
                            size=13,
                            color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_600,
                        ),
                        ft.Icon(
                            ft.Icons.CHEVRON_RIGHT,
                            size=18,
                            color=TEXT_TERTIARY,
                        ),
                    ],
                ),
            ],
        )

    def build_five_text_row(row_items):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(-1, 0) if i < len(row_items) - 1 else ft.Alignment(1, 0),
                    content=build_text(item, size=13, color=TEXT_ROW),
                )
                for i, item in enumerate(row_items)
            ],
        )

    def build_empty_message(message="표시할 데이터가 없습니다."):
        return ft.Container(
            height=142,
            alignment=ft.Alignment(0, 0),
            content=build_text(message, size=13, color=TEXT_SECONDARY),
        )

    def build_status_box(box_data):
        rows = box_data.get("rows", [])

        if rows:
            row_area = ft.Column(
                spacing=10,
                controls=[build_five_text_row(row) for row in rows],
            )
        else:
            row_area = build_empty_message()

        return build_base_box(
            expand=1,
            height=260,
            content=ft.Column(
                spacing=12,
                controls=[
                    build_box_header(box_data.get("title", ""), box_data.get("count_text", "0건")),
                    build_text(box_data.get("subtitle", ""), size=13, color=TEXT_SECONDARY),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    row_area,
                ],
            ),
        )

    def build_recent_purchase_item_box(item_data):
        return ft.Container(
            expand=1,
            height=210,
            padding=16,
            border_radius=12,
            bgcolor=CARD_INNER_BG,
            border=ft.border.all(1, BORDER_COLOR),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            build_text(
                                item_data.get("name", ""),
                                size=12,
                                color=TEXT_TERTIARY,
                            )
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.TextButton(
                                item_data.get("action_text", "상세 내역"),
                                on_click=item_data.get("on_action_click"),
                                style=ft.ButtonStyle(
                                    padding=0,
                                    color=ACTION_BLUE,
                                    text_style=ft.TextStyle(
                                        size=13,
                                        weight=ft.FontWeight.W_600,
                                    ),
                                ),
                            )
                        ],
                    ),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    *[
                        build_info_row(left, right)
                        for left, right in item_data.get("rows", [])
                    ],
                ],
            ),
        )

    def build_recent_purchase_box(section_data):
        items = section_data.get("items", [])

        if items:
            item_area = ft.Row(
                spacing=12,
                controls=[
                    build_recent_purchase_item_box(item)
                    for item in items
                ],
            )
        else:
            item_area = build_empty_message("최근 발주 내역이 없습니다.")

        return build_base_box(
            expand=1,
            padding=20,
            border_radius=16,
            content=ft.Column(
                spacing=16,
                controls=[
                    build_text(
                        section_data.get("title", "최근 발주 내역"),
                        size=18,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
                    ),
                    item_area,
                ],
            ),
        )

    def build_month_navigation():
        def nav_button(icon, message):
            return ft.IconButton(
                icon=icon,
                icon_size=20,
                on_click=lambda e: print(message),
            )

        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                nav_button(ft.Icons.CHEVRON_LEFT, "이전"),
                build_text(
                    current_month_text,
                    size=18,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),
                nav_button(ft.Icons.CHEVRON_RIGHT, "다음"),
            ],
        )

    # ==============================
    # ☑️ 최종 화면
    # ==============================
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                build_text(
                    page_title,
                    size=24,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),
                build_month_navigation(),
                ft.Row(
                    spacing=16,
                    controls=[build_status_box(box) for box in status_box_data],
                ),
                # 🔥 수정: 실제 DB chart_data 전달
                build_production_twin_chart(chart_data=chart_data),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(
                            width=180,
                            height=260,
                            bgcolor=CARD_BG,
                            border_radius=12,
                            padding=12,
                            border=ft.border.all(1, BORDER_COLOR),
                            ink=True,
                            on_click=open_purchase_order_page,
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.START,
                                        controls=[
                                            ft.Text(
                                                "발주관리",
                                                size=16,
                                                weight=ft.FontWeight.W_700,
                                                color=TEXT_PRIMARY,
                                            ),
                                            ft.Icon(
                                                ft.Icons.CHEVRON_RIGHT,
                                                size=18,
                                                color=TEXT_TERTIARY,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                        ),
                        build_recent_purchase_box(top_production_section_data),
                    ],
                ),
            ],
        ),
    )
