import flet as ft
from components import common as cm
from erp.domain.controller.home.erp_home_controller import HomeViewMain



def erp_home_view():
    ## 컨트롤러에서 실제 데이터 가지고 오기
    try:
        raw_sale_data = HomeViewMain.sale_dashboard()
        ## 데이터가 없는 경우
        if not raw_sale_data:
            raise Exception("sale 데이터 없음")      
        sale_data = raw_sale_data
    except Exception as e:
        print(f"UI 연결을 실패했습니다: {e}") 
        ## 서버 연결 실패를 대비해 미리 0으로 초기화된 데이터를 준비한다.
        sale_data = {
            "total_sale": 0, "year": 2026, "growth_goal": 0, 
            "last_year_growth": 0, "total_sale_value": 0,
            "month_rate_text": 0, "month_goal": 0, 
            "week_rate_text": 0, "week_goal": 0
        }
    
    try:
        raw_inven_data = HomeViewMain.inventory_dashboard()
    ## 데이터가 없는 경우
        if not raw_inven_data:
            raise Exception("sale 데이터 없음")
        inven_data = raw_inven_data
    except Exception as e:
        print(f"UI 연결을 실패했습니다: {e}") 
        # 불러오기 실패 시 0을 가지고 옴
        inven_data = {
            "monthly_production_qty": 0,
            "expected_incoming_qty": 0,
            "current_total_inventory": 0,
            "monthly_avg_sales_qty": 0,
            "stock_type_status": {}
        }
    stock_status = inven_data.get("stock_type_status", {})
    total_stock_sum = sum(stock_status.values())

    if total_stock_sum > 0:
        feed_data = {
            k: round((v / total_stock_sum) * 100, 1)
            for k, v in stock_status.items()
        }
    else:
        feed_data = {}    
    
    prod_data = HomeViewMain.prduct_defect_chart()

    ## invent data의 전년도 동월대비 증감 전처리
    diff_value = inven_data.get('yoy_inventory_growth',0)
    # 양수일 경우 +
    sign = "+" if diff_value >= 0 else "-"
    # 부호+콤파 포맷팅 + 개 조합하기
    formatted_str = f"{sign}{diff_value:,}개"

    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
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
                        cm.erp_info_box("총 매출 ", f"{sale_data.get('total_amount',0):,} 원", f"{sale_data.get('year',0)}년 누계 기준"),
                        cm.erp_info_box("연간 목표대비 달성률", f"{sale_data.get('target_achievement_rate',0)}%", f"연간 목표매출: {sale_data.get('yearly_target_amount',0):,} 원"),
                        cm.erp_info_box("전년 동월대비 달성률", f"{sale_data.get('growth_rate',0)}%", f"기준: {sale_data.get('year',0)-1}년 동월 기준"),
                        cm.erp_info_box("총 판매량수", f"{sale_data.get('total_qty',0):,}개", f"{sale_data.get('year',0)}년 누적 판매량수"),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Column(
                            spacing=16,
                            controls=[
                                cm.gauge_chart(float(sale_data.get('monthly_achievement_rate', 0)), f"월간 목표 : {sale_data.get('monthly_target', 0) // 10000:,}만 원"),
                                cm.gauge_chart(float(sale_data.get('weekly_achievement_rate', 0)), f"주간 목표 : {sale_data.get('weekly_target', 0) // 10000:,}만 원"),
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
                        cm.erp_info_box("입고", f"{inven_data.get('monthly_production_qty',0):,}개",""),
                        cm.erp_info_box("입고 예정", f"{inven_data.get('expected_incoming_qty',0):,}개",""),
                        cm.erp_info_box("전년 동월 대비 재고 증감", formatted_str,""),
                        cm.erp_info_box("총 판매량수", f"{inven_data.get('monthly_total_sales',0):,}개",""),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        cm.build_production_status_box(prod_data if prod_data else {}),
                        cm.build_stock_pie_chart_box(feed_data),
                    ],
                ),
            ],
        ),
    )