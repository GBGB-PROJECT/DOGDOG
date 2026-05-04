# =========================================================
# 🔥 생산관리 > 불량현황조회 화면
# - 생산관리 메인 대시보드의 "불량 내역 n건 >" 클릭 시 해당 월 불량만 조회
# - ERP.purchase_order_item.defective 기준 불량수량/불량금액 표시
# - 50개씩 페이지네이션
# - DatePicker 선택값은 거래처 관리와 동일하게 +9시간 보정 후 사용
# - DatePicker 기간 검색 기준은 테이블에 보이는 입고완료일(inbound_complete)로 고정
# =========================================================

import datetime
import flet as ft

# 🔥 httpx 방식 API 호출
from api.erp_httpx_api import count_defectives, fetch_defectives
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button, build_expand_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages, build_pagination_bar
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area





ACTION_RED = "#DC2626"



# =========================================================
# 🔥 생산관리 대시보드 → 불량현황 화면 월 필터 전달용
# - production_view.py에서 불량 내역 count 영역을 클릭하면 여기로 필터를 임시 저장
# - defective_view 진입 시 한 번 읽고 바로 비움
# =========================================================
_PRODUCTION_DEFECTIVE_PREFILTER = {"value": None}


def set_production_defective_prefilter(start_date=None, end_date=None, search_type="inbound_complete"):
    _PRODUCTION_DEFECTIVE_PREFILTER["value"] = {
        "start_date": start_date,
        "end_date": end_date,
        "search_type": search_type or "inbound_complete",
    }


def _consume_production_defective_prefilter():
    value = _PRODUCTION_DEFECTIVE_PREFILTER.get("value")
    _PRODUCTION_DEFECTIVE_PREFILTER["value"] = None
    return value or {}


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
# 🔥 공통 텍스트
# =========================================================
# =========================================================
# 🔥 날짜 박스
# =========================================================
# =========================================================
# 🔥 버튼
# =========================================================
# =========================================================
# 🔥 테이블 셀
# =========================================================
# =========================================================
# 🔥 날짜/시간/숫자 포맷
# =========================================================
def format_datetime_text(value):
    if not value:
        return ""
    return str(value)[:19]


def format_date_text_from_value(value):
    if not value:
        return ""
    return str(value)[:10]


def format_number_text(value):
    if value is None or value == "":
        return ""

    try:
        return f"{int(float(value)):,}"
    except (TypeError, ValueError):
        return str(value)


def _build_product_no(product_detail_id, product_id):
    product_detail_id = str(product_detail_id or "").strip()
    product_id = str(product_id or "").strip()

    if product_detail_id and product_id:
        return f"{product_detail_id}-{product_id}"

    return product_detail_id or product_id


# =========================================================
# 🔥 DB row -> 화면 row 변환
# =========================================================
def defective_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "inbound_id": row.get("inbound_id", ""),
                "purchase_order_id": row.get("purchase_order_id", ""),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "inbound_status": row.get("inbound_status", ""),
                "product_id": row.get("product_id", ""),
                "product_detail_id": row.get("product_detail_id", ""),
                "product_no": row.get("product_no") or _build_product_no(row.get("product_detail_id", ""), row.get("product_id", "")),  # 🔥 추가: 상품 상세 정보 관리와 동일한 상품번
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "defective": format_number_text(row.get("defective", "")),
                "purchase_price": format_number_text(row.get("purchase_price", "")),
                "defective_amount": format_number_text(row.get("defective_amount", "")),
                "inbound_scheduled_date": format_date_text_from_value(row.get("inbound_scheduled_date", "")),
                "inbound_start": format_datetime_text(row.get("inbound_start", "")),
                "inbound_complete": format_date_text_from_value(row.get("inbound_complete", "")),
                "employee_id": row.get("employee_id", ""),
                "last_update": format_datetime_text(row.get("last_update", "")),
            }
        )

    return rows


# =========================================================
# 🔥 불량현황조회 화면 본체
# =========================================================

def _format_product_display(row):
    brand = str(row.get("brand") or "").strip()
    product_name = str(row.get("product_name") or "").strip()
    weight_text = str(row.get("weight_text") or "").strip()
    product_id = row.get("product_id", "")

    product_main = f"{brand} {product_name}".strip() or "-"

    product_meta = []
    if weight_text:
        product_meta.append(weight_text)
    if product_id not in [None, ""]:
        product_meta.append(f"#{product_id}")

    if product_meta:
        return f"{product_main} ({' / '.join(product_meta)})"

    return product_main


