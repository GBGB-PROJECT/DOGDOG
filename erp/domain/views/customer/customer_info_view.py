import math
import flet as ft
import datetime

from components import common as cm
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import CUSTOMER_FIELDS
# 🔥 requests 방식 API 호출로 변경
from api.erp_requests_api import count_customers, fetch_customers, create_customer


# =========================================================
# ☑️ product_master_view 스타일 참고용 공통 색상
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

SESSION_PREFIX = "customer"
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


def customer_row_adapter(saved_data: dict, next_no: int):
    subscribed_raw = str(saved_data.get("is_subscribed", "") or "").strip().lower()
    active_raw = str(saved_data.get("active", "") or "").strip().lower()

    subscribed_text = "Y" if subscribed_raw in ["true", "1", "y", "yes", "구독", "사용", "활성"] else "N"
    active_text = "활성" if active_raw in ["true", "1", "y", "yes", "활성", "사용"] else "비활성"

    return {
        "no": str(next_no),
        "customer_id": saved_data.get("customer_id", ""),
        "email": saved_data.get("email", ""),
        "oauth_type": saved_data.get("oauth_type", ""),
        "nickname": saved_data.get("nickname", ""),
        "phone": saved_data.get("phone", ""),
        "is_subscribed": subscribed_text,
        "subs_count": saved_data.get("subs_count", ""),
        "active": active_text,
        "create_date": saved_data.get("create_date", ""),
    }


def customer_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "customer_id": row.get("customer_id", ""),
                "email": row.get("email", ""),
                "oauth_type": row.get("oauth_type", ""),
                "nickname": row.get("nickname", ""),
                "phone": row.get("phone", ""),
                "is_subscribed": "Y" if row.get("is_subscribed") else "N",
                "subs_count": row.get("subs_count", ""),
                "active": "활성" if row.get("active") else "비활성",
                "create_date": row.get("create_date", ""),
            }
        )

    return rows


