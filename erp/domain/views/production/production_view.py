import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_production_twin_chart

# 🔥 생산관리 메인 대시보드 DB 조회 service
from backend.erp.production.dashboard_service import fetch_production_dashboard

# 🔥 생산 입고 count 클릭 시 입고 화면에 해당 월 필터 전달
from domain.views.production.inbound_view import set_production_inbound_prefilter

# 🔥 발주관리 상자 클릭 시 해당 월 발주 목록 필터 전달
from domain.views.production.purchase_order_view import set_purchase_order_prefilter

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
ACTION_RED = "#EF4444"


# ==============================
# 🔥 생산관리 월 상태 유지용 전역값
# - 생산입고/발주관리로 이동 후 다시 돌아와도 마지막 선택 월 유지
# - on_mount 사용 안 함
# ==============================
_PRODUCTION_DASHBOARD_MONTH_STATE = {
    "year": None,
    "month": None,
}


def set_production_dashboard_month_state(year=None, month=None):
    if year is None or month is None:
        return

    _PRODUCTION_DASHBOARD_MONTH_STATE["year"] = int(year)
    _PRODUCTION_DASHBOARD_MONTH_STATE["month"] = int(month)


def get_production_dashboard_month_state():
    year = _PRODUCTION_DASHBOARD_MONTH_STATE.get("year")
    month = _PRODUCTION_DASHBOARD_MONTH_STATE.get("month")

    if year is None or month is None:
        return None, None

    return int(year), int(month)


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

    saved_year, saved_month = get_production_dashboard_month_state()

    try:
        # 🔥 저장된 월이 있으면 그 월로 다시 조회
        # - 예: 2026년 2월에서 발주관리/생산입고 갔다가 돌아오면 2026년 2월 유지
        if saved_year and saved_month:
            initial_data = fetch_production_dashboard(
                year=saved_year,
                month=saved_month,
            )
        else:
            initial_data = fetch_production_dashboard()
    except Exception as exc:
        print(f"생산관리 대시보드 조회 실패: {exc}")
        initial_data = _empty_dashboard_data(
            saved_year or 2026,
            saved_month or 4,
        )

    state = {
        "year": int(initial_data.get("current_year") or saved_year or 2026),
        "month": int(initial_data.get("current_month") or saved_month or 4),
        "data": initial_data,
    }

    # 🔥 최초 진입 시에도 현재 월 저장
    set_production_dashboard_month_state(state["year"], state["month"])

    month_navigation_holder = ft.Container()
    status_box_holder = ft.Container()
    chart_holder = ft.Container()
    recent_purchase_holder = ft.Container()

    # 🔥 발주관리 상자 우측 최하단 월 표시용 holder
    purchase_month_text_holder = ft.Container()

    def open_purchase_order_page(e):
        data = state["data"]

        # 🔥 이동 직전 현재 월 저장
        set_production_dashboard_month_state(state["year"], state["month"])

        set_purchase_order_prefilter(
            start_date=data.get("month_start"),
            end_date=data.get("month_end"),
            date_type="contract_date",
        )

        e.page.go("/production/order")

    def open_month_inbound_page(e):
        data = state["data"]

        # 🔥 이동 직전 현재 월 저장
        set_production_dashboard_month_state(state["year"], state["month"])

        set_production_inbound_prefilter(
            start_date=data.get("month_start"),
            end_date=data.get("month_end"),
            search_type="inbound_complete",
        )

        e.page.go("/production/inbound")

    # 🔥 최근 발주 카드의 상세내역 클릭 시 바로 발주서 모달 열기
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
        max_lines: int = 1,
    ):
        return ft.Text(
            value=str(value or ""),
            size=size,
            color=color,
            weight=weight,
            text_align=text_align,
            max_lines=max_lines,
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
                    width=78,
                    alignment=ft.Alignment(-1, 0),
                    content=build_text(
                        left_text,
                        size=13,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
                    ),
                ),
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(1, 0),
                    content=build_text(
                        right_text,
                        size=13,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
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
                    alignment=ft.Alignment(-1, 0)
                    if i < len(row_items) - 1
                    else ft.Alignment(1, 0),
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
                    build_box_header(
                        title,
                        box_data.get("count_text", "0건"),
                        on_click=header_click,
                    ),
                    build_text(
                        box_data.get("subtitle", ""),
                        size=13,
                        color=TEXT_SECONDARY,
                    ),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    row_area,
                ],
            ),
        )

    def build_recent_purchase_item_box(item_data):
        return ft.Container(
            width=220,
            height=220,
            padding=16,
            border_radius=12,
            bgcolor=CARD_INNER_BG,
            border=ft.border.all(1, BORDER_COLOR),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Container(
                        height=34,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(
                            item_data.get("name", ""),
                            size=13,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.LEFT,
                        ),
                    ),
                    ft.Container(
                        height=28,
                        alignment=ft.Alignment(1, 0),
                        content=ft.TextButton(
                            item_data.get("action_text", "상세내역"),
                            on_click=item_data.get("on_action_click"),
                            style=ft.ButtonStyle(
                                padding=0,
                                color=ACTION_RED,
                                text_style=ft.TextStyle(
                                    size=12,
                                    weight=ft.FontWeight.W_500,
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
        items = section_data.get("items", [])[:5]

        if items:
            item_area = ft.Container(
                height=238,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Row(
                    spacing=12,
                    scroll=ft.ScrollMode.AUTO,
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        build_recent_purchase_item_box(item)
                        for item in items
                    ],
                ),
            )
        else:
            item_area = ft.Container(
                height=220,
                alignment=ft.Alignment(0, 0),
                content=build_text(
                    "최근 발주 내역이 없습니다.",
                    size=13,
                    color=TEXT_SECONDARY,
                ),
            )

        return build_base_box(
            expand=1,
            height=310,
            padding=20,
            border_radius=16,
            bgcolor=CARD_BG,
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

    # ==============================
    # 🔥 발주관리 왼쪽 상자 하단 월 표시 생성
    # ==============================
    def build_purchase_month_text():
        month_text = state["data"].get(
            "current_month_text",
            f"{state['year']}년 {state['month']}월",
        )

        return ft.Container(
            expand=True,
            alignment=ft.Alignment(1, 1),
            padding=ft.Padding.only(right=0, bottom=0),
            content=ft.Text(
                value=month_text,
                size=16,
                weight=ft.FontWeight.W_700,
                color=TEXT_PRIMARY,
                text_align=ft.TextAlign.RIGHT,
            ),
        )

    def build_purchase_menu_box():
        return ft.Container(
            width=180,
            height=260,
            bgcolor=CARD_BG,
            border_radius=12,
            padding=12,
            border=ft.border.all(1, BORDER_COLOR),
            ink=True,
            on_click=open_purchase_order_page,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment(0, -1),
                        content=ft.Row(
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
                    ),
                    purchase_month_text_holder,
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

        # 🔥 현재 월 상태 저장
        # - 생산입고/발주관리 이동 후 다시 돌아와도 이 월로 재조회
        set_production_dashboard_month_state(state["year"], state["month"])

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

        purchase_month_text_holder.content = build_purchase_month_text()

        if page:
            page.update()

    def move_dashboard_month(diff: int, e):
        new_year, new_month = _move_month(state["year"], state["month"], diff)

        state["year"] = new_year
        state["month"] = new_month

        # 🔥 CHEVRON으로 월 이동하는 순간에도 저장
        set_production_dashboard_month_state(new_year, new_month)

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
                    state["data"].get(
                        "current_month_text",
                        f"{state['year']}년 {state['month']}월",
                    ),
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
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        build_purchase_menu_box(),
                        recent_purchase_holder,
                    ],
                ),
            ],
        ),
    )