def erp_defective_view():
    page_title = "생산관리 > 불량현황조회"

    # 🔥 생산관리 메인에서 넘어온 월 필터가 있으면 입고완료일 기준으로 바로 조회
    initial_prefilter = _consume_production_defective_prefilter()
    initial_search_type = initial_prefilter.get("search_type") or "inbound_id"
    if initial_search_type not in {
        "inbound_id",
        "product_no",
        "product_name",
        "supplier_name",
        "inbound_status",
        "employee_id",
    }:
        initial_search_type = "inbound_id"

    rows_state = []

    selected_start = {"value": _parse_prefilter_date(initial_prefilter.get("start_date"))}
    selected_end = {"value": _parse_prefilter_date(initial_prefilter.get("end_date"))}
    search_type_value = {"value": initial_search_type}
    # 🔥 추가: DatePicker 날짜 기준은 검색조건과 분리해서 입고완료일로 고정
    # 🔥 수정: 검색조건 드롭다운에서는 입고예정일/입고시작일/입고완료일 제거
    # - 테이블에 입고시작일 컬럼이 없으므로 화면에서 검증 가능한 입고완료일 기준으로 조회
    date_filter_type_value = {"value": "inbound_complete"}

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": "",
    }

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    result_text = ft.Text("불러오는 중입니다.", size=13, color=TEXT_SECONDARY)
    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    # 🔥 추가: 고객 3총사와 동일하게 조건 사용 후에만 보이는 초기화 버튼 자리
    reset_button_holder = ft.Container(visible=False)

    # =========================================================
    # 🔥 불량현황 컬럼 비율
    # =========================================================
    col_expand = {
        "no": 3,
        "inbound_id": 5,
        "product_no": 6,  # 🔥 추가: 상품 상세 정보 관리의 상품번과 동일한 형식
        "product_name": 14,
        "supplier_name": 8,
        "defective": 5,
        "purchase_price": 6,
        "defective_amount": 7,
        "inbound_complete": 7,
        "inbound_status": 6,
        "employee_id": 5,
        "last_update": 8,
    }

    search_type_labels = {
        "inbound_id": "입고ID",
        "product_no": "상품번",  # 🔥 수정: 상품번과 상품명을 검색조건에서 분리
        "product_name": "상품명",  # 🔥 수정: 상품번과 상품명을 검색조건에서 분리
        "supplier_name": "거래처명",
        "inbound_status": "입고상태",
        "employee_id": "담당자ID",
    }

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
# - DatePicker 기간 검색 기준은 테이블에 보이는 입고완료일(inbound_complete)로 고정
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

    search_type_text = ft.Text(
        search_type_labels[search_type_value["value"]],
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
            or search_type_value["value"] != "inbound_id"
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

    def build_search_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(label, size=13, color=FIELD_TEXT, weight=ft.FontWeight.W_500),
            ),
            on_click=lambda e: set_search_type(value, e.page),
        )

    search_type = ft.Container(
        width=170,
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
                        content=ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=18, color="#4B5563"),
                    ),
                    items=[
                        build_search_menu_item(label, value)
                        for value, label in search_type_labels.items()
                    ],
                ),
            ],
        ),
    )

    search_field = ft.TextField(
        width=185,
        height=38,
        hint_text="검색어",
        hint_style=ft.TextStyle(size=13, color=HINT_TEXT),
        text_size=13,
        border_color=FIELD_BORDER,
        border_radius=6,
        bgcolor=FIELD_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
    )

    def build_table_header():
        return ft.Container(
            bgcolor=TABLE_HEADER_BG,
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            content=ft.Row(
                expand=True,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell("No", col_expand["no"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고ID", col_expand["inbound_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("상품번", col_expand["product_no"], 0, ft.FontWeight.W_700),  # 🔥 추가
                    build_table_cell("상품명", col_expand["product_name"], 0, ft.FontWeight.W_700),
                    build_table_cell("거래처명", col_expand["supplier_name"], 0, ft.FontWeight.W_700),
                    build_table_cell("불량수량", col_expand["defective"], 0, ft.FontWeight.W_700),
                    build_table_cell("구매단가", col_expand["purchase_price"], 0, ft.FontWeight.W_700),
                    build_table_cell("불량손실액", col_expand["defective_amount"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고완료일", col_expand["inbound_complete"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고상태", col_expand["inbound_status"], 0, ft.FontWeight.W_700),
                    build_table_cell("담당자ID", col_expand["employee_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("최종수정일", col_expand["last_update"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        product_display = _format_product_display(row)

        return ft.Container(
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            content=ft.Row(
                expand=True,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell(row.get("no", ""), col_expand["no"], 0),
                    build_table_cell(row.get("inbound_id", ""), col_expand["inbound_id"], 0),
                    build_table_cell(row.get("product_no", ""), col_expand["product_no"], 0),  # 🔥 추가
                    build_table_cell(row.get("product_name", ""), col_expand["product_name"], 0),
                    build_table_cell(row.get("supplier_name", ""), col_expand["supplier_name"], 0),
                    build_table_cell(
                        row.get("defective", ""),
                        col_expand["defective"],
                        0,
                        ft.FontWeight.W_700,
                        ACTION_RED,
                    ),
                    build_table_cell(row.get("purchase_price", ""), col_expand["purchase_price"], 0),
                    build_table_cell(
                        row.get("defective_amount", ""),
                        col_expand["defective_amount"],
                        0,
                        ft.FontWeight.W_700,
                        ACTION_RED,
                    ),
                    build_table_cell(row.get("inbound_complete", ""), col_expand["inbound_complete"], 0),
                    build_table_cell(row.get("inbound_status", ""), col_expand["inbound_status"], 0),
                    build_table_cell(row.get("employee_id", ""), col_expand["employee_id"], 0),
                    build_table_cell(row.get("last_update", ""), col_expand["last_update"], 0),
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
                    content=ft.Text("일치하는 정보가 없습니다.", size=14, color=TEXT_SECONDARY),
                )
            )
            return

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def fetch_total_count(keyword=""):
        start_date, end_date = get_selected_date_range()
        return count_defectives(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
            # 🔥 추가: DatePicker 기간은 항상 입고완료일 기준
            date_filter_type=date_filter_type_value["value"],
        )

    def fetch_page_rows(page_no=1, keyword=""):
        start_date, end_date = get_selected_date_range()
        offset = (page_no - 1) * PAGE_SIZE

        return fetch_defectives(
            search_type=search_type_value["value"],
            keyword=keyword,
            page=page_no,
            size=PAGE_SIZE,
            start_date=start_date,
            end_date=end_date,
            offset=offset,
            limit=PAGE_SIZE,
            # 🔥 추가: DatePicker 기간은 항상 입고완료일 기준
            date_filter_type=date_filter_type_value["value"],
        )

    def refresh_result_text():
        keyword = pagination_state.get("keyword", "")
        start_date, end_date = get_selected_date_range()
        start_text = start_date.strftime("%Y.%m.%d") if start_date else "미선택"
        end_text = end_date.strftime("%Y.%m.%d") if end_date else "미선택"
        search_label = search_type_labels.get(search_type_value["value"], "입고ID")
        keyword_text = keyword if keyword else "없음"

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"날짜기준: 입고완료일 / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 {pagination_state['total_count']:,}건 / "
            f"현재 페이지 {len(rows_state):,}건 / "
            f"{pagination_state['current_page']:,} / {pagination_state['total_pages']:,} 페이지"
        )

    # =========================================================
    # 🔥 수정: 생산입고현황조회와 동일한 페이지네이션 UI로 통일
    # - 작은 검정 버튼(‹ 1 2 3 ›) 방식 제거
    # - 생산입고현황조회처럼 파란색 선택 버튼 + < > 표기 사용
    # =========================================================
    def move_page(page_no: int, page: ft.Page):
        if page_no < 1 or page_no > pagination_state["total_pages"]:
            return

        pagination_state["current_page"] = page_no
        load_page(page_no)
        page.update()

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        return ft.Container(
            width=40,
            height=40,
            border_radius=10,
            bgcolor="#2563EB" if selected else ft.Colors.TRANSPARENT,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
            content=ft.Text(
                str(label),
                size=16,
                color=ft.Colors.WHITE if selected else "#0F172A",
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
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

    def load_page(page_no=1, page=None):
        try:
            keyword = pagination_state.get("keyword", "")
            total_count = fetch_total_count(keyword)
            total_pages = calc_total_pages(total_count, PAGE_SIZE)

            if page_no > total_pages:
                page_no = total_pages
            if page_no < 1:
                page_no = 1

            db_rows = fetch_page_rows(page_no, keyword)
            rows_state.clear()
            rows_state.extend(defective_db_row_adapter(db_rows, page_no))

            pagination_state["current_page"] = page_no
            pagination_state["total_count"] = total_count
            pagination_state["total_pages"] = total_pages

            refresh_table(rows_state)
            refresh_result_text()
            refresh_pagination()

        except Exception as exc:
            rows_state.clear()
            table_rows_holder.controls.clear()
            table_rows_holder.controls.append(
                ft.Container(
                    height=120,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        f"불량현황조회 실패: {exc}",
                        size=14,
                        color=ACTION_RED,
                    ),
                )
            )
            result_text.value = "불량현황조회 중 오류가 발생했습니다."
            pagination_holder.content = None

        if page:
            page.update()

    def on_search(e):
        pagination_state["keyword"] = (search_field.value or "").strip()
        load_page(1, e.page)
        update_reset_button_visibility()
        e.page.update()

    def on_reset(e):
        # 🔥 수정: 고객 3총사와 동일하게 모든 조건을 기본값으로 복구
        search_field.value = ""
        selected_start["value"] = None
        selected_end["value"] = None
        search_type_value["value"] = "inbound_id"
        search_type_text.value = search_type_labels["inbound_id"]
        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        refresh_picker_fields()
        load_page(1, e.page)
        update_reset_button_visibility()
        e.page.update()

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨겨두고, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset, width=78, run_async=True)
    update_reset_button_visibility()

    table_area = build_lookup_table_area(build_table_header(), table_rows_holder)

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
            search_type,
            search_field,
            action_button("조회", on_click=on_search, run_async=True),
            reset_button_holder,
        ],
    )

    class DefectivePage(ft.Container):
        def did_mount(self):
            self.page.run_thread(lambda: load_page(1, self.page))

    return DefectivePage(expand=True, content=page_layout)
