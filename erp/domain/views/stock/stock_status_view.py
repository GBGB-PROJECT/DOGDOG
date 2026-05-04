import re
from datetime import datetime, timedelta
import flet as ft

from components.common.erp_busy_cursor import go_with_busy_cursor
from components import common as cm
from components.common.charts.twin_chart import build_stock_twin_chart
from components.common.modals.production_order import (
    ProductionOrderDialog,
    to_int,
    format_number,
)

# 🔥 requests 방식 API 호출로 변경
from api.erp_httpx_api import fetch_stock_dashboard

# 🔥 재고현황 → 입고/출고 관리 화면 월 필터 전달
from domain.views.stock.stock_inout_view import set_stock_inout_prefilter
from domain.views.stock.stock_product_detail_view import set_stock_product_detail_prefilter
from components.common.erp_view_widgets import build_text
from components.common.erp_dashboard_utils import move_month as _move_month


# ==============================
# ☑️ 공통 스타일
# ==============================
CARD_BG = "#FFFFFF"  # 🔥 수정: 화면 카드 배경 흰색 통일
CARD_INNER_BG = "#FFFFFF"
BORDER_COLOR = "#E5E7EB"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"
TEXT_ROW = "#374151"
ACTION_BLUE = "#2563EB"
# 🔥 추가: 최초 진입 기본 조회 월을 2026년 5월로 고정
DEFAULT_DASHBOARD_YEAR = 2026
DEFAULT_DASHBOARD_MONTH = 5


# ==============================
# 🔥 재고 현황 월 상태 유지용 전역값
# - 다른 화면 이동 후 다시 돌아와도 마지막 선택 월 유지
# - on_mount 사용 안 함
# ==============================
_STOCK_DASHBOARD_MONTH_STATE = {
    "year": None,
    "month": None,
}


def set_stock_dashboard_month_state(year=None, month=None):
    if year is None or month is None:
        return

    _STOCK_DASHBOARD_MONTH_STATE["year"] = int(year)
    _STOCK_DASHBOARD_MONTH_STATE["month"] = int(month)


def get_stock_dashboard_month_state():
    year = _STOCK_DASHBOARD_MONTH_STATE.get("year")
    month = _STOCK_DASHBOARD_MONTH_STATE.get("month")

    if year is None or month is None:
        return None, None

    return int(year), int(month)


# ==============================
# 🔥 DB 오류/빈 데이터 fallback
# - DB 연결 실패로 화면 자체가 죽는 것 방지
# ==============================
def _empty_dashboard_data(year=DEFAULT_DASHBOARD_YEAR, month=DEFAULT_DASHBOARD_MONTH):
    return {
        "current_year": year,
        "current_month": month,
        "current_month_text": f"{year}년 {month}월",
        "month_start": f"{year:04d}-{month:02d}-01",
        "month_end": f"{year:04d}-{month:02d}-01",
        "status_box_data": [
            {
                "title": "입고",
                "count_text": "0건",
                "count": 0,
                "subtitle": "최근 입고 내역",
                "rows": [],
            },
            {
                "title": "출고",
                "count_text": "0건",
                "count": 0,
                "subtitle": "최근 출고 내역",
                "rows": [],
            },
        ],
        "chart_data": [(f"{month_no}월", 0, 0) for month_no in range(1, 13)],
        "total_stock_quantity": 0,
        "total_stock_quantity_text": "0 ea",
        "expiring_stock_count": 0,
        "expiring_stock_count_text": "0건",
        "expiring_stock_days": 30,
        "top_stock_section_data": {
            "title": "매출 TOP 3 재고",
            "items": [],
        },
    }


