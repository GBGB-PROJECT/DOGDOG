import math
import flet as ft
import datetime

from components import common as cm
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import SUPPLIER_FIELDS
from backend.erp.production.service import count_suppliers, fetch_suppliers, create_supplier, create_supplier


# =========================================================
# ☑️ customer_view 스타일 참고용 공통 색상
# =========================================================
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

SESSION_PREFIX = "supplier"
PAGE_SIZE = 50


def build_text(
    value,
    size=12,
    color=TEXT_PRIMARY,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.LEFT,
):
    return ft.Text(
        value=str(value or ""),
        size=size,
        color=color,
        weight=weight,
        text_align=text_align,
        max_lines=1,
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
        on_click=on_click,
        content=ft.Text(
            value=text,
            size=13,
            color=FIELD_TEXT,
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
        ),
    )


def build_table_cell(
    text,
    expand,
    align_x=-1,
    weight=ft.FontWeight.W_400,
    color=TEXT_ROW,
    size=12,
):
    return ft.Container(
        expand=expand,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=text,
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT,
        ),
    )


def supplier_row_adapter(saved_data: dict, next_no: int):
    contact_raw = (saved_data.get("is_contact_status", "") or "").strip().lower()

    contact_text = "활성" if contact_raw in ["true", "1", "y", "yes", "활성", "가능"] else "비활성"

    return {
        "no": str(next_no),
        "supplier_id": "",
        "supplier_name": saved_data.get("supplier_name", ""),
        "brn": saved_data.get("brn", ""),
        "is_contact_status": contact_text,
        "designated_payment_date": saved_data.get("designated_payment_date", ""),
        "scheduled_payment_date": saved_data.get("scheduled_payment_date", ""),
        "employee_id": saved_data.get("employee_id", ""),
        "memo": saved_data.get("memo", ""),
        "sup_manager": saved_data.get("sup_manager", ""),
        "phone": saved_data.get("phone", ""),
        "last_update": "",
    }


def supplier_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "brn": row.get("brn", ""),
                "is_contact_status": "활성" if row.get("is_contact_status") else "비활성",
                "designated_payment_date": row.get("designated_payment_date", ""),
                "scheduled_payment_date": row.get("scheduled_payment_date", ""),
                "employee_id": row.get("employee_id", ""),
                "memo": row.get("memo", ""),
                "sup_manager": row.get("sup_manager", ""),
                "phone": row.get("phone", ""),
                "last_update": row.get("last_update", ""),
            }
        )

    return rows


