import flet as ft
from components import common as cm
from components.common.input_data.erp_home_view_input import home_view_data as hd
from components.common.input_data.erp_home_view_input import sale_inventory_data as si

def erp_home_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,   # 🔥 이거 추가
            controls=[
                ft.Text(
                    "매출 하이라이트",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=cm.TEXT_PRIMARY,
                ),
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        cm.erp_info_box("총 매출 ",f"{hd.get('total_sale',0)} 원", "2026년 누계 실적"),
                        cm.erp_info_box("연간 목표대비 달성", f"{hd.get('growth_goal',0)}%", "연간 목표:"),
                        cm.erp_info_box("전년대비 성장", f"{hd.get('last_year_growth',0)}%", ""),
                        cm.erp_info_box("총 판매량수", f"{hd.get('total_sale_value',0)}개", "2026년 누적 판매량수"),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=16,
                            controls=[
                                cm.gauge_chart(hd.get('month_rate',0), f"월간 목표 : {hd.get('month_goal',0)}만 원"),
                                cm.gauge_chart(hd.get('week_rate',0), f"주간 목표 : {hd.get('week_goal',0)}만 원"),
                            ],
                        ),
                        cm.build_sales_linechart(),
                    ],
                ),
                ft.Text(
                    "생산/재고 하이라이트",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color=cm.TEXT_PRIMARY,
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        cm.erp_info_box("이번달 생산량", si.get('monthly_production',0), ""),
                        cm.erp_info_box("입고 예정", si.get('incoming_planned',0), ""),
                        cm.erp_info_box("전년대비 성장", f"{si.get('yoy_growth',0)}%", ""),
                        cm.erp_info_box("총 판매량수", si.get('total_sales_count',0), ""),
                    ],
                ),
                ft.Row(
                spacing=16,
                controls=[
                    cm.build_production_status_box(),
                    cm.build_inventory_pie_chart_box(),
                ],
            ),
            ],
        ),
    )