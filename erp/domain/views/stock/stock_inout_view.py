# =========================================================
# 🔥 상품 재고 관리 > 입고/출고 관리 화면
# - 재고 현황 대시보드에서 입고/출고 건수 클릭 시 월 필터 연동
# - requests 방식 API 호출
# =========================================================

import math
import datetime
import flet as ft

from api.erp_httpx_api import count_stock_inouts, fetch_stock_inouts


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
# 🔥 재고 현황 대시보드 → 입고/출고 관리 화면 필터 전달용
# =========================================================
_STOCK_INOUT_PREFILTER = {"value": None}


def set_stock_inout_prefilter(
    start_date=None,
    end_date=None,
    inout_type="all",
    search_type="all",
    keyword="",
):
    _STOCK_INOUT_PREFILTER["value"] = {
        "start_date": start_date,
        "end_date": end_date,
        "inout_type": inout_type or "all",
        "search_type": search_type or "all",
        "keyword": keyword or "",
    }


def _consume_stock_inout_prefilter():
    value = _STOCK_INOUT_PREFILTER.get("value")
    _STOCK_INOUT_PREFILTER["value"] = None
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


def build_text(
    value,
    size=12,
    color=TEXT_PRIMARY,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.LEFT,
    max_lines=1,
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


def date_value_box(text, on_click=None):
    return ft.Container(
        width=138,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=14, right=14),
        alignment=ft.Alignment(-1, 0),
        ink=True if on_click else False,
        on_click=on_click,
        content=ft.Text(
            value=text or "",
            size=13,
            color=FIELD_TEXT if text else HINT_TEXT,
            weight=ft.FontWeight.W_500,
        ),
    )


def calendar_icon_box(on_click=None):
    return ft.Container(
        width=38,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        ink=True if on_click else False,
        on_click=on_click,
        content=ft.Icon(ft.Icons.CALENDAR_MONTH, size=18, color="#4B5563"),
    )


def build_button(text, on_click=None, width=82):
    return ft.ElevatedButton(
        text,
        width=width,
        height=38,
        style=ft.ButtonStyle(
            bgcolor=BUTTON_BG,
            color=BUTTON_TEXT,
            shape=ft.RoundedRectangleBorder(radius=6),
            side=ft.BorderSide(1, BUTTON_BORDER),
            elevation=0,
        ),
        on_click=on_click,
    )


