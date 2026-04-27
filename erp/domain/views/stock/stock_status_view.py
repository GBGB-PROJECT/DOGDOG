import flet as ft
from components import common as cm
from components.common.charts.twin_chart import build_stock_twin_chart

# 🔥 재고 현황 대시보드 DB 조회 service
from backend.erp.stock.dashboard_service import fetch_stock_dashboard


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
def _empty_dashboard_data(year=2026, month=4):
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
        "top_stock_section_data": {
            "title": "매출 TOP 3 재고",
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
            initial_data = fetch_stock_dashboard()
    except Exception as exc:
        print(f"재고 현황 대시보드 조회 실패: {exc}")
        initial_data = _empty_dashboard_data(
            saved_year or 2026,
            saved_month or 4,
        )

    state = {
        "year": int(initial_data.get("current_year") or saved_year or 2026),
        "month": int(initial_data.get("current_month") or saved_month or 4),
        "data": initial_data,
    }

    set_stock_dashboard_month_state(state["year"], state["month"])

    month_navigation_holder = ft.Container()
    status_box_holder = ft.Container()
    chart_holder = ft.Container()
    top_stock_holder = ft.Container()

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

    def build_box_header(title: str, right_text: str):
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
                ft.Row(
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
                    build_box_header(box_data.get("title", ""), box_data.get("count_text", "0건")),
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
            product_id = copied.get("product_id")

            # 🔥 현재는 즉시 생산 화면/등록 모달 연결 전
            # - 클릭 이벤트가 죽지 않게 product_id만 로그로 남김
            copied["on_action_click"] = (
                lambda e, pid=product_id: print(f"즉시 생산 클릭 product_id={pid}")
            )
            new_items.append(copied)

        return new_items

    def build_top_stock_box(section_data):
        items = section_data.get("items", [])[:3]

        if items:
            item_area = ft.Row(
                spacing=12,
                controls=[
                    build_top_stock_item_box(item)
                    for item in items
                ],
            )
        else:
            item_area = ft.Container(
                height=210,
                alignment=ft.Alignment(0, 0),
                content=build_text(
                    "매출 기준 재고 데이터가 없습니다.",
                    size=13,
                    color=TEXT_SECONDARY,
                ),
            )

        return build_base_box(
            expand=1,
            padding=20,
            border_radius=16,
            content=ft.Column(
                spacing=16,
                controls=[
                    build_text(
                        section_data.get("title", "매출 TOP 3 재고"),
                        size=18,
                        color=TEXT_PRIMARY,
                        weight=ft.FontWeight.W_700,
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

        return ft.Container(
            width=180,
            height=260,
            bgcolor=CARD_BG,
            border_radius=12,
            padding=12,
            border=ft.border.all(1, BORDER_COLOR),
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment(-1, -1),
                        content=ft.Text(
                            "재고관리",
                            size=16,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                    ),
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(1, 1),
                        content=ft.Text(
                            month_text,
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
                top_stock_holder,
            ],
        ),
    )