# 🔥 수정: 기존 customer_view.py의 고객 목록/검색/등록 화면을 고객 정보 관리 전용 화면으로 분리
def erp_customer_info_view():
    # 🔥 수정: 고객관리 대분류가 아니라 고객 정보 관리 하위 화면 제목으로 변경
    page_title = "고객 정보 관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "customer_id"}

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
        value="불러오는 중입니다.",
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
        "customer_id": 6,
        "email": 10,
        "oauth_type": 6,
        "nickname": 7,
        "phone": 8,
        "is_subscribed": 5,
        "subs_count": 5,
        "active": 5,
        "create_date": 6,
    }

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_type_labels = {
        "customer_id": "고객ID",
        "email": "이메일",
        "oauth_type": "OAuth유형",
        "nickname": "닉네임",
        "phone": "전화번호",
        "is_subscribed": "구독여부",
        "subs_count": "구독횟수",
        "active": "상태",
        "create_date": "가입일",
    }

    def format_date_text(value):
        if not value:
            return ""
        return value.strftime("%Y.%m.%d")

    def get_selected_date_range():
        start_date = None
        end_date = None

        if selected_start["value"]:
            start_date = selected_start["value"].date()

        if selected_end["value"]:
            end_date = selected_end["value"].date()

        return start_date, end_date

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
            corrected_date = corrected_date.replace(tzinfo=None)
            selected_start["value"] = corrected_date

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            corrected_date = e.control.value + datetime.timedelta(hours=9)
            corrected_date = corrected_date.replace(tzinfo=None)

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
        width=160,
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
                    build_table_cell("고객ID", col_expand["customer_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("이메일", col_expand["email"], 0, ft.FontWeight.W_700),
                    build_table_cell("OAuth유형", col_expand["oauth_type"], 0, ft.FontWeight.W_700),
                    build_table_cell("닉네임", col_expand["nickname"], 0, ft.FontWeight.W_700),
                    build_table_cell("전화번호", col_expand["phone"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독여부", col_expand["is_subscribed"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독횟수", col_expand["subs_count"], 0, ft.FontWeight.W_700),
                    build_table_cell("상태", col_expand["active"], 0, ft.FontWeight.W_700),
                    build_table_cell("가입일", col_expand["create_date"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        subscribe_color = "#16A34A" if row.get("is_subscribed", "") == "Y" else "#DC2626"
        active_color = "#2563EB" if row.get("active", "") == "활성" else "#6B7280"

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
                    build_table_cell(row.get("customer_id", ""), col_expand["customer_id"], 0),
                    build_table_cell(row.get("email", ""), col_expand["email"], 0),
                    build_table_cell(row.get("oauth_type", ""), col_expand["oauth_type"], 0),
                    build_table_cell(row.get("nickname", ""), col_expand["nickname"], 0),
                    build_table_cell(row.get("phone", ""), col_expand["phone"], 0),
                    build_table_cell(
                        row.get("is_subscribed", ""),
                        col_expand["is_subscribed"],
                        0,
                        ft.FontWeight.W_700,
                        subscribe_color,
                    ),
                    build_table_cell(row.get("subs_count", ""), col_expand["subs_count"], 0),
                    build_table_cell(
                        row.get("active", ""),
                        col_expand["active"],
                        0,
                        ft.FontWeight.W_700,
                        active_color,
                    ),
                    build_table_cell(row.get("create_date", ""), col_expand["create_date"], 0),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    # =========================================================
    # ☑️ SQLAlchemy ORM: 고객 count/list 조회
    # - 날짜 필터를 repository로 내려서 count/fetch 기준을 통일
    # =========================================================
    def fetch_total_count(keyword=""):
        start_date, end_date = get_selected_date_range()

        return count_customers(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )

    def fetch_customer_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        db_rows = fetch_customers(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return customer_db_row_adapter(db_rows, page_no)

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

    def update_result_text():
        start_text = format_date_text(selected_start["value"]) or "미선택"
        end_text = format_date_text(selected_end["value"]) or "미선택"
        search_label = search_type_labels.get(search_type_value["value"], "고객ID")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 페이지 {pagination_state['total_count']}건 / "
            f"현재 페이지 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]

        total_count = fetch_total_count(keyword=keyword)
        total_pages = max(1, math.ceil(total_count / PAGE_SIZE))

        if current_page > total_pages:
            current_page = total_pages
            pagination_state["current_page"] = current_page

        rows = fetch_customer_rows(keyword=keyword, page_no=current_page)

        rows_state.clear()
        rows_state.extend(rows)

        pagination_state["total_count"] = total_count
        pagination_state["total_pages"] = total_pages

        refresh_table(rows_state)
        refresh_pagination()
        update_result_text()

    def on_search_click(e):
        pagination_state["keyword"] = (search_field.value or "").strip()
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page
        reload_current_page()
        e.page.update()

    def on_register_success(saved_data: dict):
        created = create_customer(saved_data)
        next_no = ((pagination_state["current_page"] - 1) * PAGE_SIZE) + len(rows_state) + 1
        rows_state.append(customer_row_adapter(created, next_no))

        pagination_state["keyword"] = ""
        search_field.value = ""
        pagination_state["current_page"] = 1
        pagination_state["total_count"] = fetch_total_count(keyword="")
        pagination_state["total_pages"] = max(1, math.ceil(pagination_state["total_count"] / PAGE_SIZE))

        reload_current_page()

    def close_popup(e=None):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        if e and e.page:
            e.page.update()

    def open_register_modal(e):
        modal = build_modal(
            page=e.page,
            register_title="고객 정보 등록",
            edit_title="고객 정보 수정",
            fields=CUSTOMER_FIELDS,
            session_prefix=SESSION_PREFIX,
            close_handler=close_popup,
            on_submit_success=on_register_success,
        )

        dim_bg.visible = True
        popup_layer.visible = True
        popup_layer.content = modal
        e.page.update()

    refresh_picker_fields()

    # =========================================================
    # ☑️ 최초 진입 시 전체 고객 목록 자동 조회
    # =========================================================
    pagination_state["keyword"] = ""
    pagination_state["current_page"] = 1
    reload_current_page()

    page_content = ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor="#F3F4F6",
                padding=ft.Padding.only(left=24, right=24, top=18, bottom=14),
                content=ft.Row(
                    wrap=True,
                    spacing=12,
                    run_spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        start_field_holder,
                        start_icon_holder,
                        ft.Text("~", size=18, color="#374151", weight=ft.FontWeight.W_600),
                        end_field_holder,
                        end_icon_holder,
                        search_type,
                        search_field,
                        action_button("조회", on_click=on_search_click),
                        action_button("인쇄"),
                        action_button("다운로드", width=92),
                        action_button("등록", on_click=open_register_modal),
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                bgcolor="#F5F5F5",
                padding=ft.Padding.only(left=24, right=24, top=26, bottom=18),
                content=ft.Column(
                    expand=True,
                    spacing=18,
                    controls=[
                        ft.Text(
                            value=page_title,
                            size=22,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        result_text,
                        ft.Container(
                            expand=True,
                            bgcolor=CARD_BG,
                            border_radius=10,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
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
                        pagination_holder,
                    ],
                ),
            ),
        ],
    )

    root = ft.Stack(
        expand=True,
        controls=[
            page_content,
            dim_bg,
            popup_layer,
        ],
    )

    return root