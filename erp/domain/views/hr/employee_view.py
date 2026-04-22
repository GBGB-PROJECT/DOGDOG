import math
import flet as ft
import datetime

from components import common as cm
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import EMPLOYEE_FIELDS
from backend.erp.service.erp_query_service import count_employees, fetch_employees


# =========================================================
# ☑️ merchandise_master_view 스타일 참고용 공통 색상
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

SESSION_PREFIX = "employee"
PAGE_SIZE = 50


# =========================================================
# ☑️ 공통 텍스트
# =========================================================
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


# =========================================================
# ☑️ 날짜 표시 필드
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
        content=ft.Text(
            value=text,
            size=13,
            color=FIELD_TEXT,
            weight=ft.FontWeight.W_500,
        ),
    )


# =========================================================
# ☑️ 달력 버튼
# =========================================================
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


# =========================================================
# ☑️ 공통 액션 버튼
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
        content=ft.Text(
            value=text,
            size=13,
            color=BUTTON_TEXT,
            weight=ft.FontWeight.W_500,
        ),
    )


# =========================================================
# ☑️ 테이블 셀 공통
# =========================================================
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


# =========================================================
# ☑️ 저장 데이터 -> 사원 테이블 row 변환
# - EMPLOYEE_FIELDS 실제 key 기준
# =========================================================
def employee_row_adapter(saved_data: dict, next_no: int):
    active_raw = (saved_data.get("active", "") or "").strip().lower()

    if active_raw in ["true", "1", "y", "yes", "재직", "활성", "사용"]:
        active_text = "재직"
    else:
        active_text = "비활성"

    return {
        "no": str(next_no),
        "employee_id": saved_data.get("employee_id", ""),
        "account_id": saved_data.get("account_id", ""),
        "username": saved_data.get("username", ""),
        "hire_date": saved_data.get("hire_date", ""),
        "quit_date": saved_data.get("quit_date", ""),
        "emp_position_id": saved_data.get("emp_position_id", ""),
        "manager_id": saved_data.get("manager_id", ""),
        "email": saved_data.get("email", ""),
        "phone": saved_data.get("phone", ""),
        "address": saved_data.get("address", ""),
        "postal_code": saved_data.get("postal_code", ""),
        "active": active_text,
    }


# =========================================================
# ☑️ DB row -> 사원 테이블 row 변환
# - EmployeeModel 결과 기준
# =========================================================
def employee_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "employee_id": row.get("employee_id", ""),
                "account_id": row.get("account_id", ""),
                "username": row.get("username", ""),
                "hire_date": row.get("hire_date", ""),
                "quit_date": row.get("quit_date", ""),
                "emp_position_id": row.get("emp_position_id", ""),
                "manager_id": row.get("manager_id", ""),
                "email": row.get("email", ""),
                "phone": row.get("phone", ""),
                "address": row.get("address", ""),
                "postal_code": row.get("postal_code", ""),
                "active": "재직" if row.get("active") else "비활성",
            }
        )

    return rows