def erp_stock_inout_view():
    page_title = "상품 재고 관리 > 입고/출고 관리"

    initial_prefilter = _consume_stock_inout_prefilter()

    initial_search_type = initial_prefilter.get("search_type") or "all"
    if initial_search_type not in {
        "all",
        "inout_type",
        "inbound_id",
        "sales_order_id",
        "product_id",
        "brand",
        "product_name",
        "status",
    }:
        initial_search_type = "all"

    initial_inout_type = initial_prefilter.get("inout_type") or "all"
    if initial_inout_type not in {"all", "inbound", "outbound"}:
        initial_inout_type = "all"

    selected_start = {"value": _parse_prefilter_date(initial_prefilter.get("start_date"))}
    selected_end = {"value": _parse_prefilter_date(initial_prefilter.get("end_date"))}
    search_type_value = {"value": initial_search_type}
    inout_type_value = {"value": initial_inout_type}

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": initial_prefilter.get("keyword") or "",
    }

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    result_text = ft.Text("불러오는 중입니다.", size=13, color=TEXT_SECONDARY)
    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    col_expand = {
        "no": 3,
        "inout_type": 4,
        "base_id": 5,
        "product_id": 5,
        "brand": 6,
        "product_name": 12,
        "quantity": 5,
        "unit_price": 6,
        "amount": 7,
        "event_date": 7,
        "status": 6,
    }

    search_type_labels = {
        "all": "전체",
        "inout_type": "구분",
        "inbound_id": "입고ID",
        "sales_order_id": "출고ID",
        "product_id": "상품ID",
        "brand": "브랜드",
        "product_name": "상품명",
        "status": "상태",
    }

    inout_type_labels = {
        "all": "전체",
        "inbound": "입고",
        "outbound": "출고",
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

    inout_type_text = ft.Text(
        inout_type_labels[inout_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
    )

    def set_search_type(value: str):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        search_type_text.update()

    def set_inout_type(value: str):
        inout_type_value["value"] = value
        inout_type_text.value = inout_type_labels[value]
        inout_type_text.update()

    def build_menu_item(label: str, value: str, setter):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(label, size=13, color=FIELD_TEXT, weight=ft.FontWeight.W_500),
            ),
            on_click=lambda e: setter(value),
        )

    def build_dropdown(width, text_control, items):
        return ft.Container(
            width=width,
            height=38,
            bgcolor=FIELD_BG,
            border=ft.Border.all(1, FIELD_BORDER),
            border_radius=6,
            padding=ft.Padding.only(left=12, right=4),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    text_control,
                    ft.PopupMenuButton(
                        tooltip="조건 선택",
                        content=ft.Container(
                            width=24,
                            height=24,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=18, color="#4B5563"),
                        ),
                        items=items,
                    ),
                ],
            ),
        )

    inout_type_dropdown = build_dropdown(
        110,
        inout_type_text,
        [
            build_menu_item(label, value, set_inout_type)
            for value, label in inout_type_labels.items()
        ],
    )

    search_type_dropdown = build_dropdown(
        150,
        search_type_text,
        [
            build_menu_item(label, value, set_search_type)
            for value, label in search_type_labels.items()
        ],
    )

    search_field = ft.TextField(
        width=185,
        height=38,
        value=pagination_state["keyword"],
        hint_text="검색어",
        hint_style=ft.TextStyle(size=13, color=HINT_TEXT),
        text_size=13,
        border_color=FIELD_BORDER,
        border_radius=6,
        bgcolor=FIELD_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
    )

    def build_table_cell(text, expand, align=0, weight=ft.FontWeight.W_400, color=TEXT_ROW):
        return ft.Container(
            expand=expand,
            alignment=ft.Alignment(align, 0),
            content=ft.Text(
                value=str(text if text is not None else ""),
                size=12,
                color=color,
                weight=weight,
                text_align=ft.TextAlign.CENTER if align == 0 else ft.TextAlign.LEFT,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
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
                    build_table_cell("No", col_expand["no"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("구분", col_expand["inout_type"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("기준ID", col_expand["base_id"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("상품ID", col_expand["product_id"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("브랜드", col_expand["brand"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("상품명", col_expand["product_name"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("수량", col_expand["quantity"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("단가", col_expand["unit_price"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("금액", col_expand["amount"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("처리일자", col_expand["event_date"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("상태", col_expand["status"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                ],
            ),
        )

    def build_table_row(row, index):
        status_color = ACTION_BLUE if row.get("inout_type") == "입고" else "#16A34A"

        return ft.Container(
            height=54,
            padding=ft.Padding.only(left=14, right=14),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            content=ft.Row(
                expand=True,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell(index, col_expand["no"]),
                    build_table_cell(row.get("inout_type"), col_expand["inout_type"], 0, ft.FontWeight.W_700, status_color),
                    build_table_cell(row.get("base_id"), col_expand["base_id"]),
                    build_table_cell(row.get("product_id"), col_expand["product_id"]),
                    build_table_cell(row.get("brand"), col_expand["brand"]),
                    build_table_cell(row.get("product_name"), col_expand["product_name"]),
                    build_table_cell(row.get("quantity_text"), col_expand["quantity"]),
                    build_table_cell(row.get("unit_price_text"), col_expand["unit_price"]),
                    build_table_cell(row.get("amount_text"), col_expand["amount"]),
                    build_table_cell(row.get("event_date"), col_expand["event_date"]),
                    build_table_cell(row.get("status"), col_expand["status"], 0, ft.FontWeight.W_700, status_color),
                ],
            ),
        )

    def build_empty_table_message():
        return ft.Container(
            height=300,
            bgcolor=CARD_BG,
            alignment=ft.Alignment(0, 0),
            content=build_text("일치하는 입고/출고 내역이 없습니다.", size=14, color=TEXT_SECONDARY),
        )

    def load_rows(page_no=1):
        start_date, end_date = get_selected_date_range()
        keyword = (search_field.value or "").strip()
        offset = (page_no - 1) * PAGE_SIZE

        total_count = count_stock_inouts(
            search_type=search_type_value["value"],
            keyword=keyword,
            inout_type=inout_type_value["value"],
            start_date=start_date,
            end_date=end_date,
        )

        rows = fetch_stock_inouts(
            search_type=search_type_value["value"],
            keyword=keyword,
            inout_type=inout_type_value["value"],
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        pagination_state["current_page"] = page_no
        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = max(math.ceil(total_count / PAGE_SIZE), 1)
        pagination_state["keyword"] = keyword

        return rows

    def refresh_result_text():
        start_date, end_date = get_selected_date_range()
        start_text = start_date.strftime("%Y.%m.%d") if start_date else "전체"
        end_text = end_date.strftime("%Y.%m.%d") if end_date else "전체"
        condition_text = search_type_labels.get(search_type_value["value"], "전체")
        inout_text = inout_type_labels.get(inout_type_value["value"], "전체")
        keyword = pagination_state["keyword"] or "없음"

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"구분: {inout_text} / "
            f"검색조건: {condition_text} / 검색어: {keyword} / "
            f"전체 {pagination_state['total_count']:,}건 / "
            f"현재 페이지 {len(table_rows_holder.controls)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def move_page(page_no: int, page: ft.Page):
        if page_no < 1 or page_no > pagination_state["total_pages"]:
            return

        reload_current_page(page_no)
        page.update()

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        return ft.Container(
            width=36,
            height=36,
            border_radius=9,
            bgcolor="#2563EB" if selected else ft.Colors.TRANSPARENT,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: move_page(page_no, e.page),
            content=ft.Text(
                label,
                size=14,
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

        page_controls = [
            build_page_button("<", current_page - 1, disabled=(current_page == 1))
        ]

        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)

        for page_no in range(start_page, end_page + 1):
            page_controls.append(
                build_page_button(str(page_no), page_no, selected=(page_no == current_page))
            )

        page_controls.append(
            build_page_button(">", current_page + 1, disabled=(current_page == total_pages))
        )

        pagination_holder.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=6,
            controls=page_controls,
        )

    def reload_current_page(page_no=None):
        target_page = page_no or pagination_state["current_page"]
        rows = load_rows(target_page)

        table_rows_holder.controls = [
            build_table_row(row, ((pagination_state["current_page"] - 1) * PAGE_SIZE) + idx + 1)
            for idx, row in enumerate(rows)
        ]

        if not rows:
            table_rows_holder.controls = [build_empty_table_message()]

        refresh_result_text()
        refresh_pagination()

    def on_search_click(e):
        reload_current_page(1)
        e.page.update()

    def on_reset_click(e):
        selected_start["value"] = None
        selected_end["value"] = None
        search_field.value = ""
        set_search_type("all")
        set_inout_type("all")
        refresh_picker_fields()
        reload_current_page(1)
        e.page.update()

    refresh_picker_fields()
    reload_current_page(1)

    return ft.Container(
        expand=True,
        bgcolor="#EDEDED",
        padding=20,
        content=ft.Column(
            spacing=18,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        start_field_holder,
                        start_icon_holder,
                        ft.Text("~", size=18, color="#111827", weight=ft.FontWeight.W_700),
                        end_field_holder,
                        end_icon_holder,
                        inout_type_dropdown,
                        search_type_dropdown,
                        search_field,
                        build_button("조회", on_search_click),
                        build_button("초기화", on_reset_click),
                    ],
                ),
                build_text(
                    page_title,
                    size=22,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),
                result_text,
                ft.Container(
                    bgcolor=CARD_BG,
                    border_radius=12,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Column(
                        spacing=0,
                        controls=[
                            build_table_header(),
                            table_rows_holder,
                        ],
                    ),
                ),
                pagination_holder,
            ],
        ),
    )
