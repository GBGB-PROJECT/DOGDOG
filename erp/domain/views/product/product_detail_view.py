import math
import flet as ft
from components import common as cm
from backend.erp.product.service import count_product_join_rows, fetch_product_join_rows, create_product_detail
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import PRODUCT_DETAIL_FIELDS


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

# =========================================================
# ☑️ 상품 상세 session prefix
# =========================================================
SESSION_PREFIX = "product_detail"
PAGE_SIZE = 50


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
        alignment=ft.Alignment(0, 0),
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


def _format_sale_status(value):
    if value is True:
        return "판매중"
    if value is False:
        return "판매중지"

    lowered = str(value).lower()
    if lowered == "true":
        return "판매중"
    if lowered == "false":
        return "판매중지"

    return str(value or "")


def product_detail_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        product_detail_id = row.get("product_detail_id", "")
        product_id = row.get("product_id", "")

        rows.append(
            {
                "no": str(index),
                "product_display_id": f"{product_detail_id}-{product_id}" if product_detail_id != "" and product_id != "" else "",
                "type": row.get("type", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "function": row.get("function", ""),
                "main_protein": row.get("main_protein", ""),
                "life": row.get("life", ""),
                "weight": _format_number(row.get("weight", "")),
                "retail_price": _format_number(row.get("retail_price", "")),
                "quantity": _format_number(row.get("quantity", "")),
                "active": _format_sale_status(row.get("active", "")),
            }
        )

    return rows


# =========================================================
# ☑️ 모달 저장 데이터 -> 테이블 row 변환
# =========================================================
def product_detail_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_display_id": "",
        "type": saved_data.get("type", ""),
        "brand": saved_data.get("brand", ""),
        "product_name": saved_data.get("product_name", ""),
        "function": saved_data.get("function", ""),
        "main_protein": saved_data.get("main_protein", ""),
        "life": saved_data.get("life", ""),
        "weight": "",
        "retail_price": "",
        "quantity": "",
        "active": "",
    }


def erp_product_detail_view():
    page_title = "상품관리 > 상품 상세 정보 관리"

    search_type_value = {"value": "product_name"}
    search_type_labels = {
        "product_name": "상품명",
        "type": "타입",
        "brand": "브랜드",
        "function": "기능",
        "main_protein": "주원료",
    }

    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product_display_id", "label": "상품ID", "width": 110, "align_x": 0},
        {"key": "type", "label": "타입", "width": 90, "align_x": 0},
        {"key": "brand", "label": "브랜드", "width": 100, "align_x": 0},
        {"key": "product_name", "label": "상품명", "width": 250, "align_x": 0},
        {"key": "function", "label": "기능", "width": 200, "align_x": 0},
        {"key": "main_protein", "label": "주원료", "width": 140, "align_x": 0},
        {"key": "life", "label": "생애주기", "width": 90, "align_x": 0},
        {"key": "weight", "label": "중량(g)", "width": 90, "align_x": 0},
        {"key": "retail_price", "label": "판매가(원)", "width": 110, "align_x": 0},
        {"key": "quantity", "label": "유닛(EA)", "width": 90, "align_x": 0},
        {"key": "active", "label": "판매상태", "width": 100, "align_x": 0},
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

    dim_bg = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
    )

    popup_layer = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

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

    search_type_text = ft.Text(
        value=search_type_labels[search_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
        text_align=ft.TextAlign.CENTER,
    )

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

    rows_state = []

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

    # =========================================================
    # ☑️ SQLAlchemy ORM: 상품 상세 count/list 조회
    # - OPD.product + OPD.product_detail JOIN 기반 조회
    # =========================================================
    def fetch_total_count(keyword=""):
        return count_product_join_rows(
            search_type=search_type_value["value"],
            keyword=keyword,
        )

    def fetch_product_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        db_rows = fetch_product_join_rows(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
        )
        return product_detail_db_row_adapter(db_rows, page_no)

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
                page_numbers = [1, None, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
            else:
                page_numbers = [1, current_page - 1, current_page, current_page + 1, None, total_pages]

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

        fetched_rows = fetch_product_rows(keyword, current_page)

        rows_state.clear()
        rows_state.extend(fetched_rows)
        refresh_table(rows_state)
        refresh_pagination()

        if pagination_state["total_count"] == 0:
            result_text.value = (
                f"검색조건: {search_type_labels[search_type_value['value']]} / "
                f"검색어: {keyword if keyword else '없음'} / "
                "일치하는 정보가 없습니다."
            )
            return

        result_text.value = (
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

    def close_register_modal(e):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        e.page.update()

    def clear_register_session(page: ft.Page):
        for field in PRODUCT_DETAIL_FIELDS:
            page.session.store.set(f"{SESSION_PREFIX}_{field['key']}", "")

    def handle_register_success(saved_data: dict):
        create_product_detail(saved_data)
        pagination_state["current_page"] = 1
        pagination_state["keyword"] = ""
        pagination_state["total_count"] = fetch_total_count("")
        pagination_state["total_pages"] = max(
            1,
            math.ceil(pagination_state["total_count"] / PAGE_SIZE),
        )
        reload_current_page()

    def open_register_modal(e):
        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="상품 상세 정보 등록",
            edit_title="상품 상세 정보 수정",
            fields=PRODUCT_DETAIL_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_register_modal,
            on_submit_success=handle_register_success,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        e.page.update()

    dim_bg.on_click = close_register_modal
    search_field.on_submit = lambda e: (run_search(e.page), e.page.update())

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
                search_type,
                search_field,
                action_button(
                    "조회",
                    on_click=lambda e: (
                        load_rows(e.page) if not (search_field.value or "").strip() else run_search(e.page),
                        e.page.update(),
                    ),
                    width=78,
                ),
                action_button("인쇄", on_click=on_print, width=78),
                action_button("다운로드", on_click=on_download, width=104),
                action_button("등록", on_click=open_register_modal, width=78),
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
            controls=[ft.Container(content=table_content)],
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
        content=ft.Stack(
            expand=True,
            controls=[
                main_content,
                dim_bg,
                popup_layer,
            ],
        ),
    )