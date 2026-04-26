import math
import datetime
import flet as ft

from components import common as cm
from backend.erp.stock.stock_product_detail_service import count_stocks, fetch_stocks


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

PAGE_SIZE = 50


# =========================================================
# 🔥 상품별 재고 상세 View
# - stock이 주인공인 화면
# - 중량/수량/판매가/샘플/활성/상세ID/발주ID 제거
# - 브랜드 뒤에 stock 관련 컬럼 배치
# =========================================================


def build_text(
    value,
    size=12,
    color=TEXT_PRIMARY,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.CENTER,
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
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Text(
            value=text,
            size=13,
            color=FIELD_TEXT,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
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
        on_click=on_click,
        content=ft.Icon(
            ft.Icons.CALENDAR_MONTH_OUTLINED,
            size=18,
            color="#4B5563",
        ),
    )


def action_button(text, on_click=None, width=78):
    return ft.Container(
        width=width,
        height=38,
        bgcolor=BUTTON_BG,
        border=ft.Border.all(1, BUTTON_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Text(
            value=text,
            size=13,
            color=BUTTON_TEXT,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
        ),
    )


def build_table_cell(
    text,
    width,
    align_x=0,
    weight=ft.FontWeight.W_400,
    color=TEXT_ROW,
    size=12,
):
    return ft.Container(
        width=width,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=text,
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.CENTER,
            max_lines=2,
        ),
    )


def _format_number(value):
    if value in [None, ""]:
        return ""

    try:
        if isinstance(value, bool):
            return str(value)
        return f"{int(value):,}"
    except Exception:
        return str(value)


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
                "expiration_date": row.get("expiration_date", ""),
                "inbound_id": row.get("inbound_id", ""),
                "inbound_status": row.get("inbound_status", ""),
                "save_stock": _format_number(row.get("save_stock", "")),
                "sale_stock": _format_number(row.get("sale_stock", "")),
                "stock_available": _format_number(row.get("stock_available", "")),
                "scrap_stock": _format_number(row.get("scrap_stock", "")),
                "last_update": row.get("last_update", ""),
            }
        )

    return rows


def normalize_to_date(value):
    if not value:
        return None

    # 🔥 +9 / -9 시간 보정 없이 DatePicker 선택값 그대로 사용
    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    return None


def erp_stock_product_detail_view():
    page_title = "재고관리 > 상품별 재고 상세"

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "product_id"}

    search_type_labels = {
        "product_id": "상품ID",
        "brand": "브랜드",
        "product_name": "상품명",
        "inbound_id": "입고ID",
        "inbound_status": "입고상태",
        "save_stock": "보관재고",
        "sale_stock": "판매재고",
        "scrap_stock": "폐기재고",
        "stock_available": "가용재고",
        "expiration_date": "유통기한",
    }

    # =========================================================
    # 🔥 컬럼 순서 수정
    # - stock이 주인공이라 브랜드 뒤에 stock 관련 컬럼 배치
    # - 상세ID / 발주ID / 중량 / 수량 / 판매가 / 샘플 / 활성 제거
    # =========================================================
    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product_id", "label": "상품ID", "width": 90, "align_x": 0},
        {"key": "brand", "label": "브랜드", "width": 130, "align_x": 0},
        {"key": "product_name", "label": "상품명", "width": 260, "align_x": 0},
        {"key": "expiration_date", "label": "유통기한", "width": 120, "align_x": 0},
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
        "keyword": "",
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

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_field = ft.TextField(
        width=220,
        height=38,
        value="",
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
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            selected_date = normalize_to_date(e.control.value)

            if selected_start["value"] and selected_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = selected_date

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

    rows_state = []

    def set_search_type(value: str):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        search_type_text.update()

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
            on_click=lambda e: set_search_type(value),
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

        if pagination_state["total_count"] == 0:
            result_text.value = (
                f"기간: {start_text} ~ {end_text} / "
                f"검색조건: {search_type_labels[search_type_value['value']]} / "
                f"검색어: {keyword if keyword else '없음'} / "
                "일치하는 정보가 없습니다."
            )
            return

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_type_labels[search_type_value['value']]} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"전체 {pagination_state['total_count']}건 / "
            f"현재 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def load_rows(page_ref: ft.Page | None = None):
        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count("")
        pagination_state["total_pages"] = max(
            1,
            math.ceil(pagination_state["total_count"] / PAGE_SIZE),
        )

        reload_current_page()

    def run_search(page_ref: ft.Page | None = None):
        keyword = (search_field.value or "").strip()

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count(keyword)
        pagination_state["total_pages"] = max(
            1,
            math.ceil(pagination_state["total_count"] / PAGE_SIZE),
        )

        reload_current_page()

    def on_download(e):
        result_text.value = "다운로드 기능은 아직 연결 전입니다."
        e.page.update()

    def on_print(e):
        result_text.value = "인쇄 기능은 아직 연결 전입니다."
        e.page.update()

    search_field.on_submit = lambda e: (run_search(e.page), e.page.update())

    refresh_picker_fields()

    try:
        load_rows()
    except Exception as exc:
        result_text.value = f"DB 조회 실패: {exc}"

    filter_bar = ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=ft.Padding.only(left=20, right=20, top=12, bottom=12),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                start_field_holder,
                start_icon_holder,
                end_field_holder,
                end_icon_holder,
                search_type,
                search_field,
                action_button(
                    "조회",
                    on_click=lambda e: (
                        load_rows(e.page)
                        if not (search_field.value or "").strip()
                        else run_search(e.page),
                        e.page.update(),
                    ),
                    width=78,
                ),
                action_button("인쇄", on_click=on_print, width=78),
                action_button("다운로드", on_click=on_download, width=104),
            ],
        ),
    )

    table_content = ft.Column(
        spacing=0,
        controls=[
            build_table_header(),
            table_rows_holder,
        ],
    )

    table_area = ft.Container(
        expand=True,
        border=ft.border.all(1, TABLE_BORDER),
        border_radius=10,
        bgcolor=CARD_BG,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(content=table_content),
            ],
        ),
    )

    main_content = ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=0,
        content=ft.Column(
            spacing=0,
            controls=[
                filter_bar,
                ft.Container(
                    padding=20,
                    expand=True,
                    content=ft.Column(
                        spacing=14,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            ft.Text(
                                value=page_title,
                                size=20,
                                color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_700,
                            ),
                            result_text,
                            table_area,
                            pagination_holder,
                        ],
                    ),
                ),
            ],
        ),
    )

    return ft.Container(
        expand=True,
        content=main_content,
    )
