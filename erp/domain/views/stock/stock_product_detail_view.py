import datetime
import flet as ft

from components import common as cm
# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_stocks, fetch_stocks
from components.common.erp_view_widgets import build_text, date_value_box_center as date_value_box, calendar_icon_box, action_button, build_width_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area








# =========================================================
# 🔥 재고 현황 대시보드 → 상품별 재고 상세 화면 월 필터 전달용
# - 총 재고량 카드 클릭 시 해당 월 입고 기준 재고만 조회
# =========================================================
_STOCK_PRODUCT_DETAIL_PREFILTER = {"value": None}


def set_stock_product_detail_prefilter(
    start_date=None,
    end_date=None,
    date_filter_type="inbound_date",
    search_type="product_id",
    keyword="",
):
    _STOCK_PRODUCT_DETAIL_PREFILTER["value"] = {
        "start_date": start_date,
        "end_date": end_date,
        "date_filter_type": date_filter_type or "inbound_date",
        "search_type": search_type or "product_id",
        "keyword": keyword or "",
    }


def _consume_stock_product_detail_prefilter():
    value = _STOCK_PRODUCT_DETAIL_PREFILTER.get("value")
    _STOCK_PRODUCT_DETAIL_PREFILTER["value"] = None
    return value or {}


def _parse_prefilter_date(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    clean = str(value).strip()[:10]
    try:
        return datetime.datetime.strptime(clean, "%Y-%m-%d").date()
    except ValueError:
        try:
            return datetime.datetime.strptime(clean.replace(".", "-"), "%Y-%m-%d").date()
        except ValueError:
            return None


# =========================================================
# 🔥 상품별 재고 상세 View
# - stock이 주인공인 화면
# - 중량/수량/판매가/샘플/활성/상세ID/발주ID 제거
# - 브랜드 뒤에 stock 관련 컬럼 배치
# =========================================================


def _format_number(value):
    if value in [None, ""]:
        return ""

    try:
        if isinstance(value, bool):
            return str(value)
        return f"{int(value):,}"
    except Exception:
        return str(value)


def _format_date_only(value):
    # 🔥 API/DB에서 datetime 문자열이 와도 화면에는 날짜만 표시
    if value in [None, ""]:
        return ""

    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d")

    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")

    text = str(value).strip()
    if not text:
        return ""

    # 예: 2026-05-18 00:00:00 / 2026-05-18T00:00:00 -> 2026-05-18
    if len(text) >= 10:
        return text[:10]

    return text



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


def stock_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "product_id": row.get("product_id", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "weight_text": row.get("weight_text", ""),
                "product": _format_product_display(row),
                "expiration_date": _format_date_only(row.get("expiration_date", "")),
                "inbound_id": row.get("inbound_id", ""),
                "inbound_date": _format_date_only(row.get("inbound_date", "")),
                "inbound_status": row.get("inbound_status", ""),
                "save_stock": _format_number(row.get("save_stock", "")),
                "sale_stock": _format_number(row.get("sale_stock", "")),
                "stock_available": _format_number(row.get("stock_available", "")),
                "scrap_stock": _format_number(row.get("scrap_stock", "")),
                "last_update": _format_date_only(row.get("last_update", "")),
            }
        )

    return rows


def normalize_to_date(value):
    if not value:
        return None

    # 🔥 수정: 생산관리 DatePicker와 동일하게 +9시간 보정 후 날짜만 사용
    # - Flet DatePicker가 UTC 기준 값으로 들어와 하루 전날로 표시되는 문제 방지
    if isinstance(value, datetime.datetime):
        return normalize_datepicker_date(value)

    if isinstance(value, datetime.date):
        return value

    return None