# =========================================================
# ☑️ 인사관리 화면
# =========================================================
def erp_employee_view():
    page_title = "인사관리 > 사원관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "username"}

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
        "no": 3,
        "employee_id": 5,
        "account_id": 7,
        "username": 7,
        "hire_date": 7,
        "quit_date": 7,
        "emp_position_id": 6,
        "manager_id": 6,
        "email": 12,
        "phone": 10,
        "address": 12,
        "postal_code": 6,
        "active": 5,
    }

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_type_labels = {
        "username": "이름",
        "employee_id": "사원ID",
        "account_id": "계정ID",
        "emp_position_id": "직급ID",
        "phone": "전화번호",
        "email": "이메일",
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
                    build_table_cell("사원ID", col_expand["employee_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("계정ID", col_expand["account_id"], -1, ft.FontWeight.W_700),
                    build_table_cell("이름", col_expand["username"], -1, ft.FontWeight.W_700),
                    build_table_cell("입사일", col_expand["hire_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("퇴사일", col_expand["quit_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("직급ID", col_expand["emp_position_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("관리자ID", col_expand["manager_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("이메일", col_expand["email"], -1, ft.FontWeight.W_700),
                    build_table_cell("전화번호", col_expand["phone"], -1, ft.FontWeight.W_700),
                    build_table_cell("주소", col_expand["address"], -1, ft.FontWeight.W_700),
                    build_table_cell("우편번호", col_expand["postal_code"], 0, ft.FontWeight.W_700),
                    build_table_cell("상태", col_expand["active"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        active_color = "#166534" if row.get("active") == "재직" else "#991B1B"

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
                    build_table_cell(row.get("employee_id", ""), col_expand["employee_id"], 0),
                    build_table_cell(row.get("account_id", ""), col_expand["account_id"], -1),
                    build_table_cell(row.get("username", ""), col_expand["username"], -1),
                    build_table_cell(row.get("hire_date", ""), col_expand["hire_date"], 0),
                    build_table_cell(row.get("quit_date", ""), col_expand["quit_date"], 0),
                    build_table_cell(row.get("emp_position_id", ""), col_expand["emp_position_id"], 0),
                    build_table_cell(row.get("manager_id", ""), col_expand["manager_id"], 0),
                    build_table_cell(row.get("email", ""), col_expand["email"], -1),
                    build_table_cell(row.get("phone", ""), col_expand["phone"], -1),
                    build_table_cell(row.get("address", ""), col_expand["address"], -1),
                    build_table_cell(row.get("postal_code", ""), col_expand["postal_code"], 0),
                    build_table_cell(
                        row.get("active", ""),
                        col_expand["active"],
                        0,
                        ft.FontWeight.W_700,
                        active_color,
                    ),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def apply_date_filter(rows):
        filtered_rows = []

        for row in rows:
            is_match = True
            hire_date_value = str(row.get("hire_date", "")).strip()

            if hire_date_value:
                try:
                    date_text = hire_date_value[:10]
                    hire_date_obj = datetime.datetime.strptime(date_text, "%Y-%m-%d")

                    if (
                        selected_start["value"]
                        and hire_date_obj < selected_start["value"].replace(
                            hour=0,
                            minute=0,
                            second=0,
                            microsecond=0,
                        )
                    ):
                        is_match = False

                    if (
                        selected_end["value"]
                        and hire_date_obj > selected_end["value"].replace(
                            hour=0,
                            minute=0,
                            second=0,
                            microsecond=0,
                        )
                    ):
                        is_match = False

                except ValueError:
                    pass

            if is_match:
                filtered_rows.append(row)

        return filtered_rows

    # =========================================================
    # ☑️ SQLAlchemy ORM: 사원 count/list 조회
    # - SQL 문자열을 직접 실행하지 않고 EmployeeModel 기반 ORM 함수 사용
    # =========================================================
    def fetch_total_count(keyword=""):
        return count_employees(
            search_type=search_type_value["value"],
            keyword=keyword,
        )

    def fetch_employee_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE

        db_rows = fetch_employees(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
        )

        return employee_db_row_adapter(db_rows, page_no)

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

        fetched_rows = fetch_employee_rows(keyword, current_page)
        filtered_rows = apply_date_filter(fetched_rows)

        rows_state.clear()
        rows_state.extend(filtered_rows)

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

    search_field.on_submit = lambda e: (run_search(e.page), e.page.update())

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
        for field in EMPLOYEE_FIELDS:
            page.session.store.set(f"{SESSION_PREFIX}_{field['key']}", "")

    def handle_register_success(saved_data: dict):
        next_no = len(rows_state) + 1
        new_row = employee_row_adapter(saved_data, next_no)

        rows_state.append(new_row)
        refresh_table(rows_state)

    def open_register_modal(e):
        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="사원 등록",
            edit_title="사원 정보 수정",
            fields=EMPLOYEE_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_register_modal,
            on_submit_success=handle_register_success,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        e.page.update()

    dim_bg.on_click = close_register_modal

    refresh_picker_fields()

    try:
        load_rows()
    except Exception as exc:
        result_text.value = f"DB 조회 실패: {exc}"

    action_controls = [
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
    ]

    filter_bar = ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=ft.Padding.only(left=20, right=20, top=12, bottom=12),
        content=ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                start_field_holder,
                start_icon_holder,
                ft.Text(
                    value="~",
                    size=16,
                    color="#374151",
                    weight=ft.FontWeight.W_500,
                ),
                end_field_holder,
                end_icon_holder,
                search_type,
                search_field,
                *action_controls,
            ],
        ),
    )

    table_area = ft.Container(
        expand=True,
        border=ft.border.all(1, TABLE_BORDER),
        border_radius=10,
        bgcolor=CARD_BG,
        content=ft.Column(
            spacing=0,
            controls=[
                build_table_header(),
                table_rows_holder,
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
        content=ft.Stack(
            expand=True,
            controls=[
                main_content,
                dim_bg,
                popup_layer,
            ],
        ),
    )