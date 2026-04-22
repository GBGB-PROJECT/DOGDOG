import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_production_twin_chart

from components.common.modals.purchase_order import PurchaseOrderDialog


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


def erp_production_view():
    # ==============================
    # ☑️ 데이터 영역
    # ==============================
    page_title = "생산관리"
    current_month_text = "2026년 4월"

    status_box_data = [
        {
            "title": "생산 입고",
            "count_text": "100건",
            "subtitle": "최근 생산 내역",
            "rows": [
                ["26.04.08", "생산", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "생산", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "생산", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "생산", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "생산", "하림가맛시", "1,000 ea", "1,000만원"],
            ],
        },
        {
            "title": "불량 내역",
            "count_text": "100건",
            "subtitle": "최근 불량 내역",
            "rows": [
                ["26.04.08", "불량", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "불량", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "불량", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "불량", "하림가맛시", "1,000 ea", "1,000만원"],
                ["26.04.08", "불량", "하림가맛시", "1,000 ea", "1,000만원"],
            ],
        },
    ]

    top_production_item_template = {
        "name": "GAEBOB_260407",
        "action_text": "상세 내역",
        "rows": [
            ("발주 일자", "2026.04.07"),
            ("현 재고량", "1000 ea"),
            ("입고 예정일", "2026.04.21"),
        ],
    }

    def open_purchase_order_page(e):
        e.page.go("/production/order")

    def generate_top_production_items(count=5):
        return [
            {
                **top_production_item_template,
                "on_action_click": lambda e, idx=i: print(f"{idx + 1}번째 클릭"),
            }
            for i in range(count)
        ]

    top_production_section_data = {
        "title": "최근 발주 내역",
        "items": generate_top_production_items(5),
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
            value=value,
            size=size,
            color=color,
            weight=weight,
            text_align=text_align,
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

    def build_status_box(box_data):
        return build_base_box(
            expand=1,
            height=260,
            content=ft.Column(
                spacing=12,
                controls=[
                    build_box_header(box_data["title"], box_data["count_text"]),
                    build_text(box_data["subtitle"], size=13, color=TEXT_SECONDARY),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    ft.Column(
                        spacing=10,
                        controls=[build_five_text_row(row) for row in box_data["rows"]],
                    ),
                ],
            ),
        )

    def build_top_production_item_box(item_data):
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
                                item_data["name"],
                                size=12,
                                color=TEXT_TERTIARY,
                            )
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.TextButton(
                                item_data["action_text"],
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
                    *[build_info_row(left, right) for left, right in item_data["rows"]],
                ],
            ),
        )

    def build_top_production_box(section_data):
        return build_base_box(
            expand=1,
            padding=20,
            border_radius=16,
            content=ft.Column(
                spacing=16,
                controls=[
                    build_text(
                        section_data["title"],
                        size=18,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
                    ),
                    ft.Row(
                        spacing=12,
                        controls=[
                            build_top_production_item_box(item)
                            for item in section_data["items"]
                        ],
                    ),
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
                build_production_twin_chart(),
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
                        build_top_production_box(top_production_section_data),
                    ],
                ),
            ],
        ),
    )