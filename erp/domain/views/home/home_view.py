import flet as ft
from components import common as cm
from service.erp_homeview_service import get_home_view_data

def erp_home_view():
    # 데이터 가져오기
    sale_data, inventory_data, feed_data = get_home_view_data()
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
                        cm.erp_info_box("총 매출 ",f"{sale_data.get('total_sale',0)} 원", "2026년 누계 실적"),
                        cm.erp_info_box("연간 목표대비 달성", f"{sale_data.get('growth_goal',0)}%", "연간 목표:"),
                        cm.erp_info_box("전년대비 성장", f"{sale_data.get('last_year_growth',0)}%", ""),
                        cm.erp_info_box("총 판매량수", f"{sale_data.get('total_sale_value',0)}개", "2026년 누적 판매량수"),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=16,
                            controls=[
                                cm.gauge_chart(float(sale_data.get('month_rate_text', 0)), f"월간 목표 : {sale_data.get('month_goal', 0)}만 원"),
                                cm.gauge_chart(float(sale_data.get('week_rate_text', 0)), f"주간 목표 : {sale_data.get('week_goal', 0)}만 원"),
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
                        cm.erp_info_box("이번달 생산량", f"{inventory_data.get('monthly_production_qty',0)}",""),
                        cm.erp_info_box("입고 예정", f"{inventory_data.get('expected_incoming_qty',0)}",""),
                        cm.erp_info_box("전년대비 성장", f"{inventory_data.get('current_total_inventory',0)}",""),
                        cm.erp_info_box("총 판매량수", f"{inventory_data.get('monthly_avg_sales_qty',0)}",""),
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