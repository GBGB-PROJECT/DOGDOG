# =========================================================
# 🔥 상품 재고 관리 > 입고/출고 관리 화면
# - 재고 현황 대시보드에서 입고/출고 건수 클릭 시 월 필터 연동
# - httpx 방식 API 호출
# - DatePicker 선택값은 거래처 관리와 동일하게 +9시간 보정 후 사용
# - DatePicker 기간 기준은 화면의 처리일자(event_date) 기준
# =========================================================

import datetime
import flet as ft

from api.erp_httpx_api import count_stock_inouts, fetch_stock_inouts
from components.common.erp_view_widgets import build_text, date_value_box_hint as date_value_box, calendar_icon_box, build_expand_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area





ACTION_BLUE = "#2563EB"



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


def build_button(text, on_click=None, width=82):
    # 🔥 수정: ElevatedButton은 내부 기본 padding 때문에 "초기화"가 세로로 줄바꿈되는 문제가 있음
    # - 다른 조회 화면 버튼들과 동일하게 Container + Text 방식으로 고정
    # - max_lines=1을 줘서 버튼 텍스트가 절대 두 줄로 내려가지 않게 처리
    # 🔥 추가: stock_inout_view는 공통 action_button을 안 쓰므로 여기에도 progress cursor 직접 적용
    button = ft.Container(
        width=width,
        height=38,
        bgcolor=BUTTON_BG,
        border=ft.Border.all(1, BUTTON_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        ink=True,
        content=ft.Text(
            value=text,
            size=13,
            color=BUTTON_TEXT,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

    def handle_click(e):
        if on_click is None or getattr(button, "_erp_clicking", False):
            return

        setattr(button, "_erp_clicking", True)
        button.opacity = 0.62
        try:
            button.update()
        except Exception:
            pass

        try:
            return on_click(e)
        finally:
            button.opacity = 1
            setattr(button, "_erp_clicking", False)
            try:
                button.update()
            except Exception:
                pass

    button.on_click = handle_click
    return button


def erp_stock_inout_view():
    page_title = "상품 재고 관리 > 입고/출고 관리"

    initial_prefilter = _consume_stock_inout_prefilter()

    initial_search_type = initial_prefilter.get("search_type") or "all"
    if initial_search_type not in {
        "all",
        "inout_type",
        "inbound_id",
        "sales_order_id",
        "product",
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

    # 🔥 추가: 다른 조회 화면과 동일하게 조건 사용 후에만 보이는 초기화 버튼
    reset_button_holder = ft.Container(visible=False)

    col_expand = {
        "no": 3,
        "inout_type": 4,
        "base_id": 5,
        "product": 18,
        "quantity": 5,
        "unit_price": 6,
        "amount": 7,
        "event_date": 7,
        "status": 6,
    }

    # =========================================================
    # 🔥 수정: 출고ID → 주문ID
    # - 출고 데이터는 sales_order_id를 기준으로 보여주기 때문에
    #   화면 검색조건도 주문ID가 더 정확함
    # =========================================================
    search_type_labels = {
        "all": "전체",
        "inout_type": "구분",
        "inbound_id": "입고ID",
        "sales_order_id": "주문ID",
        "product": "상품",
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

    # =========================================================
    # 🔥 DatePicker 선택값은 거래처 관리와 동일하게 +9시간 보정 후 사용
    # - Flet DatePicker가 UTC 기준 값으로 들어와 하루 전날로 표시되는 문제 방지
    # - DatePicker 기간 기준은 테이블의 처리일자(event_date) 기준
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

    inout_type_text = ft.Text(
        inout_type_labels[inout_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
    )

    def update_reset_button_visibility():
        # 🔥 추가: 기본값이 아니면 초기화 버튼 표시
        has_filter = (
            selected_start["value"] is not None
            or selected_end["value"] is not None
            or inout_type_value["value"] != "all"
            or search_type_value["value"] != "all"
            or (search_field.value or "").strip() != ""
            or (pagination_state["keyword"] or "").strip() != ""
        )
        reset_button_holder.visible = has_filter

    def set_search_type(value: str):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        update_reset_button_visibility()
        search_type_text.update()

    def set_inout_type(value: str):
        inout_type_value["value"] = value
        inout_type_text.value = inout_type_labels[value]
        update_reset_button_visibility()
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

                    # =========================================================
                    # 🔥 수정: 기준ID → 입고ID/주문ID
                    # - 입고 행: inbound_id
                    # - 출고 행: sales_order_id
                    # =========================================================
                    build_table_cell("입고ID/주문ID", col_expand["base_id"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
                    build_table_cell("상품", col_expand["product"], 0, ft.FontWeight.W_700, TEXT_PRIMARY),
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

        brand = (row.get("brand") or "").strip()
        product_name = (row.get("product_name") or "").strip()
        weight_text = (row.get("weight_text") or "").strip()
        product_id = row.get("product_id")

        product_main = f"{brand} {product_name}".strip() or "-"
        product_meta = []
        if weight_text:
            product_meta.append(weight_text)
        if product_id not in (None, ""):
            product_meta.append(f"#{product_id}")

        if product_meta:
            product_display = f"{product_main} ({' / '.join(product_meta)})"
        else:
            product_display = product_main

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
                    build_table_cell(product_display, col_expand["product"]),
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
        pagination_state["total_pages"] = calc_total_pages(total_count, PAGE_SIZE)
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
            f"기간기준: 처리일자 / "
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
        update_reset_button_visibility()
        e.page.update()

    def on_reset_click(e):
        # 🔥 추가: 검색/날짜/구분 조건을 전부 기본값으로 되돌리고 첫 화면 재조회
        selected_start["value"] = None
        selected_end["value"] = None

        inout_type_value["value"] = "all"
        inout_type_text.value = inout_type_labels["all"]

        search_type_value["value"] = "all"
        search_type_text.value = search_type_labels["all"]

        search_field.value = ""
        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1

        refresh_picker_fields()
        reload_current_page(1)
        update_reset_button_visibility()
        e.page.update()

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨기고, 날짜/구분/검색 조건이 생기면 표시
    reset_button_holder.content = build_button("초기화", on_reset_click, width=82)
    update_reset_button_visibility()

    reload_current_page(1)

    table_area = build_lookup_table_area(build_table_header(), table_rows_holder)

    return build_lookup_page_layout(
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
            inout_type_dropdown,
            search_type_dropdown,
            search_field,
            build_button("조회", on_search_click),
            reset_button_holder,
        ],
    )
