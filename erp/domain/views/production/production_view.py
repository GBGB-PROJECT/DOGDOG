import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_production_twin_chart

# 🔥 생산관리 메인 대시보드 DB 조회 service
from backend.erp.production.dashboard_service import fetch_production_dashboard

# 🔥 생산 입고 count 클릭 시 입고 화면에 해당 월 필터 전달
from domain.views.production.inbound_view import set_production_inbound_prefilter

# 🔥 최근 발주 카드 상세 내역 모달 조회
from backend.erp.production.production_supplier_service import (
    fetch_purchase_order_detail,
    fetch_purchase_order_items,
)
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


# ==============================
# 🔥 DB 오류/빈 데이터 fallback
# - DB 연결 실패로 화면 자체가 죽는 것 방지
# ==============================
def _empty_dashboard_data(year=2026, month=4):
    return {
        "current_year": year,
        "current_month": month,
        "current_month_text": f"{year}년 {month}월",
        "month_start": f"{year:04d}-{month:02d}-01",
        "month_end": f"{year:04d}-{month:02d}-01",
        "status_box_data": [
            {
                "title": "생산 입고",
                "count_text": "0건",
                "count": 0,
                "subtitle": "최근 생산 내역",
                "rows": [],
            },
            {
                "title": "불량 내역",
                "count_text": "0건",
                "count": 0,
                "subtitle": "최근 불량 내역",
                "rows": [],
            },
        ],
        "chart_data": [(f"{month_no}월", 0, 0) for month_no in range(1, 13)],
        "top_production_section_data": {
            "title": "최근 발주 내역",
            "items": [],
        },
    }


# ==============================
# 🔥 월 이동 계산
# ==============================
def _move_month(year: int, month: int, diff: int):
    month_index = (year * 12) + (month - 1) + diff
    new_year = month_index // 12
    new_month = (month_index % 12) + 1
    return new_year, new_month


