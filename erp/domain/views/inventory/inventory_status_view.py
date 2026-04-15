import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_inventory_twin_chart


def erp_inventory_status_view():
    # ☑️ 공통: 5칸짜리 한 줄
    def build_five_text_row(row_items):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(-1, 0),
                    content=ft.Text(
                        value=row_items[0],
                        size=13,
                        color="#374151",
                    ),
                ),
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(-1, 0),
                    content=ft.Text(
                        value=row_items[1],
                        size=13,
                        color="#374151",
                    ),
                ),
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(-1, 0),
                    content=ft.Text(
                        value=row_items[2],
                        size=13,
                        color="#374151",
                    ),
                ),
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(-1, 0),
                    content=ft.Text(
                        value=row_items[3],
                        size=13,
                        color="#374151",
                    ),
                ),
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(1, 0),  # ☑️ 마지막 칸은 우측 정렬
                    content=ft.Text(
                        value=row_items[4],
                        size=13,
                        color="#374151",
                    ),
                ),
            ],
        )

    # ☑️ 공통: 동일 포맷 박스
    def build_status_box(title, count_text, subtitle, rows_data):
        return ft.Container(
            expand=1,
            height=260,
            bgcolor="#F9FAFB",
            border_radius=12,
            padding=16,
            border=ft.border.all(1, "#E5E7EB"),
            content=ft.Column(
                spacing=12,
                controls=[
                    # ☑️ 상단 헤더
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                value=title,
                                size=16,
                                color="#111827",
                                weight=ft.FontWeight.W_700,
                            ),
                            ft.Row(
                                spacing=4,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        value=count_text,
                                        size=13,
                                        color="#6B7280",
                                        weight=ft.FontWeight.W_600,
                                    ),
                                    ft.Icon(
                                        ft.Icons.CHEVRON_RIGHT,
                                        size=18,
                                        color="#9CA3AF",
                                    ),
                                ],
                            ),
                        ],
                    ),

                    # ☑️ 서브 텍스트
                    ft.Text(
                        value=subtitle,
                        size=13,
                        color="#6B7280",
                    ),

                    ft.Divider(height=1, color="#E5E7EB"),

                    # ☑️ 5칸 row × 5줄
                    ft.Column(
                        spacing=10,
                        controls=[
                            build_five_text_row(rows_data[0]),
                            build_five_text_row(rows_data[1]),
                            build_five_text_row(rows_data[2]),
                            build_five_text_row(rows_data[3]),
                            build_five_text_row(rows_data[4]),
                        ],
                    ),
                ],
            ),
        )

    # ☑️ 예시 데이터: 박스 1
    box1_rows = [
        ["26.04.08", "입고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "입고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "입고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "입고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "입고", "하림가맛시", "1,000 ea", "1,000만원"],
    ]

    # ☑️ 예시 데이터: 박스 2
    box2_rows = [
        ["26.04.08", "출고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "출고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "출고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "출고", "하림가맛시", "1,000 ea", "1,000만원"],
        ["26.04.08", "출고", "하림가맛시", "1,000 ea", "1,000만원"],
    ]

    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Text(
                    value="상품 재고 관리 > 재고 현황",
                    size=24,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),

                # ☑️ 상단 년월 + chevron
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=lambda e: print("이전"),
                        ),
                        ft.Text(
                            value="2026년 4월",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color="#222222",
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=lambda e: print("다음"),
                        ),
                    ],
                ),

                # ☑️ 상단 동일 포맷 박스 2개
                ft.Row(
                    spacing=16,
                    controls=[
                        build_status_box(
                            title="입고",
                            count_text="100건",
                            subtitle="최근 입고 내역",
                            rows_data=box1_rows,
                        ),
                        build_status_box(
                            title="출고",
                            count_text="100건",
                            subtitle="최근 출고 내역",
                            rows_data=box2_rows,
                        ),
                    ],
                ),

                build_inventory_twin_chart(),
            ],
        ),
    )