import flet as ft

from components import common as cm
from erp.domain.controller.home.erp_home_controller import HomeViewMain


HOME_PAGE_BG = "#F5F7FA"


def _default_sale_data():
    return {
        "total_amount": 0,
        "year": 2026,
        "target_achievement_rate": 0,
        "yearly_target_amount": 0,
        "growth_rate": 0,
        "total_qty": 0,
        "monthly_achievement_rate": 0,
        "monthly_target": 0,
        "weekly_achievement_rate": 0,
        "weekly_target": 0,
    }


def _default_inventory_data():
    return {
        "monthly_production_qty": 0,
        "expected_incoming_qty": 0,
        "current_total_inventory": 0,
        "monthly_avg_sales_qty": 0,
        "monthly_total_sales": 0,
        "yoy_inventory_growth": 0,
        "stock_type_status": {},
    }


def _load_home_data():
    try:
        sale_data = HomeViewMain.sale_dashboard()
        if not sale_data:
            raise Exception("sale data empty")
    except Exception as exc:
        print(f"홈 매출 데이터 조회 실패: {exc}")
        sale_data = _default_sale_data()

    try:
        inventory_data = HomeViewMain.inventory_dashboard()
        if not inventory_data:
            raise Exception("inventory data empty")
    except Exception as exc:
        print(f"홈 재고 데이터 조회 실패: {exc}")
        inventory_data = _default_inventory_data()

    try:
        production_data = HomeViewMain.prduct_defect_chart() or {}
    except Exception as exc:
        print(f"홈 생산 차트 조회 실패: {exc}")
        production_data = {}

    return sale_data, inventory_data, production_data


def _build_home_content(sale_data, inventory_data, production_data):
    stock_status = inventory_data.get("stock_type_status", {}) or {}
    total_stock_sum = sum(stock_status.values())

    feed_data = (
        {
            key: round((value / total_stock_sum) * 100, 1)
            for key, value in stock_status.items()
        }
        if total_stock_sum > 0
        else {}
    )

    diff_value = inventory_data.get("yoy_inventory_growth", 0)
    sign = "+" if diff_value >= 0 else "-"
    formatted_inventory_growth = f"{sign}{diff_value:,}개"

    return ft.Column(
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
                    cm.erp_info_box(
                        "총 매출",
                        f"{sale_data.get('total_amount', 0):,} 원",
                        f"{sale_data.get('year', 0)}년 누계 기준",
                    ),
                    cm.erp_info_box(
                        "연간 목표대비 달성률",
                        f"{sale_data.get('target_achievement_rate', 0)}%",
                        f"연간 목표매출: {sale_data.get('yearly_target_amount', 0):,} 원",
                    ),
                    cm.erp_info_box(
                        "전년 동월대비 달성률",
                        f"{sale_data.get('growth_rate', 0)}%",
                        f"기준: {sale_data.get('year', 0) - 1}년 동월 기준",
                    ),
                    cm.erp_info_box(
                        "총 판매횟수",
                        f"{sale_data.get('total_qty', 0):,}개",
                        f"{sale_data.get('year', 0)}년 누적 판매횟수",
                    ),
                ],
            ),
            ft.Row(
                spacing=16,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        spacing=16,
                        controls=[
                            cm.gauge_chart(
                                float(sale_data.get("monthly_achievement_rate", 0)),
                                f"월간 목표 : {sale_data.get('monthly_target', 0) // 10000:,}만원",
                            ),
                            cm.gauge_chart(
                                float(sale_data.get("weekly_achievement_rate", 0)),
                                f"주간 목표 : {sale_data.get('weekly_target', 0) // 10000:,}만원",
                            ),
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
                    cm.erp_info_box(
                        "입고",
                        f"{inventory_data.get('monthly_production_qty', 0):,}개",
                        "",
                    ),
                    cm.erp_info_box(
                        "입고 예정",
                        f"{inventory_data.get('expected_incoming_qty', 0):,}개",
                        "",
                    ),
                    cm.erp_info_box(
                        "전년 동월 대비 재고 증감",
                        formatted_inventory_growth,
                        "",
                    ),
                    cm.erp_info_box(
                        "총 판매횟수",
                        f"{inventory_data.get('monthly_total_sales', 0):,}개",
                        "",
                    ),
                ],
            ),
            ft.Row(
                spacing=16,
                controls=[
                    cm.build_production_status_box(production_data),
                    cm.build_stock_pie_chart_box(feed_data),
                ],
            ),
        ],
    )


def erp_home_view():
    page_ref = {"page": None, "mounted": False}
    content_holder = ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            "홈 데이터를 불러오는 중입니다.",
            size=16,
            weight=ft.FontWeight.W_600,
            color=cm.TEXT_SECONDARY,
        ),
    )

    class HomePage(ft.Container):
        def did_mount(self):
            page_ref["page"] = self.page
            page_ref["mounted"] = True

            def worker():
                sale_data, inventory_data, production_data = _load_home_data()
                if not page_ref["mounted"]:
                    return
                content_holder.alignment = None
                content_holder.content = _build_home_content(
                    sale_data,
                    inventory_data,
                    production_data,
                )
                if page_ref["mounted"]:
                    page_ref["page"].update()

            page_ref["page"].run_thread(worker)

        def will_unmount(self):
            page_ref["mounted"] = False
            page_ref["page"] = None

    return HomePage(
        expand=True,
        bgcolor=HOME_PAGE_BG,
        padding=20,
        content=content_holder,
    )
