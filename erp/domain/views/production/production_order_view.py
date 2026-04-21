import flet as ft
from components import common as cm
from components.common.modals.purchase_order import PurchaseOrderDialog


# ==============================
# ☑️ 공통 스타일
# ==============================
CARD_BG = "#F9FAFB"
WHITE = "#FFFFFF"
BORDER_COLOR = "#E5E7EB"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"
TEXT_ROW = "#374151"

ACTION_BLUE = "#2563EB"
BUTTON_BG = "#111827"


def erp_production_order_view():
    # ==============================
    # ☑️ 더미 데이터
    # ==============================
    order_rows = [
        {
            "order_date": "2026.04.07",
            "order_no": "PO-20260407-001",
            "client_name": "하림가맛시",
            "manager": "홍길동",
            "total_amount": "1,000,000원",
            "status": "발주 완료",
        },
        {
            "order_date": "2026.04.08",
            "order_no": "PO-20260408-002",
            "client_name": "오리온푸드",
            "manager": "김민수",
            "total_amount": "2,500,000원",
            "status": "입고 대기",
        },
        {
            "order_date": "2026.04.09",
            "order_no": "PO-20260409-003",
            "client_name": "청정사료",
            "manager": "이서연",
            "total_amount": "780,000원",
            "status": "검수 중",
        },
    ]

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
        padding=16,
        border_radius=12,
        bgcolor=CARD_BG,
        expand=False,
    ):
        return ft.Container(
            expand=expand,
            padding=padding,
            border_radius=border_radius,
            bgcolor=bgcolor,
            border=ft.border.all(1, BORDER_COLOR),
            content=content,
        )

    def open_purchase_order_dialog(e):
        popup = PurchaseOrderDialog(e.page)
        popup.open()

    def build_search_bar():
        return build_base_box(
            bgcolor=WHITE,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=220,
                                height=40,
                                border=ft.border.all(1, BORDER_COLOR),
                                border_radius=8,
                                padding=ft.Padding(left=10, top=0, right=10, bottom=0),
                                alignment=ft.Alignment(-1, 0),
                                content=ft.TextField(
                                    hint_text="발주번호 검색",
                                    border=ft.InputBorder.NONE,
                                    text_size=13,
                                    content_padding=ft.Padding(left=0, top=10, right=0, bottom=10),
                                ),
                            ),
                            ft.Container(
                                width=180,
                                height=40,
                                border=ft.border.all(1, BORDER_COLOR),
                                border_radius=8,
                                padding=ft.Padding(left=10, top=0, right=10, bottom=0),
                                alignment=ft.Alignment(-1, 0),
                                content=ft.TextField(
                                    hint_text="거래처 검색",
                                    border=ft.InputBorder.NONE,
                                    text_size=13,
                                    content_padding=ft.Padding(left=0, top=10, right=0, bottom=10),
                                ),
                            ),
                            ft.ElevatedButton(
                                "조회",
                                height=40,
                                style=ft.ButtonStyle(
                                    bgcolor=BUTTON_BG,
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ],
                    ),
                    ft.ElevatedButton(
                        "발주서 등록",
                        height=40,
                        style=ft.ButtonStyle(
                            bgcolor=ACTION_BLUE,
                            color=ft.Colors.WHITE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=open_purchase_order_dialog,
                    ),
                ],
            ),
        )

    def build_table_header():
        headers = [
            ("발주일자", 120),
            ("발주번호", 200),
            ("거래처", 180),
            ("담당자", 120),
            ("총금액", 150),
            ("상태", 120),
        ]

        return ft.Container(
            padding=ft.Padding(left=16, top=14, right=16, bottom=14),
            bgcolor="#F3F4F6",
            border_radius=8,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=width,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(
                            title,
                            size=13,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_700,
                        ),
                    )
                    for title, width in headers
                ],
            ),
        )

    def build_table_row(row_data: dict):
        return ft.Container(
            padding=ft.Padding(left=16, top=16, right=16, bottom=16),
            border=ft.border.only(bottom=ft.BorderSide(1, BORDER_COLOR)),
            ink=True,
            on_click=lambda e: print(f"선택한 발주번호: {row_data['order_no']}"),
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(row_data["order_date"], size=13, color=TEXT_ROW),
                    ),
                    ft.Container(
                        width=200,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(row_data["order_no"], size=13, color=TEXT_ROW),
                    ),
                    ft.Container(
                        width=180,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(row_data["client_name"], size=13, color=TEXT_ROW),
                    ),
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(row_data["manager"], size=13, color=TEXT_ROW),
                    ),
                    ft.Container(
                        width=150,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(row_data["total_amount"], size=13, color=TEXT_ROW),
                    ),
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(
                            row_data["status"],
                            size=13,
                            color=ACTION_BLUE,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                ],
            ),
        )

    def build_order_table():
        return build_base_box(
            bgcolor=WHITE,
            padding=16,
            content=ft.Column(
                spacing=0,
                controls=[
                    build_table_header(),
                    *[build_table_row(row) for row in order_rows],
                ],
            ),
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
                    "생산관리 > 발주 관리",
                    size=24,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                build_search_bar(),
                build_order_table(),
            ],
        ),
    )