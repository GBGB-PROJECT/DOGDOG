import datetime
import flet as ft

from components import common as cm
from components.common.modals.purchase_order import PurchaseOrderDialog
# API client import
# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import (
    count_purchase_orders,
    fetch_purchase_orders,
    fetch_purchase_order_detail,
    fetch_purchase_order_items,
)
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button, build_width_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages, build_pagination_bar
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area





ACTION_BLUE = "#2563EB"
ERROR_RED = "#DC2626"



# =========================================================
# 🔥 생산관리 대시보드 → 발주관리 월 필터 전달용
# - production_view.py에서 발주관리 상자 클릭 시 설정
# - erp_purchase_order_view()가 열릴 때 이 값을 읽어서 자동 조회
# =========================================================
_PURCHASE_ORDER_PREFILTER = {
    "enabled": False,
    "start_date": None,
    "end_date": None,
    "date_type": "contract_date",
}


def set_purchase_order_prefilter(
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    _PURCHASE_ORDER_PREFILTER["enabled"] = True
    _PURCHASE_ORDER_PREFILTER["start_date"] = start_date
    _PURCHASE_ORDER_PREFILTER["end_date"] = end_date
    _PURCHASE_ORDER_PREFILTER["date_type"] = date_type or "contract_date"


def clear_purchase_order_prefilter():
    _PURCHASE_ORDER_PREFILTER["enabled"] = False
    _PURCHASE_ORDER_PREFILTER["start_date"] = None
    _PURCHASE_ORDER_PREFILTER["end_date"] = None
    _PURCHASE_ORDER_PREFILTER["date_type"] = "contract_date"


def _parse_prefilter_date(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=None)

    if isinstance(value, datetime.date):
        return datetime.datetime(value.year, value.month, value.day)

    clean = str(value).strip()[:10]
    try:
        return datetime.datetime.strptime(clean, "%Y-%m-%d")
    except ValueError:
        try:
            return datetime.datetime.strptime(clean.replace(".", "-"), "%Y-%m-%d")
        except ValueError:
            return None


# =========================================================
# 🔥 inbound_view.py와 같은 DatePicker UI 함수
# =========================================================
def format_number(value):
    if value in (None, ""):
        return ""

    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


# =========================================================
# 🔥 테이블 셀
# - 발주관리 테이블 헤더/본문 전체 중앙정렬
# - ft.alignment.* 사용하지 않고 ft.Alignment(0, 0) 사용
# =========================================================
def normalize_cancel_text(value):
    # 🔥 httpx 방식에서는 API가 이미 "정상" / "취소" 문자열로 내려줄 수 있다.
    # - True / "true" / "1" / "y"  → 취소
    # - False / "false" / "0" / "n" → 정상
    # - "정상" / "취소" 문자열은 그대로 유지

    if value in [None, ""]:
        return ""

    if value is True:
        return "취소"

    if value is False:
        return "정상"

    clean = str(value).strip().lower()

    if clean in {"취소", "true", "1", "y", "yes"}:
        return "취소"

    if clean in {"정상", "false", "0", "n", "no"}:
        return "정상"

    return str(value)


def normalize_pay_status(value):
    status = str(value or "").strip()

    if status == "completed":
        return "결제완료"

    if status == "scheduled":
        return "결제예정"

    return status


def purchase_order_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(row.get("no", index)),  # 🔥 API에서 내려준 no 우선 사용
                "purchase_order_id": row.get("purchase_order_id", ""),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "contract_date": row.get("contract_date", ""),
                "inbound_scheduled_date": row.get("inbound_scheduled_date", ""),
                "pay_status": normalize_pay_status(row.get("pay_status", "")),
                "is_purchase_order_cancel": normalize_cancel_text(row.get("is_purchase_order_cancel")),
                "employee_id": row.get("employee_id", ""),
                "item_count": row.get("item_count", ""),
                "final_amount_sum": format_number(row.get("final_amount_sum", "")),
                "last_update": row.get("last_update", ""),
            }
        )

    return rows