# ==============================
# 🔥 월 이동 계산
# ==============================
def erp_stock_status_view():
    page_title = "상품 재고 관리 > 재고 현황"

    saved_year, saved_month = get_stock_dashboard_month_state()

    try:
        if saved_year and saved_month:
            initial_data = fetch_stock_dashboard(
                year=saved_year,
                month=saved_month,
            )
        else:
            # 🔥 수정: 화면 최초 진입 시에는 데이터가 많은 2026년 5월을 기본 조회
            initial_data = fetch_stock_dashboard(year=DEFAULT_DASHBOARD_YEAR, month=DEFAULT_DASHBOARD_MONTH)
    except Exception as exc:
        print(f"재고 현황 대시보드 조회 실패: {exc}")
        initial_data = _empty_dashboard_data(
            saved_year or DEFAULT_DASHBOARD_YEAR,
            saved_month or DEFAULT_DASHBOARD_MONTH,
        )

    state = {
        "year": int(initial_data.get("current_year") or saved_year or DEFAULT_DASHBOARD_YEAR),
        "month": int(initial_data.get("current_month") or saved_month or DEFAULT_DASHBOARD_MONTH),
        "data": initial_data,
    }

    set_stock_dashboard_month_state(state["year"], state["month"])

    month_navigation_holder = ft.Container()
    status_box_holder = ft.Container()
    chart_holder = ft.Container()
    top_stock_holder = ft.Container()

    def open_stock_inout_page(e, inout_type="all"):
        data = state["data"]

        set_stock_dashboard_month_state(state["year"], state["month"])

        set_stock_inout_prefilter(
            start_date=data.get("month_start"),
            end_date=data.get("month_end"),
            inout_type=inout_type,
            search_type="all",
            keyword="",
        )

        go_with_busy_cursor(e.page, "/stock/product/inout")

    def open_stock_product_detail_page(e):
        data = state["data"]

        set_stock_dashboard_month_state(state["year"], state["month"])

        # 🔥 수정: 왼쪽 카드는 유통기한 임박 재고 확인용 이동 카드로 사용
        # - 상품별 재고 상세의 기존 DatePicker 필터를 재사용한다.
        today = datetime.now().date()
        expiring_days = int(data.get("expiring_stock_days") or 30)
        end_date = today + timedelta(days=expiring_days)

        set_stock_product_detail_prefilter(
            start_date=today.isoformat(),
            end_date=end_date.isoformat(),
            date_filter_type="expiration_date",
            search_type="product",
            keyword="",
        )

        go_with_busy_cursor(e.page, "/stock/product/detail")

    def _extract_quantity_number(text):
        if text is None:
            return ""

        value = str(text)
        matched = re.search(r"[\d,]+", value)
        if not matched:
            return ""

        return matched.group(0).replace(",", "")

    def open_production_order_from_stock(e, item_data):
        dialog = ProductionOrderDialog(e.page)

        product_name = item_data.get("name", "")
        product_id = item_data.get("product_id", "")
        expected_qty = ""

        for left, right in item_data.get("rows", []):
            if left in ("예상 발주량", "보충 권장량"):
                expected_qty = _extract_quantity_number(right)
                break

        # 🔥 추가: 생산지시서 상단 기본 정보 자동 입력
        # - DB에 없는 계약번호/LOT/TEL/FAX는 억지로 채우지 않음
        # - 화면에서 이미 가지고 있는 월 범위와 클릭 상품ID만 안전하게 사용
        today = datetime.today()
        today_text = today.strftime("%Y.%m.%d")

        # 🔥 수정: 생산기간은 조회 월 전체가 아니라 실제 즉시 생산 예정 기간으로 입력
        # - 기존: 선택 월 시작일 ~ 종료일 예) 2026.05.01 ~ 2026.05.31
        # - 수정: 지시일자 기준 5일 예) 2026.04.28 ~ 2026.05.02
        # - 즉시 생산 버튼으로 여는 생산지시서이므로 한 달 전체보다 짧은 예정 기간이 자연스러움
        production_start_text = today.strftime("%Y.%m.%d")
        production_end_text = (today + timedelta(days=4)).strftime("%Y.%m.%d")
        period_text = f"{production_start_text} ~ {production_end_text}"

        dialog.instruction_date.value = today_text
        dialog.doc_no.value = f"PRD-{state['year']}{state['month']:02d}-{product_id or 'AUTO'}"
        dialog.request_dept.value = "재고관리"

        # 🔥 생산지시서 첫 번째 품목 행 자동 입력
        if dialog.item_rows:
            first_row = dialog.item_rows[0]

            # 🔥 추가: 대시보드 API에서 내려준 구매단가/판매가를 생산지시서에 바로 주입
            # - 구매단가: ERP.purchase_order_item.purchase_price
            # - 판매가: OPD.product.retail_price 또는 sales_order_item.retail_price
            buy_price = item_data.get("purchase_price") or item_data.get("buy_price") or ""
            sell_price = item_data.get("retail_price") or item_data.get("sell_price") or ""

            first_row["product_name"].value = product_name
            first_row["unit"].value = "ea"
            first_row["qty"].value = expected_qty
            first_row["buy_price"].value = format_number(buy_price) if buy_price else ""
            first_row["sell_price"].value = format_number(sell_price) if sell_price else ""
            first_row["period"].value = period_text

            # 🔥 추가: 모달을 열자마자 구매가계/판매가계까지 자동 계산
            qty = to_int(first_row["qty"].value)
            buy_price_num = to_int(first_row["buy_price"].value)
            sell_price_num = to_int(first_row["sell_price"].value)

            first_row["buy_total"].value = (
                format_number(qty * buy_price_num)
                if qty and buy_price_num
                else ""
            )
            first_row["sell_total"].value = (
                format_number(qty * sell_price_num)
                if qty and sell_price_num
                else ""
            )

        dialog.open()

    # ==============================
    # ☑️ 공통 함수
    # ==============================
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
                    width=92,
                    alignment=ft.Alignment(-1, 0),
                    content=build_text(
                        left_text,
                        size=13,
                        color=TEXT_SECONDARY,
                    ),
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
        # 🔥 수정: 재고 현황 카드 행 정렬 통일
        # - 날짜 / 구분 / 상품명 / 수량(ea) / 금액을 정수 expand 비율로 배치
        # - Flet 0.81.0에서는 expand가 bool 또는 int만 가능하므로 float 사용 금지
        # - 수량(ea)처럼 숫자+단위가 들어간 텍스트도 가운데 정렬
        column_expands = [12, 10, 20, 10, 14]

        return ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    expand=column_expands[i] if i < len(column_expands) else 10,
                    alignment=ft.Alignment(0, 0),
                    content=build_text(
                        item,
                        size=13,
                        color=TEXT_ROW,
                        text_align=ft.TextAlign.CENTER,
                    ),
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

        if title == "입고":
            header_click = lambda e: open_stock_inout_page(e, inout_type="inbound")
        elif title == "출고":
            header_click = lambda e: open_stock_inout_page(e, inout_type="outbound")
        else:
            header_click = None

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
                    build_text(box_data.get("subtitle", ""), size=13, color=TEXT_SECONDARY),
                    ft.Divider(height=1, color=BORDER_COLOR),
                    row_area,
                ],
            ),
        )

    def build_top_stock_item_box(item_data):
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
                            item_data.get("action_text", "즉시 생산"),
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

    def attach_top_stock_item_click(items):
        new_items = []

        for item in items:
            copied = dict(item)
            copied["on_action_click"] = (
                lambda e, item_data=copied: open_production_order_from_stock(e, item_data)
            )
            new_items.append(copied)

        return new_items

    def build_top_stock_box(section_data):
        items = section_data.get("items", [])[:3]

        if items:
            item_area = ft.Container(
                height=238,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                content=ft.Row(
                    spacing=12,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        build_top_stock_item_box(item)
                        for item in items
                    ],
                ),
            )
        else:
            item_area = ft.Container(
                height=238,
                alignment=ft.Alignment(0, 0),
                content=build_text(
                    "매출 기준 재고 데이터가 없습니다.",
                    size=13,
                    color=TEXT_SECONDARY,
                ),
            )

        return build_base_box(
            expand=1,
            height=310,  # 🔥 수정: 왼쪽 총 재고량 카드와 높이 통일
            padding=20,
            border_radius=16,
            content=ft.Column(
                spacing=16,
                controls=[
                    ft.Container(
                        height=24,
                        alignment=ft.Alignment(-1, 0),
                        content=build_text(
                            section_data.get("title", "매출 TOP 3 재고"),
                            size=18,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_700,
                        ),
                    ),
                    item_area,
                ],
            ),
        )

    def build_stock_summary_side_box():
        month_text = state["data"].get(
            "current_month_text",
            f"{state['year']}년 {state['month']}월",
        )
        expiring_stock_text = state["data"].get("expiring_stock_count_text") or "0건"
        expiring_days = int(state["data"].get("expiring_stock_days") or 30)

        return ft.Container(
            width=180,
            height=310,
            bgcolor=CARD_BG,
            border_radius=12,
            padding=20,  # 🔥 수정: 오른쪽 매출 TOP 3 재고 카드와 안쪽 여백 통일
            border=ft.border.all(1, BORDER_COLOR),
            ink=True,
            on_click=open_stock_product_detail_page,
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
                                    "유통기한 임박",
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
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 0.42),
                        content=ft.Text(
                            expiring_stock_text,
                            size=22,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 1),
                        content=ft.Text(
                            f"오늘 기준 {expiring_days}일 이내",
                            size=16,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.RIGHT,
                        ),
                    ),
                ],
            ),
        )

    def reload_dashboard(page=None):
        try:
            dashboard_data = fetch_stock_dashboard(
                year=state["year"],
                month=state["month"],
            )
        except Exception as exc:
            print(f"재고 현황 대시보드 월 이동 조회 실패: {exc}")
            dashboard_data = _empty_dashboard_data(state["year"], state["month"])

        state["data"] = dashboard_data
        state["year"] = int(dashboard_data.get("current_year") or state["year"])
        state["month"] = int(dashboard_data.get("current_month") or state["month"])

        set_stock_dashboard_month_state(state["year"], state["month"])

        section_data = dashboard_data.get(
            "top_stock_section_data",
            {"title": "매출 TOP 3 재고", "items": []},
        )
        section_data = {
            **section_data,
            "items": attach_top_stock_item_click(section_data.get("items", [])),
        }

        month_navigation_holder.content = build_month_navigation()

        status_box_holder.content = ft.Row(
            spacing=16,
            controls=[
                build_status_box(box)
                for box in dashboard_data.get("status_box_data", [])
            ],
        )

        chart_holder.content = build_stock_twin_chart(
            chart_data=dashboard_data.get("chart_data", [])
        )

        top_stock_holder.content = ft.Row(
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.START,  # 🔥 수정: 두 카드의 상단 기준선 통일
            controls=[
                build_stock_summary_side_box(),
                build_top_stock_box(section_data),
            ],
        )

        if page:
            page.update()

    def move_dashboard_month(diff: int, e):
        new_year, new_month = _move_month(state["year"], state["month"], diff)

        state["year"] = new_year
        state["month"] = new_month

        set_stock_dashboard_month_state(new_year, new_month)

        reload_dashboard(e.page)

    def build_month_navigation():
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.CHEVRON_LEFT,
                    icon_size=20,
                    on_click=lambda e: e.page.run_thread(lambda: move_dashboard_month(-1, e)),
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
                    on_click=lambda e: e.page.run_thread(lambda: move_dashboard_month(1, e)),
                ),
            ],
        )

    # ==============================
    # ☑️ 최종 화면
    # ==============================
    page_layout = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,  # 🔥 수정: 화면 배경 흰색 통일
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
                top_stock_holder,
            ],
        ),
    )

    class StockStatusPage(ft.Container):
        def did_mount(self):
            self.page.run_thread(lambda: reload_dashboard(self.page))

    return StockStatusPage(expand=True, content=page_layout)
