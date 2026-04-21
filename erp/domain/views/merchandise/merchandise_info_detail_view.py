import flet as ft
from db import fetch_all
from full_query import ProductDetail
from components import common as cm
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
        ),
    )


def build_table_cell(
    text,
    width,
    align_x=-1,
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
            text_align=ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT,
            max_lines=2,
        ),
    )


def get_product_detail_rows(keyword=""):
    if keyword:
        search = f"%{keyword}%"
        raw_rows = fetch_all(
            ProductDetail.search_query,
            (search, search, search, search, search),
        )
    else:
        raw_rows = fetch_all(ProductDetail.list_query)

    rows = []
    for index, row in enumerate(raw_rows, start=1):
        rows.append(
            {
                "no": str(index),
                "product_detail_id": row.get("product_detail_id", ""),
                "type": row.get("type", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "function": row.get("function", ""),
                "description": row.get("description", ""),
                "crude_protein": row.get("crude_protein", ""),
                "crude_fat": row.get("crude_fat", ""),
                "calories": row.get("calories", ""),
                "thumbnail": row.get("thumbnail", ""),
                "kibble_size": row.get("kibble_size", ""),
                "life": row.get("life", ""),
                "protein_type": row.get("protein_type", ""),
                "main_protein": row.get("main_protein", ""),
                "certified": row.get("certified", ""),
                "preservative": row.get("preservative", ""),
                "feedshape": row.get("feedshape", ""),
            }
        )
    return rows


# =========================================================
# ☑️ 모달 저장 데이터 -> 테이블 row 변환
# =========================================================
def product_detail_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_detail_id": "",
        "type": saved_data.get("type", ""),
        "brand": saved_data.get("brand", ""),
        "product_name": saved_data.get("product_name", ""),
        "function": saved_data.get("function", ""),
        "description": saved_data.get("description", ""),
        "crude_protein": saved_data.get("crude_protein", ""),
        "crude_fat": saved_data.get("crude_fat", ""),
        "calories": saved_data.get("calories", ""),
        "thumbnail": saved_data.get("thumbnail", ""),
        "kibble_size": saved_data.get("kibble_size", ""),
        "life": saved_data.get("life", ""),
        "protein_type": saved_data.get("protein_type", ""),
        "main_protein": saved_data.get("main_protein", ""),
        "certified": saved_data.get("certified", ""),
        "preservative": saved_data.get("preservative", ""),
        "feedshape": saved_data.get("feedshape", ""),
    }


def erp_merchandise_info_detail_view():
    page_title = "상품관리 > 상품 상세 정보 관리"

    search_type_value = {"value": "product_name"}
    search_type_labels = {
        "product_name": "상품명",
        "type": "타입",
        "brand": "브랜드",
        "function": "기능",
        "main_protein": "주원료",
    }
    search_key_map = {
        "product_name": "product_name",
        "type": "type",
        "brand": "brand",
        "function": "function",
        "main_protein": "main_protein",
    }

    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product_detail_id", "label": "상세ID", "width": 80, "align_x": 1},
        {"key": "type", "label": "타입", "width": 90, "align_x": -1},
        {"key": "brand", "label": "브랜드", "width": 90, "align_x": -1},
        {"key": "product_name", "label": "상품명", "width": 220, "align_x": -1},
        {"key": "function", "label": "기능", "width": 220, "align_x": -1},
        {"key": "description", "label": "설명", "width": 220, "align_x": -1},
        {"key": "crude_protein", "label": "조단백", "width": 80, "align_x": 1},
        {"key": "crude_fat", "label": "조지방", "width": 80, "align_x": 1},
        {"key": "calories", "label": "칼로리", "width": 80, "align_x": 1},
        {"key": "thumbnail", "label": "썸네일 URL", "width": 220, "align_x": -1},
        {"key": "kibble_size", "label": "알갱이 크기", "width": 100, "align_x": -1},
        {"key": "life", "label": "급여 단계", "width": 90, "align_x": -1},
        {"key": "protein_type", "label": "단백질유형", "width": 100, "align_x": -1},
        {"key": "main_protein", "label": "주원료", "width": 140, "align_x": -1},
        {"key": "certified", "label": "인증", "width": 120, "align_x": -1},
        {"key": "preservative", "label": "보존제", "width": 140, "align_x": -1},
        {"key": "feedshape", "label": "사료 형태", "width": 90, "align_x": -1},
    ]

    result_text = ft.Text(
        value="DB 조회 전입니다.",
        size=13,
        color=TEXT_SECONDARY,
    )
    table_rows_holder = ft.Column(spacing=0)

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
    )

    search_type_text = ft.Text(
        value=search_type_labels[search_type_value["value"]],
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
                padding=ft.Padding.only(left=2, right=2),
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
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

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()
        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def load_rows(keyword=""):
        rows_state.clear()
        rows_state.extend(get_product_detail_rows(keyword))
        refresh_table(rows_state)
        result_text.value = f"조회 건수: {len(rows_state)}건"

    def run_search():
        keyword = (search_field.value or "").strip()

        if not keyword:
            load_rows("")
            result_text.update()
            return

        actual_key = search_key_map.get(search_type_value["value"], "product_name")
        db_rows = get_product_detail_rows(keyword)

        filtered_rows = []
        for row in db_rows:
            target_value = str(row.get(actual_key, ""))
            if keyword.lower() in target_value.lower():
                filtered_rows.append(row)

        rows_state.clear()
        rows_state.extend(filtered_rows)
        refresh_table(filtered_rows)
        result_text.value = f"검색어: {keyword} / 조회 건수: {len(rows_state)}건"
        result_text.update()

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
        next_no = len(rows_state) + 1
        new_row = product_detail_row_adapter(saved_data, next_no)
        rows_state.append(new_row)
        refresh_table(rows_state)

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
    search_field.on_submit = lambda e: run_search()

    try:
        load_rows("")
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
                action_button("조회", on_click=lambda e: run_search(), width=78),
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