import re

import flet as ft
from components import common as cm
# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_product_join_rows, fetch_product_join_rows, create_product_detail, update_product_detail
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import PRODUCT_DETAIL_FIELDS, PRODUCT_DETAIL_EDIT_FIELDS
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button, build_width_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages, build_pagination_bar
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area






# =========================================================
# ☑️ 상품 상세 session prefix
# =========================================================
SESSION_PREFIX = "product_detail"


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


def _build_product_no(product_detail_id, product_id):
    product_detail_id = str(product_detail_id or "").strip()
    product_id = str(product_id or "").strip()

    if product_detail_id and product_id:
        return f"{product_detail_id}-{product_id}"

    return product_detail_id or product_id


def _strip_product_weight(product_name, weight=None):
    name = str(product_name or "").strip()
    if not name:
        return ""

    weight_text = str(weight or "").replace(",", "").strip()
    if weight_text:
        name = re.sub(
            rf"\s*\(?\s*{re.escape(weight_text)}\s*(?:g|kg|ml|l|G|KG|ML|L)\s*\)?\s*$",
            "",
            name,
        ).strip()
        name = re.sub(
            rf"\s*\(\s*{re.escape(weight_text)}\s*(?:g|kg|ml|l|G|KG|ML|L)[^)]*\)\s*$",
            "",
            name,
        ).strip()

    return re.sub(
        r"\s*(?:\(\s*)?\d+(?:\.\d+)?\s*(?:g|kg|ml|l|G|KG|ML|L)(?:[^)]*\))?\s*$",
        "",
        name,
    ).strip()


def product_detail_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        product_detail_id = row.get("product_detail_id", "")
        product_id = row.get("product_id", "")
        weight = row.get("weight", "")
        rows.append(
            {
                "no": str(row.get("no", index)),  # 🔥 API에서 내려준 no가 있으면 우선 사용
                "product_no": _build_product_no(product_detail_id, product_id),
                "product_detail_id": product_detail_id,
                "product_id": product_id,
                "type": row.get("type", ""),
                "brand": row.get("brand", ""),
                "product_name": _strip_product_weight(row.get("product_name", ""), weight),
                "function": row.get("function", ""),
                "main_protein": row.get("main_protein", ""),
                "life": row.get("life", ""),
                "weight": weight,
                "retail_price": row.get("retail_price", ""),
                "quantity": row.get("quantity", ""),
                "active": row.get("active", ""),
            }
        )

    return rows


# =========================================================
# ☑️ 모달 저장 데이터 -> 테이블 row 변환
# =========================================================
def product_detail_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_no": "",
        "product_detail_id": "",
        "product_id": "",
        "type": saved_data.get("type", ""),
        "brand": saved_data.get("brand", ""),
        "product_name": _strip_product_weight(saved_data.get("product_name", ""), saved_data.get("weight", "")),
        "function": saved_data.get("function", ""),
        "main_protein": saved_data.get("main_protein", ""),
        "life": saved_data.get("life", ""),
        "weight": "",
        "retail_price": "",
        "quantity": "",
        "active": "",
    }