def erp_purchase_order_view():
    page_title = "생산관리 > 발주 관리"

    # 🔥 생산관리 메인에서 넘어온 월 필터가 있으면 계약일자 기준으로 바로 조회
    prefilter_state = dict(_PURCHASE_ORDER_PREFILTER)
    clear_purchase_order_prefilter()

    selected_start = {
        "value": _parse_prefilter_date(prefilter_state.get("start_date"))
        if prefilter_state.get("enabled")
        else None
    }
    selected_end = {
        "value": _parse_prefilter_date(prefilter_state.get("end_date"))
        if prefilter_state.get("enabled")
        else None
    }

    search_type_value = {"value": "purchase_order_id"}
    date_type_value = {
        "value": prefilter_state.get("date_type") if prefilter_state.get("enabled") else "contract_date"
    }

    search_type_labels = {
        "purchase_order_id": "발주ID",
        "supplier_name": "거래처명",
        "is_purchase_order_cancel": "발주상태",  # 🔥 수정: 취소여부 → 발주상태
        "pay_status": "결제상태",
        "employee_id": "담당자ID",
    }

    date_type_labels = {
        "contract_date": "계약일자",
        "inbound_scheduled_date": "입고예정일",
    }

    if date_type_value["value"] not in date_type_labels:
        date_type_value["value"] = "contract_date"

    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "purchase_order_id", "label": "발주ID", "width": 80, "align_x": 0},
        {"key": "supplier_name", "label": "거래처명", "width": 130, "align_x": 0},
        {"key": "contract_date", "label": "계약일자", "width": 110, "align_x": 0},
        {"key": "item_count", "label": "품목수", "width": 80, "align_x": 0},
        {"key": "final_amount_sum", "label": "최종금액합계", "width": 140, "align_x": 0},
        {"key": "inbound_scheduled_date", "label": "입고예정일", "width": 110, "align_x": 0},
        {"key": "is_purchase_order_cancel", "label": "발주상태", "width": 90, "align_x": 0},
        {"key": "pay_status", "label": "결제상태", "width": 90, "align_x": 0},
        {"key": "employee_id", "label": "담당자ID", "width": 90, "align_x": 0},
        {"key": "last_update", "label": "최종수정일", "width": 190, "align_x": 0},
    ]

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": "",
        "page_ref": None,
    }

    result_text = ft.Text(
        value="DB 조회 전입니다.",
        size=13,
        color=TEXT_SECONDARY,
    )

    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    # 🔥 추가: 고객 3총사와 동일하게 조건 사용 후에만 보이는 초기화 버튼 자리
    reset_button_holder = ft.Container(visible=False)

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    rows_state = []

    def format_picker_date(value):
        if not value:
            return ""
        return value.strftime("%Y.%m.%d")

    def get_selected_date_range():
        start_date = selected_start["value"].date() if selected_start["value"] else None
        end_date = selected_end["value"].date() if selected_end["value"] else None
        return start_date, end_date

    def refresh_picker_fields():
        start_field_holder.content = date_value_box(
            format_picker_date(selected_start["value"]),
            on_click=open_start_picker,
        )
        start_icon_holder.content = calendar_icon_box(on_click=open_start_picker)

        end_field_holder.content = date_value_box(
            format_picker_date(selected_end["value"]),
            on_click=open_end_picker,
        )
        end_icon_holder.content = calendar_icon_box(on_click=open_end_picker)

    # =========================================================
    # 🔥 DatePicker 선택값은 거래처 관리와 동일하게 +9시간 보정 후 사용
    # =========================================================
    def on_start_date_change(e):
        if e.control.value:
            selected_start["value"] = normalize_datepicker_value(e.control.value)

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        update_reset_button_visibility()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            picked_date = normalize_datepicker_value(e.control.value)

            if selected_start["value"] and picked_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = picked_date

        refresh_picker_fields()
        update_reset_button_visibility()
        e.page.update()

    start_date_picker = ft.DatePicker(
        first_date=datetime.datetime(2000, 1, 1),
        last_date=datetime.datetime(2035, 12, 31),
        on_change=on_start_date_change,
    )

    end_date_picker = ft.DatePicker(
        first_date=datetime.datetime(2000, 1, 1),
        last_date=datetime.datetime(2035, 12, 31),
        on_change=on_end_date_change,
    )

    def open_start_picker(e):
        page = e.page

        if start_date_picker not in page.overlay:
            page.overlay.append(start_date_picker)

        if selected_start["value"]:
            start_date_picker.value = selected_start["value"]

        start_date_picker.open = True
        page.update()

    def open_end_picker(e):
        page = e.page

        if end_date_picker not in page.overlay:
            page.overlay.append(end_date_picker)

        end_date_picker.first_date = selected_start["value"] or datetime.datetime(2000, 1, 1)

        if selected_end["value"]:
            end_date_picker.value = selected_end["value"]
        elif selected_start["value"]:
            end_date_picker.value = selected_start["value"]

        end_date_picker.open = True
        page.update()

    search_field = ft.TextField(
        width=185,
        height=38,
        value="",
        hint_text="검색어",
        hint_style=ft.TextStyle(size=13, color=HINT_TEXT),
        text_size=13,
        border_color=FIELD_BORDER,
        border_radius=6,
        bgcolor=FIELD_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
    )

    search_type_text = ft.Text(
        value=search_type_labels[search_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
    )

    date_type_text = ft.Text(
        value=date_type_labels[date_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
    )

    def update_reset_button_visibility():
        # 🔥 추가: 기본 상태가 아니면 초기화 버튼 표시
        has_filter = (
            selected_start["value"] is not None
            or selected_end["value"] is not None
            or (search_field.value or "").strip() != ""
            or search_type_value["value"] != "purchase_order_id"
            or date_type_value["value"] != "contract_date"
            or (pagination_state["keyword"] or "").strip() != ""
        )
        reset_button_holder.visible = has_filter

    def set_search_type(value: str, page: ft.Page | None = None):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        update_reset_button_visibility()

        if page:
            page.update()
        else:
            search_type_text.update()

    def set_date_type(value: str, page: ft.Page | None = None):
        date_type_value["value"] = value
        date_type_text.value = date_type_labels[value]
        update_reset_button_visibility()

        if page:
            page.update()
        else:
            date_type_text.update()

    def build_search_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                padding=ft.Padding.only(left=2, right=2),
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                ),
            ),
            on_click=lambda e: set_search_type(value, e.page),
        )

    def build_date_type_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                padding=ft.Padding.only(left=2, right=2),
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                ),
            ),
            on_click=lambda e: set_date_type(value, e.page),
        )

    search_type = ft.Container(
        width=150,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=12, right=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                search_type_text,
                ft.PopupMenuButton(
                    tooltip="검색 조건 선택",
                    content=ft.Container(
                        width=24,
                        height=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            ft.Icons.ARROW_DROP_DOWN,
                            size=18,
                            color="#4B5563",
                        ),
                    ),
                    items=[
                        build_search_menu_item(label, value)
                        for value, label in search_type_labels.items()
                    ],
                ),
            ],
        ),
    )

    date_type = ft.Container(
        width=150,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=12, right=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                date_type_text,
                ft.PopupMenuButton(
                    tooltip="날짜 조건 선택",
                    content=ft.Container(
                        width=24,
                        height=24,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            ft.Icons.ARROW_DROP_DOWN,
                            size=18,
                            color="#4B5563",
                        ),
                    ),
                    items=[
                        build_date_type_menu_item(label, value)
                        for value, label in date_type_labels.items()
                    ],
                ),
            ],
        ),
    )

    def open_purchase_order_dialog(e, purchase_order_id):
        try:
            order_data = fetch_purchase_order_detail(purchase_order_id)
            item_rows = fetch_purchase_order_items(purchase_order_id)

            if not order_data:
                result_text.value = f"발주ID {purchase_order_id} 데이터를 찾을 수 없습니다."
                e.page.update()
                return

            dialog = PurchaseOrderDialog(e.page)
            if hasattr(dialog, "set_order_data"):
                dialog.set_order_data(order_data, item_rows)
            dialog.open()

        except Exception as exc:
            result_text.value = f"발주서 조회 실패: {exc}"
            e.page.update()

    def build_table_header():
        return ft.Container(
            bgcolor=TABLE_HEADER_BG,
            padding=ft.Padding.only(
                left=row_padding_x,
                right=row_padding_x,
                top=row_padding_y,
                bottom=row_padding_y,
            ),
            content=ft.Row(
                spacing=row_spacing,
                controls=[
                    *[
                        build_table_cell(
                            col["label"],
                            col["width"],
                            col["align_x"],
                            ft.FontWeight.W_700,
                            TEXT_PRIMARY,
                        )
                        for col in columns
                    ],
                    ft.Container(
                        width=100,
                        alignment=ft.Alignment(0, 0),
                        content=build_text(
                            "상세",
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                ],
            ),
        )

    def build_table_row(row):
        status_color = "#166534" if row.get("pay_status") == "결제완료" else "#B45309"
        cancel_color = ERROR_RED if row.get("is_purchase_order_cancel") == "취소" else TEXT_ROW

        return ft.Container(
            padding=ft.Padding.only(
                left=row_padding_x,
                right=row_padding_x,
                top=row_padding_y,
                bottom=row_padding_y,
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            content=ft.Row(
                spacing=row_spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    *[
                        build_table_cell(
                            row.get(col["key"], ""),
                            col["width"],
                            col["align_x"],
                            ft.FontWeight.W_700
                            if col["key"] in ["pay_status", "is_purchase_order_cancel"]
                            else ft.FontWeight.W_400,
                            status_color
                            if col["key"] == "pay_status"
                            else cancel_color
                            if col["key"] == "is_purchase_order_cancel"
                            else TEXT_ROW,
                        )
                        for col in columns
                    ],
                    ft.Container(
                        width=100,
                        height=34,
                        alignment=ft.Alignment(0, 0),
                        border_radius=6,
                        bgcolor=ACTION_BLUE,
                        on_click=lambda e, po_id=row.get("purchase_order_id"): open_purchase_order_dialog(e, po_id),
                        content=ft.Text(
                            "발주서 보기",
                            size=12,
                            color=ft.Colors.WHITE,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()

        if not filtered_rows:
            table_rows_holder.controls.append(
                ft.Container(
                    height=120,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "일치하는 정보가 없습니다.",
                        size=14,
                        color=TEXT_SECONDARY,
                    ),
                )
            )
            return

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    # =========================================================
    # ☑️ SQLAlchemy ORM: purchase_order + purchase_order_item JOIN 조회
    # =========================================================
    def fetch_total_count(keyword=""):
        start_date, end_date = get_selected_date_range()

        return count_purchase_orders(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            date_type=date_type_value["value"],
        )

    def fetch_purchase_order_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        db_rows = fetch_purchase_orders(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            date_type=date_type_value["value"],
        )

        return purchase_order_db_row_adapter(db_rows, page_no)

    def move_page(page_no: int, page: ft.Page):
        if page_no < 1:
            return

        if page_no > pagination_state["total_pages"]:
            return

        pagination_state["current_page"] = page_no
        pagination_state["page_ref"] = page

        reload_current_page()
        page.update()

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        text_color = ft.Colors.WHITE if selected else "#0F172A"
        bgcolor = "#2563EB" if selected else ft.Colors.TRANSPARENT

        if disabled:
            text_color = "#94A3B8"

        return ft.Container(
            width=40,
            height=40,
            border_radius=10,
            bgcolor=bgcolor,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
            content=ft.Text(
                value=label,
                size=16,
                color=text_color,
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def build_icon_page_button(icon_name, page_no=None, disabled=False):
        icon_color = "#94A3B8" if disabled else "#0F172A"

        return ft.Container(
            width=40,
            height=40,
            border_radius=10,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
            content=ft.Icon(
                icon_name,
                size=20,
                color=icon_color,
            ),
        )

    def refresh_pagination():
        total_pages = pagination_state["total_pages"]
        current_page = pagination_state["current_page"]

        pagination_holder.content = build_pagination_bar(
            current_page,
            total_pages,
            lambda page_no, e: e.page.run_thread(lambda: move_page(page_no, e.page)),
        )

    def update_result_text():
        start_text = format_picker_date(selected_start["value"]) or "미선택"
        end_text = format_picker_date(selected_end["value"]) or "미선택"
        date_label = date_type_labels.get(date_type_value["value"], "계약일자")
        search_label = search_type_labels.get(search_type_value["value"], "발주ID")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"날짜조건: {date_label} / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 {pagination_state['total_count']}건 / "
            f"현재 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]

        total_count = fetch_total_count(keyword=keyword)
        total_pages = calc_total_pages(total_count, PAGE_SIZE)

        if current_page > total_pages:
            current_page = total_pages
            pagination_state["current_page"] = current_page

        fetched_rows = fetch_purchase_order_rows(keyword, current_page)

        rows_state.clear()
        rows_state.extend(fetched_rows)

        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = total_pages

        refresh_table(rows_state)
        refresh_pagination()
        update_result_text()

    def load_rows(page_ref: ft.Page | None = None):
        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref

        reload_current_page()

    def run_search(page_ref: ft.Page | None = None):
        keyword = (search_field.value or "").strip()

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref

        reload_current_page()

    def on_search_click(e):
        pagination_state["keyword"] = (search_field.value or "").strip()
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page

        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    def on_reset_click(e):
        # 🔥 추가: 검색/날짜 조건을 전부 기본값으로 되돌리고 첫 화면 재조회
        selected_start["value"] = None
        selected_end["value"] = None

        search_type_value["value"] = "purchase_order_id"
        search_type_text.value = search_type_labels["purchase_order_id"]
        date_type_value["value"] = "contract_date"
        date_type_text.value = date_type_labels["contract_date"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page

        refresh_picker_fields()
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    search_field.on_submit = lambda e: e.page.run_thread(lambda: on_search_click(e))

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨겨두고, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78, run_async=True)
    update_reset_button_visibility()

    # 🔥 수정: 긴 거래처명/최종수정일이 ...으로 잘리지 않도록 테이블 전체 가로폭 확보
    table_total_width = sum(col["width"] for col in columns) + (row_spacing * (len(columns) - 1)) + (row_padding_x * 2)

    table_content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            build_table_header(),
            # 🔥 수정: 발주관리도 전체 화면이 아니라 데이터 행 영역만 스크롤
            ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    controls=[table_rows_holder],
                ),
            ),
        ],
    )

    table_area = ft.Container(
        expand=True,
        border=ft.border.all(1, TABLE_BORDER),
        border_radius=10,
        bgcolor=CARD_BG,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Row(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(width=table_total_width, content=table_content),
            ],
        ),
    )

    page_layout = build_lookup_page_layout(
        page_title=page_title,
        result_text=result_text,
        table_area=table_area,
        pagination_holder=pagination_holder,
        filter_controls=[
            start_field_holder,
            start_icon_holder,
            ft.Text("~", size=18, color="#374151", weight=ft.FontWeight.W_600),
            end_field_holder,
            end_icon_holder,
            date_type,
            search_type,
            search_field,
            action_button("조회", on_click=on_search_click, run_async=True),
            reset_button_holder,
            # 🔥 미구현 기능 버튼은 사용자 혼란 방지를 위해 숨김
        ],
    )

    class PurchaseOrderPage(ft.Container):
        def did_mount(self):
            def initial_load():
                try:
                    load_rows(self.page)
                except Exception as exc:
                    result_text.value = f"DB 조회 실패: {exc}"
                self.page.update()

            self.page.run_thread(initial_load)

    return PurchaseOrderPage(expand=True, content=page_layout)