# ==============================
# 🔥 생산관리 화면 본체
# ==============================
def erp_production_view():
    page_title = "생산관리"

    try:
        initial_data = fetch_production_dashboard()
    except Exception as exc:
        print(f"생산관리 대시보드 조회 실패: {exc}")
        initial_data = _empty_dashboard_data()

    state = {
        "year": int(initial_data.get("current_year") or 2026),
        "month": int(initial_data.get("current_month") or 4),
        "data": initial_data,
    }

    month_navigation_holder = ft.Container()
    status_box_holder = ft.Container()
    chart_holder = ft.Container()
    recent_purchase_holder = ft.Container()

    def open_purchase_order_page(e):
        e.page.go("/production/order")

    def open_month_inbound_page(e):
        data = state["data"]
        set_production_inbound_prefilter(
            start_date=data.get("month_start"),
            end_date=data.get("month_end"),
            search_type="inbound_complete",
        )
        e.page.go("/production/inbound")

    # 🔥 최근 발주 카드의 상세 내역 클릭 시 바로 발주서 모달 열기
    # - 월 이동 기능과 충돌하지 않게 reload_dashboard()에서 매번 다시 바인딩함
    def open_purchase_order_detail(e, purchase_order_id):
        try:
            if not purchase_order_id:
                print("발주 상세 조회 실패: purchase_order_id 없음")
                return

            order_data = fetch_purchase_order_detail(purchase_order_id)
            item_rows = fetch_purchase_order_items(purchase_order_id)

            if not order_data:
                print(f"발주 상세 조회 실패: 발주ID {purchase_order_id} 데이터 없음")
                return

            dialog = PurchaseOrderDialog(e.page)
            if hasattr(dialog, "set_order_data"):
                dialog.set_order_data(order_data, item_rows)
            dialog.open()

        except Exception as exc:
            print(f"발주 상세 조회 실패: {exc}")

    def attach_purchase_item_click(items):
        new_items = []
        for item in items:
            copied = dict(item)
            purchase_order_id = copied.get("purchase_order_id")
            copied["on_action_click"] = (
                lambda e, po_id=purchase_order_id: open_purchase_order_detail(e, po_id)
            )
            new_items.append(copied)
        return new_items

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
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=76,
                    alignment=ft.Alignment(-1, 0),
                    content=build_text(left_text, size=13, color=TEXT_SECONDARY),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(1, 0),
                    content=build_text(
                        right_text,
                        size=13,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_600,
                        text_align=ft.TextAlign.RIGHT,
                    ),
                ),
            ],
        )

    def build_box_header(title: str, right_text: str, on_click=None):
        right_area = ft.Container(
            border_radius=8,
            ink=True if on_click else False,
            on_click=on_click,
            padding=ft.Padding.only(left=8, right=2, top=4, bottom=4),
            content=ft.Row(
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
        )

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
                right_area,
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
        title = box_data.get("title", "")
        header_click = open_month_inbound_page if title == "생산 입고" else None

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
                    build_box_header(title, box_data.get("count_text", "0건"), on_click=header_click),
                    build_text(box_data.get("subtitle", ""), size=13, color=TEXT_SECONDARY),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    row_area,
                ],
            ),
        )

    def build_recent_purchase_item_box(item_data):
        return ft.Container(
            width=220,  # 🔥 수정: 5개 카드가 모두 같은 폭으로 보이도록 고정
            height=210,
            padding=16,
            border_radius=12,
            bgcolor=CARD_INNER_BG,
            border=ft.border.all(1, BORDER_COLOR),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        height=34,
                        alignment=ft.Alignment(1, 0),
                        content=build_text(
                            item_data.get("name", ""),
                            size=12,
                            color=TEXT_TERTIARY,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ),
                    ft.Container(
                        height=28,
                        alignment=ft.Alignment(1, 0),
                        content=ft.TextButton(
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
                        ),
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
        # 🔥 최근 발주 카드는 5개 모두 같은 크기로 고정
        # - expand=1 방식은 긴 상품명이 있는 카드가 더 넓어져서 월마다 카드 폭이 흔들릴 수 있음
        # - width=220 고정 카드 5개를 Row에 배치해서 모든 월에서 같은 모양 유지
        items = section_data.get("items", [])[:5]

        if items:
            item_area = ft.Container(
                height=226,  # 🔥 수정: 가로 스크롤바가 들어갈 여유 높이 확보
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Row(
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,  # 🔥 수정: 카드 5개가 화면을 넘으면 가로 스크롤 가능
                    alignment=ft.MainAxisAlignment.START,  # 🔥 수정: 잘림 없이 첫 카드부터 고정 배치
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        build_recent_purchase_item_box(item)
                        for item in items
                    ],
                ),
            )
        else:
            item_area = ft.Container(
                height=210,
                alignment=ft.Alignment(0, 0),
                content=build_text("최근 발주 내역이 없습니다.", size=13, color=TEXT_SECONDARY),
            )

        return build_base_box(
            expand=1,
            height=298,  # 🔥 수정: 카드 영역 + 가로 스크롤바 높이까지 포함
            padding=20,
            border_radius=16,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        height=24,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(
                            section_data.get("title", "최근 발주 내역"),
                            size=18,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_700,
                        ),
                    ),
                    item_area,
                ],
            ),
        )

    def reload_dashboard(page=None):
        try:
            dashboard_data = fetch_production_dashboard(
                year=state["year"],
                month=state["month"],
            )
        except Exception as exc:
            print(f"생산관리 대시보드 월 이동 조회 실패: {exc}")
            dashboard_data = _empty_dashboard_data(state["year"], state["month"])

        state["data"] = dashboard_data
        state["year"] = int(dashboard_data.get("current_year") or state["year"])
        state["month"] = int(dashboard_data.get("current_month") or state["month"])

        section_data = dashboard_data.get(
            "top_production_section_data",
            {"title": "최근 발주 내역", "items": []},
        )

        section_data = {
            **section_data,
            "items": attach_purchase_item_click(section_data.get("items", [])),
        }

        month_navigation_holder.content = build_month_navigation()
        status_box_holder.content = ft.Row(
            spacing=16,
            controls=[
                build_status_box(box)
                for box in dashboard_data.get("status_box_data", [])
            ],
        )
        chart_holder.content = build_production_twin_chart(
            chart_data=dashboard_data.get("chart_data", [])
        )
        recent_purchase_holder.content = build_recent_purchase_box(section_data)

        if page:
            page.update()

    def move_dashboard_month(diff: int, e):
        new_year, new_month = _move_month(state["year"], state["month"], diff)
        state["year"] = new_year
        state["month"] = new_month
        reload_dashboard(e.page)

    def build_month_navigation():
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_size=20,
                    on_click=lambda e: move_dashboard_month(-1, e),
                ),
                build_text(
                    state["data"].get("current_month_text", f"{state['year']}년 {state['month']}월"),
                    size=18,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_RIGHT,
                    icon_size=20,
                    on_click=lambda e: move_dashboard_month(1, e),
                ),
            ],
        )

    reload_dashboard()

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
                month_navigation_holder,
                status_box_holder,
                chart_holder,
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
                        recent_purchase_holder,
                    ],
                ),
            ],
        ),
    )
