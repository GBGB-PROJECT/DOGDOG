import flet as ft
from components import common as cm
# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_product_join_rows, fetch_product_join_rows, create_product_detail
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import PRODUCT_DETAIL_FIELDS
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button, build_width_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages






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


def product_detail_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(row.get("no", index)),  # 🔥 API에서 내려준 no가 있으면 우선 사용
                "product_detail_id": row.get("product_detail_id", ""),  # 🔥 수정: 상품상세ID 분리 표시
                "product_id": row.get("product_id", ""),  # 🔥 수정: 상품ID 분리 표시
                "type": row.get("type", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "function": row.get("function", ""),
                "main_protein": row.get("main_protein", ""),
                "life": row.get("life", ""),
                "weight": row.get("weight", ""),
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
        "product_detail_id": "",
        "product_id": "",
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
        "life": "생애주기",  # 🔥 추가: 생애주기 부분검색 조건
    }

    columns = [
        {"key": "no", "label": "No", "width": 60, "align_x": 0},
        {"key": "product_detail_id", "label": "상품상세ID", "width": 100, "align_x": 0},  # 🔥 수정: ID 분리
        {"key": "product_id", "label": "상품ID", "width": 90, "align_x": 0},  # 🔥 수정: ID 분리
        {"key": "type", "label": "타입", "width": 90, "align_x": 0},
        {"key": "brand", "label": "브랜드", "width": 100, "align_x": 0},
        {"key": "product_name", "label": "상품명", "width": 250, "align_x": 0},
        {"key": "function", "label": "기능", "width": 200, "align_x": 0},
        {"key": "main_protein", "label": "주원료", "width": 140, "align_x": 0},
        {"key": "life", "label": "생애주기", "width": 90, "align_x": 0},
        {"key": "weight", "label": "중량(g)", "width": 90, "align_x": 0},
        {"key": "retail_price", "label": "판매가(원)", "width": 110, "align_x": 0},
        {"key": "quantity", "label": "수량(ea)", "width": 90, "align_x": 0},
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
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
        reload_current_page()
        update_reset_button_visibility()

    def run_search(page_ref: ft.Page | None = None):
        keyword = (search_field.value or "").strip()

        pagination_state["keyword"] = keyword
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = page_ref
        pagination_state["total_count"] = fetch_total_count(keyword)
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
        reload_current_page()
        update_reset_button_visibility()

    def on_reset_click(e):
        # 🔥 추가: 검색조건/검색어를 기본값으로 되돌리고 첫 화면 재조회
        search_type_value["value"] = "product_name"
        search_type_text.value = search_type_labels["product_name"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page

        load_rows(e.page)
        update_reset_button_visibility()
        e.page.update()

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
        pagination_state["total_pages"] = calc_total_pages(pagination_state["total_count"], PAGE_SIZE)
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
    search_field.on_submit = lambda e: (run_search(e.page), update_reset_button_visibility(), e.page.update())

    # 🔥 추가: 처음에는 숨겨두고, 검색조건/검색어가 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78)
    update_reset_button_visibility()

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
                        update_reset_button_visibility(),
                        e.page.update(),
                    ),
                    width=78,
                ),
                reset_button_holder,
                action_button("인쇄", on_click=on_print, width=78),
                action_button("다운로드", on_click=on_download, width=104),
                action_button("등록", on_click=open_register_modal, width=78),
            ],
        ),
    )

    # =========================================================
    # 🔥 inbound_view.py 방식으로 스크롤 구조 통일
    # - 화면 전체가 아니라 테이블 데이터 행 영역만 세로 스크롤
    # - pagination_holder는 테이블 스크롤 영역 밖에 두어 하단 고정처럼 유지
    # - 상품 상세 테이블은 컬럼이 많으므로 가로 스크롤은 유지
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

    main_content = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,  # 🔥 수정: 화면 배경 흰색 통일
        padding=0,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                filter_bar,
                ft.Container(
                    padding=20,
                    expand=True,
                    bgcolor=ft.Colors.WHITE,  # 🔥 수정: 본문 안쪽 배경 흰색 통일
                    content=ft.Column(
                        expand=True,
                        spacing=14,
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
        bgcolor=ft.Colors.WHITE,  # 🔥 수정: 최외곽 배경 흰색 통일
        content=ft.Stack(
            expand=True,
            controls=[
                main_content,
                dim_bg,
                popup_layer,
            ],
        ),
    )
