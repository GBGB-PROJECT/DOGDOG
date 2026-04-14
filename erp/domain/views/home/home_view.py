import flet as ft
from components.common.erp_ui_boxes import erp_info_box
from components.common.charts.gauge_chart import gauge_chart
from components.common.charts.line_chart import build_sales_linechart
from components.common.charts.production_status_box import build_production_status_box
from components.common.charts.inventory_pie_chart_box import build_inventory_pie_chart_box


PAGE_BG = "#FFFFFF"


def erp_home_view():
    return ft.Container(
        expand=True,
        bgcolor=PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,   # 🔥 이거 추가
            controls=[
                ft.Text(
                    "매출 하이라이트",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color="#2B2F36",
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        erp_info_box("총 매출", "3,000,000만원", "2026년 누계 실적"),
                        erp_info_box("연간 목표대비 달성", "30%", "연간 목표:"),
                        erp_info_box("전년대비 성장", "30%", ""),
                        erp_info_box("총 판매량수", "98,400", "2026년 누적 판매량수"),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=16,
                            controls=[
                                gauge_chart(70, "월간 목표 : 000 만원"),
                                gauge_chart(45, "주간 목표 : 000 만원"),
                            ],
                        ),
                        build_sales_linechart(),
                    ],
                ),
                ft.Text(
                    "생산/재고 하이라이트",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color="#2B2F36",
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        erp_info_box("이번달 생산량", "30,000", ""),
                        erp_info_box("입고 예정", "21,000", ""),
                        erp_info_box("전년대비 성장", "30%", ""),
                        erp_info_box("총 판매량수", "98,400", ""),
                    ],
                ),
                ft.Row(
                spacing=16,
                controls=[
                    build_production_status_box(),
                    build_inventory_pie_chart_box(),
                ],
            ),
            ],
        ),
    )