def erp_stock_product_detail_view():
    page_title = "재고관리 > 상품별 재고 상세"

    initial_prefilter = _consume_stock_product_detail_prefilter()

    # 🔥 수정: 검색조건과 DatePicker 날짜기준을 분리
    # - 입력 검색조건: 텍스트/숫자로 검색할 컬럼
    # - 날짜기준: DatePicker가 조회할 날짜 컬럼(유통기한/입고일자)
    initial_search_type = initial_prefilter.get("search_type") or "product"
    initial_date_filter_type = initial_prefilter.get("date_filter_type") or "expiration_date"

    if initial_search_type in {"expiration_date", "inbound_date"}:
        initial_date_filter_type = initial_search_type
        initial_search_type = "product"

    if initial_search_type not in {
        "product",
        "inbound_id",
        "inbound_status",
    }:
        initial_search_type = "product"

    if initial_date_filter_type not in {"expiration_date", "inbound_date"}:
        initial_date_filter_type = "expiration_date"

    selected_start = {"value": _parse_prefilter_date(initial_prefilter.get("start_date"))}
    selected_end = {"value": _parse_prefilter_date(initial_prefilter.get("end_date"))}
    search_type_value = {"value": initial_search_type}
    date_filter_type_value = {"value": initial_date_filter_type}

    search_type_labels = {
        "product": "상품",
        "inbound_id": "입고ID",
        "inbound_status": "입고상태",
    }

    # 🔥 추가: DatePicker 전용 날짜 기준
    # - 검색창에 날짜를 직접 입력하지 않고, 기간 선택은 이 드롭다운 기준으로 처리
    date_filter_labels = {
        "expiration_date": "유통기한",
        "inbound_date": "입고일자",
    }

    # =========================================================
    # 🔥 컬럼 순서 수정
    # - stock이 주인공이라 브랜드 뒤에 stock 관련 컬럼 배치
    # - 상세ID / 발주ID / 중량 / 수량 / 판매가 / 샘플 / 활성 제거
    # =========================================================
    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product", "label": "상품", "width": 480, "align_x": 0},
        {"key": "expiration_date", "label": "유통기한", "width": 120, "align_x": 0},
        # 🔥 총 재고량 카드 월 필터 근거 컬럼
        # - 이 날짜가 2026-06-01 ~ 2026-06-30 안에 들어가야 6월 입고 재고임을 화면에서 확인 가능
        {"key": "inbound_date", "label": "입고일자", "width": 130, "align_x": 0},
        {"key": "inbound_id", "label": "입고ID", "width": 90, "align_x": 0},
        {"key": "inbound_status", "label": "입고상태", "width": 110, "align_x": 0},
        {"key": "save_stock", "label": "보관재고", "width": 100, "align_x": 0},
        {"key": "sale_stock", "label": "판매재고", "width": 100, "align_x": 0},
        {"key": "stock_available", "label": "가용재고", "width": 100, "align_x": 0},
        {"key": "scrap_stock", "label": "폐기재고", "width": 100, "align_x": 0},
        {"key": "last_update", "label": "최종수정일", "width": 170, "align_x": 0},
    ]

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": initial_prefilter.get("keyword") or "",
        "page_ref": None,
    }

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    result_text = ft.Text(
        value="DB 조회 전입니다.",
        size=13,
        color=TEXT_SECONDARY,
    )

    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    # 🔥 추가: 다른 조회 화면과 동일하게 조건 사용 후에만 보이는 초기화 버튼
    reset_button_holder = ft.Container(visible=False)

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_field = ft.TextField(
        width=220,
        height=38,
        value=pagination_state["keyword"],
        hint_text="검색어",
        hint_style=ft.TextStyle(size=13, color=HINT_TEXT),
        text_size=13,
        border_color=FIELD_BORDER,
        border_radius=6,
        bgcolor=FIELD_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
        text_align=ft.TextAlign.CENTER,
    )

    def format_date_text(value):
        if not value:
            return ""
        return value.strftime("%Y.%m.%d")

    def refresh_picker_fields():
        start_field_holder.content = date_value_box(
            text=format_date_text(selected_start["value"]),
            on_click=open_start_picker,
        )
        start_icon_holder.content = calendar_icon_box(on_click=open_start_picker)

        end_field_holder.content = date_value_box(
            text=format_date_text(selected_end["value"]),
            on_click=open_end_picker,
        )
        end_icon_holder.content = calendar_icon_box(on_click=open_end_picker)

    def on_start_date_change(e):
        if e.control.value:
            selected_start["value"] = normalize_to_date(e.control.value)

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        update_reset_button_visibility()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            selected_date = normalize_to_date(e.control.value)

            if selected_start["value"] and selected_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = selected_date

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
            start_date_picker.value = datetime.datetime.combine(
                selected_start["value"],
                datetime.time.min,
            )

        start_date_picker.open = True
        page.update()

    def open_end_picker(e):
        page = e.page

        if end_date_picker not in page.overlay:
            page.overlay.append(end_date_picker)

        if selected_start["value"]:
            end_date_picker.first_date = datetime.datetime.combine(
                selected_start["value"],
                datetime.time.min,
            )
        else:
            end_date_picker.first_date = datetime.datetime(2000, 1, 1)

        if selected_end["value"]:
            end_date_picker.value = datetime.datetime.combine(
                selected_end["value"],
                datetime.time.min,
            )
        elif selected_start["value"]:
            end_date_picker.value = datetime.datetime.combine(
                selected_start["value"],
                datetime.time.min,
            )

        end_date_picker.open = True
        page.update()

    search_type_text = ft.Text(
        value=search_type_labels[search_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    date_filter_text = ft.Text(
        value=date_filter_labels[date_filter_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

    rows_state = []

    def update_reset_button_visibility():
        # 🔥 추가: 기본 상태가 아니면 초기화 버튼 표시
        has_filter = (
            selected_start["value"] is not None
            or selected_end["value"] is not None
            or (search_field.value or "").strip() != ""
            or search_type_value["value"] != "product_id"
            or date_filter_type_value["value"] != "expiration_date"
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

    def set_date_filter_type(value: str, page: ft.Page | None = None):
        date_filter_type_value["value"] = value
        date_filter_text.value = date_filter_labels[value]
        update_reset_button_visibility()

        if page:
            page.update()
        else:
            date_filter_text.update()

    def build_search_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                padding=ft.Padding.only(left=2, right=2),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            on_click=lambda e: set_search_type(value, e.page),
        )

    def build_date_filter_menu_item(label: str, value: str):
        return ft.PopupMenuItem(
            height=34,
            content=ft.Container(
                padding=ft.Padding.only(left=2, right=2),
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
            on_click=lambda e: set_date_filter_type(value, e.page),
        )

    date_filter_type = ft.Container(
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
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=date_filter_text,
                ),
                ft.PopupMenuButton(
                    tooltip="날짜 기준 선택",
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
                        build_date_filter_menu_item(label, value)
                        for value, label in date_filter_labels.items()
                    ],
                ),
            ],
        ),
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
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 0),
                    content=search_type_text,
                ),
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
                    build_table_cell(
                        col["label"],
                        col["width"],
                        col["align_x"],
                        ft.FontWeight.W_700,
                        TEXT_PRIMARY,
                    )
                    for col in columns
                ],
            ),
        )

    def build_table_row(row):
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
                controls=[
                    build_table_cell(
                        row.get(col["key"], ""),
                        col["width"],
                        col["align_x"],
                    )
                    for col in columns
                ],
            ),
        )

    def build_empty_row(message: str):
        total_width = sum(col["width"] for col in columns) + (row_spacing * (len(columns) - 1))
        return ft.Container(
            padding=ft.Padding.only(
                left=row_padding_x,
                right=row_padding_x,
                top=28,
                bottom=28,
            ),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            content=ft.Container(
                width=total_width,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    value=message,
                    size=14,
                    color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_500,
                    text_align=ft.TextAlign.CENTER,
                ),
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()

        if not filtered_rows:
            table_rows_holder.controls.append(build_empty_row("일치하는 정보가 없습니다."))
            return

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def get_selected_date_text(value):
        if not value:
            return None
        return value.strftime("%Y-%m-%d")

    def fetch_total_count(keyword=""):
        return count_stocks(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=get_selected_date_text(selected_start["value"]),
            end_date=get_selected_date_text(selected_end["value"]),
            date_filter_type=date_filter_type_value["value"],
        )

    def fetch_stock_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE

        db_rows = fetch_stocks(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=get_selected_date_text(selected_start["value"]),
            end_date=get_selected_date_text(selected_end["value"]),
            date_filter_type=date_filter_type_value["value"],
        )

        return stock_db_row_adapter(db_rows, page_no)

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
            on_click=None if disabled or page_no is None else lambda e: move_page(page_no, e.page),
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
            on_click=None if disabled or page_no is None else lambda e: move_page(page_no, e.page),
            content=ft.Icon(
                icon_name,
                size=20,
                color=icon_color,
            ),
        )

    def refresh_pagination():
        total_pages = pagination_state["total_pages"]
        current_page = pagination_state["current_page"]

        if total_pages <= 1:
            pagination_holder.content = None
            return

        page_controls = [
            build_icon_page_button(
                ft.Icons.CHEVRON_LEFT,
                current_page - 1,
                disabled=(current_page == 1),
            )
        ]

        if total_pages <= 5:
            page_numbers = list(range(1, total_pages + 1))
        else:
            if current_page <= 3:
                page_numbers = [1, 2, 3, 4, None, total_pages]
            elif current_page >= total_pages - 2:
                page_numbers = [
                    1,
                    None,
                    total_pages - 3,
                    total_pages - 2,
                    total_pages - 1,
                    total_pages,
                ]
            else:
                page_numbers = [
                    1,
                    current_page - 1,
                    current_page,
                    current_page + 1,
                    None,
                    total_pages,
                ]

        for page_no in page_numbers:
            if page_no is None:
                page_controls.append(
                    ft.Container(
                        width=40,
                        height=40,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "...",
                            size=18,
                            color="#0F172A",
                            weight=ft.FontWeight.W_700,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    )
                )
            else:
                page_controls.append(
                    build_page_button(
                        label=str(page_no),
                        page_no=page_no,
                        selected=(page_no == current_page),
                    )
                )

        page_controls.append(
            build_icon_page_button(
                ft.Icons.CHEVRON_RIGHT,
                current_page + 1,
                disabled=(current_page == total_pages),
            )
        )

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

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]

        fetched_rows = fetch_stock_rows(keyword, current_page)

        rows_state.clear()
        rows_state.extend(fetched_rows)

        refresh_table(rows_state)
        refresh_pagination()

        start_text = (
            selected_start["value"].strftime("%Y-%m-%d")
            if selected_start["value"]
            else "미선택"
        )
        end_text = (
            selected_end["value"].strftime("%Y-%m-%d")
            if selected_end["value"]
            else "미선택"
        )

        date_filter_label = date_filter_labels.get(date_filter_type_value["value"], "유통기한")

        if pagination_state["total_count"] == 0:
            result_text.value = (
                f"기간기준: {date_filter_label} / "
                f"기간: {start_text} ~ {end_text} / "
                f"검색조건: {search_type_labels[search_type_value['value']]} / "
                f"검색어: {keyword if keyword else '없음'} / "
                "일치하는 정보가 없습니다."
            )
            return

        result_text.value = (
            f"기간기준: {date_filter_label} / "
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_type_labels[search_type_value['value']]} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"전체 {pagination_state['total_count']}건 / "
            f"현재 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def load_rows(page_ref: ft.Page | None = None):
        pagination_state["keyword"] = (search_field.value or "").strip()
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count("")
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)

        reload_current_page()

    def run_search(page_ref: ft.Page | None = None):
        keyword = (search_field.value or "").strip()

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count(keyword)
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)

        reload_current_page()

    def on_download(e):
        result_text.value = "다운로드 기능은 아직 연결 전입니다."
        e.page.update()

    def on_print(e):
        result_text.value = "인쇄 기능은 아직 연결 전입니다."
        e.page.update()

    def on_reset_click(e):
        # 🔥 추가: 다른 조회 화면과 동일하게 모든 조건을 기본값으로 복구
        selected_start["value"] = None
        selected_end["value"] = None

        date_filter_type_value["value"] = "expiration_date"
        date_filter_text.value = date_filter_labels["expiration_date"]
        search_type_value["value"] = "product_id"
        search_type_text.value = search_type_labels["product_id"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page
        pagination_state["total_count"] = fetch_total_count("")
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)

        refresh_picker_fields()
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    search_field.on_submit = lambda e: (run_search(e.page), update_reset_button_visibility(), e.page.update())

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨김, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78)
    update_reset_button_visibility()

    try:
        load_rows()
    except Exception as exc:
        result_text.value = f"DB 조회 실패: {exc}"

    table_total_width = sum(col["width"] for col in columns) + (row_spacing * (len(columns) - 1))

    table_area = ft.Container(
        expand=True,
        border=ft.border.all(1, TABLE_BORDER),
        border_radius=10,
        bgcolor=CARD_BG,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    width=table_total_width + (row_padding_x * 2),
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
            ],
        ),
    )

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
            date_filter_type,
            search_type,
            search_field,
            action_button(
                "조회",
                on_click=lambda e: (
                    load_rows(e.page)
                    if not (search_field.value or "").strip()
                    else run_search(e.page),
                    update_reset_button_visibility(),
                    e.page.update(),
                ),
                width=78,
            ),
            reset_button_holder,
            # 🔥 미구현 기능 버튼은 사용자 혼란 방지를 위해 숨김
        ],
    )
