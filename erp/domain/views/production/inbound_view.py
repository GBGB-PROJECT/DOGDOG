# =========================================================
# 🔥 생산입고 > 입고 현황 조회 화면
# - backend/erp/production/inbound_service.py 직접 호출
# - ERP.inbound + ERP.inbound_status + ERP.stock JOIN 결과 표시
# - 입고 상태는 숫자 ID가 아니라 상태명 문자로 표시
# - 생산관리 대시보드 카드와 이어지도록 상품명/입고수량/입고금액 표시
# - 50개씩 페이지네이션
# - DatePicker 선택값은 별도 시간 보정 없이 그대로 사용
# =========================================================

import math
import datetime
import flet as ft

from backend.erp.production.inbound_service import count_inbounds, fetch_inbounds


FIELD_BG = ft.Colors.WHITE
FIELD_BORDER = "#D1D5DB"
FIELD_TEXT = "#222222"
HINT_TEXT = "#9CA3AF"

BUTTON_BG = "#F3F4F6"
BUTTON_TEXT = "#374151"
BUTTON_BORDER = "#D1D5DB"

CARD_BG = ft.Colors.WHITE
TABLE_HEADER_BG = "#F9FAFB"
TABLE_BORDER = "#E5E7EB"

TEXT_PRIMARY = "#111827"
TEXT_SECONDARY = "#6B7280"
TEXT_ROW = "#374151"
ACTION_BLUE = "#2563EB"

PAGE_SIZE = 50


# =========================================================
# 🔥 생산관리 대시보드 → 생산입고 화면 월 필터 전달용
# - production_view.py에서 count 영역을 클릭하면 여기로 필터를 임시 저장
# - inbound_view 진입 시 한 번 읽고 바로 비움
# =========================================================
_PRODUCTION_INBOUND_PREFILTER = {"value": None}


def set_production_inbound_prefilter(start_date=None, end_date=None, search_type="inbound_complete"):
    _PRODUCTION_INBOUND_PREFILTER["value"] = {
        "start_date": start_date,
        "end_date": end_date,
        "search_type": search_type or "inbound_complete",
    }


def _consume_production_inbound_prefilter():
    value = _PRODUCTION_INBOUND_PREFILTER.get("value")
    _PRODUCTION_INBOUND_PREFILTER["value"] = None
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
def build_text(value, size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_400):
    return ft.Text(
        value=str(value or ""),
        size=size,
        color=color,
        weight=weight,
        max_lines=1,
        overflow=ft.TextOverflow.ELLIPSIS,
    )


# =========================================================
# 🔥 날짜 박스
# =========================================================
def date_value_box(text, on_click=None):
    return ft.Container(
        width=138,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=14, right=14),
        alignment=ft.Alignment(-1, 0),
        on_click=on_click,
        content=ft.Text(text, size=13, color=FIELD_TEXT, weight=ft.FontWeight.W_500),
    )


def calendar_icon_box(on_click=None):
    return ft.Container(
        width=38,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, size=18, color="#4B5563"),
    )


# =========================================================
# 🔥 버튼
# =========================================================
def action_button(text, on_click=None, width=78):
    return ft.Container(
        width=width,
        height=38,
        bgcolor=BUTTON_BG,
        border=ft.Border.all(1, BUTTON_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Text(text, size=13, color=BUTTON_TEXT, weight=ft.FontWeight.W_500),
    )


# =========================================================
# 🔥 테이블 셀
# =========================================================
def build_table_cell(text, expand, align_x=0, weight=ft.FontWeight.W_400, color=TEXT_ROW):
    return ft.Container(
        expand=expand,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(text, size=12, color=color, weight=weight),
    )


# =========================================================
# 🔥 날짜/시간 포맷
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
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


# =========================================================
# 🔥 DB row -> 화면 row 변환
# =========================================================
def inbound_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "inbound_id": row.get("inbound_id", ""),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "inbound_status": row.get("inbound_status", ""),  # 🔥 상태명 문자
                "product_id": row.get("product_id", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "save_stock": format_number_text(row.get("save_stock", "")),
                "purchase_price": format_number_text(row.get("purchase_price", "")),
                "inbound_amount": format_number_text(row.get("inbound_amount", "")),
                "expiration_date": format_date_text_from_value(row.get("expiration_date", "")),
                "inbound_scheduled_date": format_date_text_from_value(row.get("inbound_scheduled_date", "")),
                "inbound_start": format_datetime_text(row.get("inbound_start", "")),
                # 🔥 입고완료일은 시간 없이 날짜만 표시
                "inbound_complete": format_date_text_from_value(row.get("inbound_complete", "")),
                "employee_id": row.get("employee_id", ""),
                "last_update": format_datetime_text(row.get("last_update", "")),
            }
        )

    return rows