def erp_product_detail_view():
    edit_state = {"product_id": None}
    page_title = "상품관리 > 상품 상세 정보 관리"

    search_type_value = {"value": "product_name"}
    search_type_labels = {
        "product_name": "상품명",
        "product_no": "상품번",
        "type": "타입",
        "brand": "브랜드",
        "quantity": "수량(ea)",
        "weight": "중량(g)",
        "retail_price": "판매가(원)",
        "function": "기능",
        "main_protein": "주원료",
        "life": "생애주기",  # 🔥 추가: 생애주기 부분검색 조건
        "active": "판매상태",
    }

    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product_no", "label": "상품번", "width": 110, "align_x": 0},
        {"key": "product_name", "label": "상품명", "width": 250, "align_x": 0},
        {"key": "quantity", "label": "수량(ea)", "width": 80, "align_x": 0},
        {"key": "weight", "label": "중량(g)", "width": 90, "align_x": 0},
        {"key": "retail_price", "label": "판매가(원)", "width": 110, "align_x": 0},
        {"key": "brand", "label": "브랜드", "width": 100, "align_x": 0},
        {"key": "type", "label": "타입", "width": 90, "align_x": 0},
        {"key": "main_protein", "label": "주원료", "width": 130, "align_x": 0},
        {"key": "life", "label": "생애주기", "width": 90, "align_x": 0},
        {"key": "function", "label": "기능", "width": 210, "align_x": 0},
        {"key": "active", "label": "판매상태", "width": 100, "align_x": 0},
    ]

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": "",
        "search_type": "product_name",
        "page_ref": None,
    }
    request_state = {"id": 0, "initial_loaded": False}

    result_text = ft.Text(
        value="DB 조회 전입니다.",
        size=13,
        color=TEXT_SECONDARY,
    )
    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    # 🔥 추가: 검색조건/검색어 사용 후에만 보이는 초기화 버튼 자리
    reset_button_holder = ft.Container(visible=False)

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

    def update_reset_button_visibility():
        # 🔥 추가: 고객관리 3총사와 동일하게 기본 상태가 아니면 초기화 버튼 표시
        has_filter = (
            (search_field.value or "").strip() != ""
            or search_type_value["value"] != "product_name"
            or (pagination_state["keyword"] or "").strip() != ""
        )
        reset_button_holder.visible = has_filter

    def update_lookup_controls():
        for control in (
            table_rows_holder,
            pagination_holder,
            result_text,
            reset_button_holder,
        ):
            try:
                control.update()
            except Exception:
                pass

    def set_search_type(value: str, page: ft.Page | None = None):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        update_reset_button_visibility()

        if page:
            search_type_text.update()
            reset_button_holder.update()
        else:
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
            on_click=lambda e: set_search_type(value, e.page),
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
            ink=True,
            on_click=lambda e, selected_row=row: open_edit_modal(e, selected_row),
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
    def fetch_total_count(keyword="", search_type=None):
        return count_product_join_rows(
            search_type=search_type or search_type_value["value"],
            keyword=keyword,
        )

    def fetch_product_rows(keyword="", page_no=1, search_type=None):
        offset = (page_no - 1) * PAGE_SIZE
        db_rows = fetch_product_join_rows(
            search_type=search_type or search_type_value["value"],
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

        start_lookup(
            page,
            keyword=pagination_state["keyword"],
            page_no=page_no,
            search_type=pagination_state["search_type"],
            recalc_count=False,
            loading_message=f"{page_no}페이지 조회 중...",
        )

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

        pagination_holder.content = build_pagination_bar(
            current_page,
            total_pages,
            lambda page_no, e: move_page(page_no, e.page),
        )

    def apply_loaded_rows(keyword, page_no, search_type, total_count, total_pages, fetched_rows):
        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = page_no
        pagination_state["search_type"] = search_type
        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = total_pages

        rows_state.clear()
        rows_state.extend(fetched_rows)
        refresh_table(rows_state)
        refresh_pagination()

        search_label = search_type_labels.get(search_type, search_type)

        if total_count == 0:
            result_text.value = (
                f"검색조건: {search_label} / "
                f"검색어: {keyword if keyword else '없음'} / "
                "일치하는 정보가 없습니다."
            )
            return

        result_text.value = (
            f"검색조건: {search_label} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"전체 {total_count}건 / "
            f"현재 {len(rows_state)}건 / "
            f"{page_no} / {total_pages} 페이지"
        )

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]
        search_type = pagination_state["search_type"]

        fetched_rows = fetch_product_rows(keyword, current_page, search_type)
        apply_loaded_rows(
            keyword,
            current_page,
            search_type,
            pagination_state["total_count"],
            pagination_state["total_pages"],
            fetched_rows,
        )

    def load_rows(page_ref: ft.Page | None = None):
        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["search_type"] = search_type_value["value"]
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count("", pagination_state["search_type"])
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
        reload_current_page()
        update_reset_button_visibility()

    def run_search(page_ref: ft.Page | None = None):
        keyword = (search_field.value or "").strip()

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = 1
        pagination_state["search_type"] = search_type_value["value"]
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count(keyword, pagination_state["search_type"])
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
        reload_current_page()
        update_reset_button_visibility()

    def set_lookup_loading(message: str):
        result_text.value = message
        table_rows_holder.controls.clear()
        table_rows_holder.controls.append(build_empty_row(message))
        pagination_holder.content = None

    def start_lookup(
        page_ref: ft.Page | None,
        *,
        keyword: str,
        page_no: int = 1,
        search_type: str | None = None,
        recalc_count: bool = True,
        loading_message: str = "조회 중...",
    ):
        if page_ref is None:
            return

        request_state["id"] += 1
        request_id = request_state["id"]
        selected_search_type = search_type or search_type_value["value"]

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = page_no
        pagination_state["search_type"] = selected_search_type
        pagination_state["page_ref"] = page_ref
        update_reset_button_visibility()
        set_lookup_loading(loading_message)
        update_lookup_controls()

        def worker():
            try:
                total_count = (
                    fetch_total_count(keyword, selected_search_type)
                    if recalc_count
                    else pagination_state["total_count"]
                )
                total_pages = calc_total_pages(total_count, PAGE_SIZE)
                rows = fetch_product_rows(keyword, page_no, selected_search_type)

                if request_id != request_state["id"]:
                    return

                apply_loaded_rows(
                    keyword,
                    page_no,
                    selected_search_type,
                    total_count,
                    total_pages,
                    rows,
                )
            except Exception as exc:
                if request_id == request_state["id"]:
                    rows_state.clear()
                    table_rows_holder.controls.clear()
                    table_rows_holder.controls.append(build_empty_row("조회 중 오류가 발생했습니다."))
                    pagination_holder.content = None
                    result_text.value = f"DB 조회 실패: {exc}"
            finally:
                if request_id == request_state["id"]:
                    update_reset_button_visibility()
                    update_lookup_controls()

        page_ref.run_thread(worker)

    def on_reset_click(e):
        # 🔥 추가: 검색조건/검색어를 기본값으로 되돌리고 첫 화면 재조회
        search_type_value["value"] = "product_name"
        search_type_text.value = search_type_labels["product_name"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page

        search_type_text.update()
        search_field.update()
        start_lookup(
            e.page,
            keyword="",
            page_no=1,
            search_type="product_name",
            recalc_count=True,
            loading_message="초기화 후 조회 중...",
        )

    def close_register_modal(e):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        dim_bg.update()
        popup_layer.update()

    def clear_register_session(page: ft.Page):
        for field in PRODUCT_DETAIL_FIELDS:
            page.session.store.set(f"{SESSION_PREFIX}_{field['key']}", "")

    def handle_register_success(saved_data: dict):
        create_product_detail(saved_data)
        pagination_state["current_page"] = 1
        pagination_state["keyword"] = ""
        pagination_state["total_count"] = fetch_total_count("")
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
        reload_current_page()

    def handle_edit_success(saved_data: dict):
        if not edit_state["product_id"]:
            raise ValueError("수정할 상품ID를 찾을 수 없습니다.")
        update_product_detail(edit_state["product_id"], saved_data)
        reload_current_page()

    def active_for_form(value):
        text = str(value or "").strip().lower()
        if text in {"false", "0", "n", "no"} or "중지" in text:
            return "false"
        return "true"

    def set_product_edit_session(page: ft.Page, row: dict):
        for field in PRODUCT_DETAIL_EDIT_FIELDS:
            key = field["key"]
            value = row.get(key, "")
            if key == "active":
                value = active_for_form(value)
            page.session.store.set(f"{SESSION_PREFIX}_{key}", str(value or ""))

    def open_register_modal(e):
        edit_state["product_id"] = None
        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="상품 상세 정보 등록",
            edit_title="상품 상세 정보 수정",
            fields=PRODUCT_DETAIL_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_register_modal,
            on_submit_success=handle_register_success,
            mode="register",
            confirm_message="상품 상세 정보를 등록하시겠습니까?\n등록 후 조회 화면에 바로 반영됩니다.",
        )
        dim_bg.visible = True
        popup_layer.visible = True
        dim_bg.update()
        popup_layer.update()

    def open_edit_modal(e, row):
        product_id = row.get("product_id")
        if not product_id:
            return
        edit_state["product_id"] = product_id
        set_product_edit_session(e.page, row)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="상품 상세 정보 등록",
            edit_title="상품 상세 정보 수정",
            fields=PRODUCT_DETAIL_EDIT_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_register_modal,
            on_submit_success=handle_edit_success,
            mode="edit",
            confirm_message="상품 정보를 수정하시겠습니까?\n이미 주문/재고에서 사용 중인 상품이면 과거 조회 화면에도 변경된 정보가 표시될 수 있습니다.",
        )
        dim_bg.visible = True
        popup_layer.visible = True
        dim_bg.update()
        popup_layer.update()

    dim_bg.on_click = close_register_modal
    search_field.on_submit = lambda e: start_lookup(
        e.page,
        keyword=(search_field.value or "").strip(),
        page_no=1,
        search_type=search_type_value["value"],
        recalc_count=True,
        loading_message="검색 중...",
    )

    # 🔥 추가: 처음에는 숨겨두고, 검색조건/검색어가 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78)
    update_reset_button_visibility()

    set_lookup_loading("화면 준비 중...")

    # =========================================================
    # 🔥 조회 화면 공통 레이아웃 적용
    # - 필터바 위치/본문 여백/제목 크기를 다른 조회 화면과 통일
    # - 상품 상세 테이블은 컬럼이 많으므로 가로 스크롤 구조는 유지
    # =========================================================
    total_table_width = sum(col["width"] for col in columns) + (row_spacing * (len(columns) - 1))

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
                    width=total_table_width + (row_padding_x * 2),
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

    page_layout = build_lookup_page_layout(
        page_title=page_title,
        result_text=result_text,
        table_area=table_area,
        pagination_holder=pagination_holder,
        overlay_controls=[dim_bg, popup_layer],
        filter_controls=[
            search_type,
            search_field,
            action_button(
                "조회",
                on_click=lambda e: start_lookup(
                    e.page,
                    keyword=(search_field.value or "").strip(),
                    page_no=1,
                    search_type=search_type_value["value"],
                    recalc_count=True,
                    loading_message="조회 중...",
                ),
                width=78,
            ),
            reset_button_holder,
            # 🔥 미구현 기능 버튼은 사용자 혼란 방지를 위해 숨김
            action_button("등록", on_click=open_register_modal, width=78),
        ],
    )

    class ProductDetailPage(ft.Container):
        def did_mount(self):
            if request_state["initial_loaded"]:
                return
            request_state["initial_loaded"] = True
            start_lookup(
                self.page,
                keyword="",
                page_no=1,
                search_type=search_type_value["value"],
                recalc_count=True,
                loading_message="조회 중...",
            )

    return ProductDetailPage(expand=True, content=page_layout)