def erp_production_supplier_view():
    page_title = "생산관리 > 거래처 관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "supplier_name"}

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
        value="조회 전입니다.",
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

    col_expand = {
        "no": 4,
        "supplier_id": 6,
        "supplier_name": 12,
        "brn": 10,
        "is_contact_status": 8,
        "designated_payment_date": 8,
        "scheduled_payment_date": 10,
        "employee_id": 6,
        "memo": 12,
        "sup_manager": 8,
        "phone": 10,
        "last_update": 12,
    }

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_type_labels = {
        "supplier_id": "거래처ID",
        "supplier_name": "거래처명",
        "brn": "사업자번호",
        "is_contact_status": "연락상태",
        "sup_manager": "담당자명",
        "phone": "전화번호",
    }

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
            corrected_date = e.control.value + datetime.timedelta(hours=9)
            selected_start["value"] = corrected_date

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            corrected_date = e.control.value + datetime.timedelta(hours=9)

            if selected_start["value"] and corrected_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = corrected_date

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

        if selected_start["value"]:
            end_date_picker.first_date = selected_start["value"]
        else:
            end_date_picker.first_date = datetime.datetime(2000, 1, 1)

        if selected_end["value"]:
            end_date_picker.value = selected_end["value"]
        elif selected_start["value"]:
            end_date_picker.value = selected_start["value"]

        end_date_picker.open = True
        page.update()

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
        width=140,
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

    search_field = ft.TextField(
        width=185,
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
                expand=True,
                spacing=row_spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell("No", col_expand["no"], 0, ft.FontWeight.W_700),
                    build_table_cell("거래처ID", col_expand["supplier_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("거래처명", col_expand["supplier_name"], -1, ft.FontWeight.W_700),
                    build_table_cell("사업자번호", col_expand["brn"], 0, ft.FontWeight.W_700),
                    build_table_cell("연락상태", col_expand["is_contact_status"], 0, ft.FontWeight.W_700),
                    build_table_cell("지정결제일", col_expand["designated_payment_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("예정결제일", col_expand["scheduled_payment_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("담당자ID", col_expand["employee_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("메모", col_expand["memo"], -1, ft.FontWeight.W_700),
                    build_table_cell("담당자명", col_expand["sup_manager"], -1, ft.FontWeight.W_700),
                    build_table_cell("전화번호", col_expand["phone"], 0, ft.FontWeight.W_700),
                    build_table_cell("최종수정일", col_expand["last_update"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        contact_color = "#16A34A" if row.get("is_contact_status", "") == "활성" else "#6B7280"

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
                expand=True,
                spacing=row_spacing,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell(row.get("no", ""), col_expand["no"], 0),
                    build_table_cell(row.get("supplier_id", ""), col_expand["supplier_id"], 0),
                    build_table_cell(row.get("supplier_name", ""), col_expand["supplier_name"], -1),
                    build_table_cell(row.get("brn", ""), col_expand["brn"], 0),
                    build_table_cell(
                        row.get("is_contact_status", ""),
                        col_expand["is_contact_status"],
                        0,
                        ft.FontWeight.W_700,
                        contact_color,
                    ),
                    build_table_cell(row.get("designated_payment_date", ""), col_expand["designated_payment_date"], 0),
                    build_table_cell(row.get("scheduled_payment_date", ""), col_expand["scheduled_payment_date"], 0),
                    build_table_cell(row.get("employee_id", ""), col_expand["employee_id"], 0),
                    build_table_cell(row.get("memo", ""), col_expand["memo"], -1),
                    build_table_cell(row.get("sup_manager", ""), col_expand["sup_manager"], -1),
                    build_table_cell(row.get("phone", ""), col_expand["phone"], 0),
                    build_table_cell(row.get("last_update", ""), col_expand["last_update"], 0),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()
        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def build_pagination():
        total_pages = pagination_state["total_pages"]
        current_page = pagination_state["current_page"]

        if total_pages <= 1:
            pagination_holder.content = None
            return

        def move_page(target_page: int):
            if target_page < 1:
                return
            if target_page > total_pages:
                return
            run_search(target_page)

        start_page = max(1, current_page - 2)
        end_page = min(total_pages, start_page + 4)

        # ☑️ 끝 페이지가 5개보다 적게 보이면 시작 페이지를 다시 보정
        if end_page - start_page < 4:
            start_page = max(1, end_page - 4)

        page_buttons = []

        page_buttons.append(
            action_button(
                "이전",
                on_click=lambda e: move_page(current_page - 1) if current_page > 1 else None,
                width=60,
            )
        )

        for page_no in range(start_page, end_page + 1):
            is_current = page_no == current_page
            page_buttons.append(
                ft.Container(
                    width=38,
                    height=38,
                    bgcolor="#111827" if is_current else BUTTON_BG,
                    border=ft.Border.all(1, BUTTON_BORDER),
                    border_radius=6,
                    alignment=ft.Alignment(0, 0),
                    on_click=None if is_current else (lambda e, p=page_no: move_page(p)),
                    content=ft.Text(
                        value=str(page_no),
                        size=13,
                        color=ft.Colors.WHITE if is_current else BUTTON_TEXT,
                        weight=ft.FontWeight.W_600,
                    ),
                )
            )

        page_buttons.append(
            action_button(
                "다음",
                on_click=lambda e: move_page(current_page + 1) if current_page < total_pages else None,
                width=60,
            )
        )

        pagination_holder.content = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
            controls=page_buttons,
        )

    # =========================================================
    # ☑️ SQLAlchemy ORM: 거래처 count/list 조회
    # - SQL 문자열을 직접 실행하지 않고 SupplierModel 기반 ORM 함수 사용
    # - 검색조건/날짜조건은 ORM filter로 처리
    # =========================================================
    def get_selected_date_text(value):
        if not value:
            return None
        return value.strftime("%Y-%m-%d")

    def fetch_total_count(keyword: str):
        return count_suppliers(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=get_selected_date_text(selected_start["value"]),
            end_date=get_selected_date_text(selected_end["value"]),
        )

    def fetch_supplier_rows(keyword: str, page_no: int):
        offset = (page_no - 1) * PAGE_SIZE
        raw_rows = fetch_suppliers(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=get_selected_date_text(selected_start["value"]),
            end_date=get_selected_date_text(selected_end["value"]),
        )
        return supplier_db_row_adapter(raw_rows, page_no)

    def run_search(page_no: int = 1):
        keyword = (search_field.value or "").strip()

        total_count = fetch_total_count(keyword)
        total_pages = max(1, math.ceil(total_count / PAGE_SIZE))

        # ☑️ 현재 페이지가 총 페이지보다 커지는 상황 방지
        if page_no > total_pages:
            page_no = total_pages
        if page_no < 1:
            page_no = 1

        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = total_pages
        pagination_state["current_page"] = page_no
        pagination_state["keyword"] = keyword

        rows_state.clear()
        rows_state.extend(fetch_supplier_rows(keyword, page_no))

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

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"전체 조회 건수: {total_count}건 / "
            f"현재 페이지: {page_no}/{total_pages}"
        )

        refresh_table(rows_state)
        build_pagination()

    search_field.on_submit = lambda e: run_search(1)

    def on_print(e):
        result_text.value = "인쇄 기능은 아직 연결 전입니다."
        e.page.update()

    def on_download(e):
        result_text.value = "다운로드 기능은 아직 연결 전입니다."
        e.page.update()

    def close_register_modal(e):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        e.page.update()

    def clear_register_session(page: ft.Page):
        for field in SUPPLIER_FIELDS:
            page.session.store.set(f"{SESSION_PREFIX}_{field['key']}", "")

    def handle_register_success(saved_data: dict):
        create_supplier(saved_data)
        run_search(1)

    def open_register_modal(e):
        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="거래처 등록",
            edit_title="거래처 정보 수정",
            fields=SUPPLIER_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_register_modal,
            on_submit_success=handle_register_success,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        e.page.update()

    dim_bg.on_click = close_register_modal

    refresh_picker_fields()
    run_search(1)

    action_controls = [
        action_button("조회", on_click=lambda e: run_search(1), width=78),
        action_button("인쇄", on_click=on_print, width=78),
        action_button("다운로드", on_click=on_download, width=92),
        action_button("등록", on_click=open_register_modal, width=78),
    ]

    table_section = ft.Container(
        bgcolor=CARD_BG,
        border=ft.Border.all(1, TABLE_BORDER),
        border_radius=8,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            spacing=0,
            controls=[
                build_table_header(),
                table_rows_holder,
            ],
        ),
    )

    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Stack(
            expand=True,
            controls=[
                ft.Column(
                    scroll=ft.ScrollMode.AUTO,
                    spacing=16,
                    controls=[
                        ft.Text(
                            value=page_title,
                            size=24,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Row(
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                start_field_holder,
                                start_icon_holder,
                                ft.Text("~", size=14, color=TEXT_SECONDARY),
                                end_field_holder,
                                end_icon_holder,
                                ft.Container(width=12),
                                search_type,
                                search_field,
                                *action_controls,
                            ],
                        ),
                        result_text,
                        table_section,
                        pagination_holder,
                    ],
                ),
                dim_bg,
                popup_layer,
            ],
        ),
    )