# =========================================================
# 🔥 생산입고현황조회 화면 본체
# =========================================================
def erp_inbound_view():
    page_title = "생산관리 > 생산입고현황조회"

    # 🔥 생산관리 메인에서 넘어온 월 필터가 있으면 입고완료일 기준으로 바로 조회
    initial_prefilter = _consume_production_inbound_prefilter()
    initial_search_type = initial_prefilter.get("search_type") or "inbound_id"
    if initial_search_type not in {
        "inbound_id",
        "supplier_id",
        "supplier_name",
        "inbound_status",
        "product_id",
        "brand",
        "product_name",
        "employee_id",
        "expiration_date",
        "inbound_scheduled_date",
        "inbound_start",
        "inbound_complete",
    }:
        initial_search_type = "inbound_id"

    rows_state = []

    selected_start = {"value": _parse_prefilter_date(initial_prefilter.get("start_date"))}
    selected_end = {"value": _parse_prefilter_date(initial_prefilter.get("end_date"))}
    search_type_value = {"value": initial_search_type}

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

    # =========================================================
    # 🔥 입고 현황 컬럼 비율
    # =========================================================
    col_expand = {
        "no": 3,
        # 🔥 컬럼 순서 변경: No 다음 상품ID, 그 다음 입고ID
        "product_id": 5,
        "inbound_id": 5,
        "supplier_name": 7,
        "inbound_status": 6,
        "brand": 7,
        "product_name": 10,
        "save_stock": 5,
        "purchase_price": 6,
        "inbound_amount": 7,
        "expiration_date": 7,
        "inbound_complete": 7,
        "employee_id": 5,
        "last_update": 8,
    }

    search_type_labels = {
        "inbound_id": "입고ID",
        "supplier_id": "거래처ID",
        "supplier_name": "거래처명",
        "inbound_status": "입고상태",
        "product_id": "상품ID",
        "brand": "브랜드",
        "product_name": "상품명",
        "employee_id": "담당자ID",
        "expiration_date": "유통기한",
        "inbound_scheduled_date": "입고예정일",
        "inbound_start": "입고시작일",
        "inbound_complete": "입고완료일",
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
    # 🔥 DatePicker 선택값은 시간 보정 없이 그대로 사용
    # =========================================================
    def on_start_date_change(e):
        if e.control.value:
            selected_start["value"] = e.control.value.replace(tzinfo=None)

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            picked_date = e.control.value.replace(tzinfo=None)

            if selected_start["value"] and picked_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = picked_date

        refresh_picker_fields()
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

    def set_search_type(value: str):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        search_type_text.update()

    def build_search_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(label, size=13, color=FIELD_TEXT, weight=ft.FontWeight.W_500),
            ),
            on_click=lambda e: set_search_type(value),
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
                    build_table_cell("상품ID", col_expand["product_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고ID", col_expand["inbound_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("거래처명", col_expand["supplier_name"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고상태", col_expand["inbound_status"], 0, ft.FontWeight.W_700),
                    build_table_cell("브랜드", col_expand["brand"], 0, ft.FontWeight.W_700),
                    build_table_cell("상품명", col_expand["product_name"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고수량", col_expand["save_stock"], 0, ft.FontWeight.W_700),
                    build_table_cell("구매단가", col_expand["purchase_price"], 0, ft.FontWeight.W_700),
                    # 🔥 입고금액은 단가가 아니라 입고수량 * 구매단가의 총액이라 헤더명을 명확히 변경
                    build_table_cell("입고총액", col_expand["inbound_amount"], 0, ft.FontWeight.W_700),
                    build_table_cell("유통기한", col_expand["expiration_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("입고완료일", col_expand["inbound_complete"], 0, ft.FontWeight.W_700),
                    build_table_cell("담당자ID", col_expand["employee_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("최종수정일", col_expand["last_update"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
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
                    build_table_cell(row.get("product_id", ""), col_expand["product_id"], 0),
                    build_table_cell(row.get("inbound_id", ""), col_expand["inbound_id"], 0),
                    build_table_cell(row.get("supplier_name", ""), col_expand["supplier_name"], 0),
                    build_table_cell(
                        row.get("inbound_status", ""),
                        col_expand["inbound_status"],
                        0,
                        ft.FontWeight.W_700,
                        ACTION_BLUE,
                    ),
                    build_table_cell(row.get("brand", ""), col_expand["brand"], 0),
                    build_table_cell(row.get("product_name", ""), col_expand["product_name"], 0),
                    build_table_cell(row.get("save_stock", ""), col_expand["save_stock"], 0),
                    build_table_cell(row.get("purchase_price", ""), col_expand["purchase_price"], 0),
                    build_table_cell(row.get("inbound_amount", ""), col_expand["inbound_amount"], 0),
                    build_table_cell(row.get("expiration_date", ""), col_expand["expiration_date"], 0),
                    build_table_cell(row.get("inbound_complete", ""), col_expand["inbound_complete"], 0),
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
        return count_inbounds(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )

    def fetch_inbound_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        db_rows = fetch_inbounds(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return inbound_db_row_adapter(db_rows, page_no)

    def move_page(page_no: int, page: ft.Page):
        if page_no < 1 or page_no > pagination_state["total_pages"]:
            return

        pagination_state["current_page"] = page_no
        reload_current_page()
        page.update()

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        return ft.Container(
            width=40,
            height=40,
            border_radius=10,
            bgcolor="#2563EB" if selected else ft.Colors.TRANSPARENT,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: move_page(page_no, e.page),
            content=ft.Text(
                label,
                size=16,
                color=ft.Colors.WHITE if selected else "#0F172A",
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
            ),
        )

    def refresh_pagination():
        total_pages = pagination_state["total_pages"]
        current_page = pagination_state["current_page"]

        if total_pages <= 1:
            pagination_holder.content = None
            return

        page_controls = []
        page_controls.append(build_page_button("<", current_page - 1, disabled=(current_page == 1)))

        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)

        for page_no in range(start_page, end_page + 1):
            page_controls.append(
                build_page_button(
                    str(page_no),
                    page_no,
                    selected=(page_no == current_page),
                )
            )

        page_controls.append(build_page_button(">", current_page + 1, disabled=(current_page == total_pages)))

        pagination_holder.content = ft.Container(
            padding=ft.Padding.only(top=14, bottom=6),
            alignment=ft.Alignment(0, 0),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=page_controls,
            ),
        )

    def update_result_text():
        start_text = format_picker_date(selected_start["value"]) or "미선택"
        end_text = format_picker_date(selected_end["value"]) or "미선택"
        search_label = search_type_labels.get(search_type_value["value"], "입고ID")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 {pagination_state['total_count']}건 / "
            f"현재 페이지 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]

        total_count = fetch_total_count(keyword=keyword)
        total_pages = max(1, math.ceil(total_count / PAGE_SIZE))

        if current_page > total_pages:
            current_page = total_pages
            pagination_state["current_page"] = current_page

        rows = fetch_inbound_rows(keyword=keyword, page_no=current_page)

        rows_state.clear()
        rows_state.extend(rows)

        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = total_pages

        refresh_table(rows_state)
        refresh_pagination()
        update_result_text()

    def on_search_click(e):
        pagination_state["keyword"] = (search_field.value or "").strip()
        pagination_state["current_page"] = 1
        reload_current_page()
        e.page.update()

    refresh_picker_fields()

    pagination_state["keyword"] = ""
    pagination_state["current_page"] = 1
    reload_current_page()

    return ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor="#F3F4F6",
                padding=ft.Padding.only(left=24, right=24, top=18, bottom=14),
                content=ft.Row(
                    wrap=True,
                    spacing=12,
                    run_spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        start_field_holder,
                        start_icon_holder,
                        ft.Text("~", size=18, color="#374151", weight=ft.FontWeight.W_600),
                        end_field_holder,
                        end_icon_holder,
                        search_type,
                        search_field,
                        action_button("조회", on_click=on_search_click),
                        action_button("인쇄"),
                        action_button("다운로드", width=92),
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                bgcolor="#F5F5F5",
                padding=ft.Padding.only(left=24, right=24, top=26, bottom=18),
                content=ft.Column(
                    expand=True,
                    spacing=18,
                    controls=[
                        ft.Text(page_title, size=22, weight=ft.FontWeight.W_700, color=TEXT_PRIMARY),
                        result_text,
                        ft.Container(
                            expand=True,
                            bgcolor=CARD_BG,
                            border_radius=10,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                            content=ft.Column(
                                expand=True,
                                spacing=0,
                                controls=[
                                    build_table_header(),
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
                            ),
                        ),
                        pagination_holder,
                    ],
                ),
            ),
        ],
    )
