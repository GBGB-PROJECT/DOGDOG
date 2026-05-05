import math
import flet as ft
import datetime

from components import common as cm
# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_customers, fetch_customers, fetch_customers_page
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button, build_expand_table_cell as build_table_cell
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages, build_pagination_bar
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area


# =========================================================
# ☑️ product_master_view 스타일 참고용 공통 색상
# =========================================================
def _to_yn(value):
    # 🔥 수정: API에서 "Y" / "N" 문자열로 내려오는 경우까지 정확히 처리
    # - 기존 코드: "N" 문자열도 비어있지 않아 True로 판정되어 화면에서 전부 Y처럼 보였음
    # - 구독여부 검색 n/f/false 결과가 N이어도 화면에서 Y로 보이는 문제 해결
    if isinstance(value, bool):
        return "Y" if value else "N"

    if value is None:
        return "N"

    text = str(value).strip().lower()

    true_words = {
        "y",
        "yes",
        "true",
        "t",
        "1",
        "구독",
        "구독함",
        "구독중",
        "사용",
        "활성",
    }

    false_words = {
        "n",
        "no",
        "false",
        "f",
        "0",
        "",
        "미구독",
        "비구독",
        "구독안함",
        "해지",
        "비활성",
        "미사용",
    }

    if text in true_words:
        return "Y"

    if text in false_words:
        return "N"

    return "N"


def _to_active_text(value):
    # 🔥 수정: API에서 "비활성" 문자열로 내려오는 경우도 정확히 처리
    if isinstance(value, bool):
        return "활성" if value else "비활성"

    if value is None:
        return "비활성"

    text = str(value).strip().lower()

    true_words = {
        "활성",
        "active",
        "y",
        "yes",
        "true",
        "t",
        "1",
        "사용",
    }

    false_words = {
        "비활성",
        "inactive",
        "n",
        "no",
        "false",
        "f",
        "0",
        "",
        "미사용",
    }

    if text in true_words:
        return "활성"

    if text in false_words:
        return "비활성"

    return "비활성"
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
                # 🔥 수정: API 응답 "N" 문자열을 True처럼 오판하지 않도록 변환 함수 사용
                "is_subscribed": _to_yn(row.get("is_subscribed")),
                "subs_count": row.get("subs_count", ""),
                "active": _to_active_text(row.get("active")),
                "create_date": row.get("create_date", ""),
            }
        )

    return rows


# 🔥 수정: 기존 customer_view.py의 고객 목록/검색 화면을 고객 정보 관리 전용 화면으로 분리
def erp_customer_info_view():
    # 🔥 수정: 고객관리 대분류가 아니라 고객 정보 관리 하위 화면 제목으로 변경
    page_title = "고객 정보 관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "email"}

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

    # 🔥 추가: 검색/날짜 조건 사용 후에만 보이는 초기화 버튼 자리
    reset_button_holder = ft.Container(visible=False)

    col_expand = {
        "no": 3,
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
        "email": "이메일",
        "oauth_type": "OAuth유형",
        "nickname": "닉네임",
        "phone": "전화번호",
        "is_subscribed": "구독여부",
        "subs_count": "구독횟수",
        "active": "상태",
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
            corrected_date = normalize_datepicker_value(e.control.value)
            corrected_date = corrected_date.replace(tzinfo=None)
            selected_start["value"] = corrected_date

            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        update_reset_button_visibility()
        e.page.update()

    def on_end_date_change(e):
        if e.control.value:
            corrected_date = normalize_datepicker_value(e.control.value)
            corrected_date = corrected_date.replace(tzinfo=None)

            if selected_start["value"] and corrected_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = corrected_date

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

    def update_reset_button_visibility():
        # 🔥 추가: 기본 상태가 아니면 초기화 버튼 표시
        has_filter = (
            selected_start["value"] is not None
            or selected_end["value"] is not None
            or (search_field.value or "").strip() != ""
            or search_type_value["value"] != "email"
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
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    value=label,
                    size=13,
                    color=FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                ),
            ),
            on_click=lambda e: set_search_type(value, e.page),
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

    def fetch_customer_page(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        result = fetch_customers_page(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "rows": customer_db_row_adapter(result["items"], page_no),
            "pagination": result["pagination"],
        }

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
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
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
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
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
            lambda page_no, e: e.page.run_thread(lambda: move_page(page_no, e.page)),
        )

    def update_result_text():
        start_text = format_date_text(selected_start["value"]) or "미선택"
        end_text = format_date_text(selected_end["value"]) or "미선택"
        search_label = search_type_labels.get(search_type_value["value"], "이메일")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간기준: 가입일 / "
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

        page_result = fetch_customer_page(keyword=keyword, page_no=current_page)
        pagination = page_result["pagination"]
        total_count = pagination.get("total_count", 0)
        total_pages = pagination.get("total_pages") or calc_total_pages(total_count, PAGE_SIZE)

        if current_page > total_pages:
            current_page = total_pages
            pagination_state["current_page"] = current_page
            page_result = fetch_customer_page(keyword=keyword, page_no=current_page)
            pagination = page_result["pagination"]
            total_count = pagination.get("total_count", 0)
            total_pages = pagination.get("total_pages") or calc_total_pages(total_count, PAGE_SIZE)

        rows = page_result["rows"]

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
        update_reset_button_visibility()
        e.page.update()

    def on_reset_click(e):
        # 🔥 추가: 검색/날짜 조건을 전부 기본값으로 되돌리고 첫 화면 재조회
        selected_start["value"] = None
        selected_end["value"] = None

        search_type_value["value"] = "email"
        search_type_text.value = search_type_labels["email"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1
        pagination_state["page_ref"] = e.page

        refresh_picker_fields()
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨겨두고, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78, run_async=True)
    update_reset_button_visibility()

    # =========================================================
    # ☑️ 최초 진입 시 전체 고객 목록 자동 조회
    # =========================================================
    pagination_state["keyword"] = ""
    pagination_state["current_page"] = 1

    table_area = build_lookup_table_area(build_table_header(), table_rows_holder)

    page_layout = build_lookup_page_layout(
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
            search_type,
            search_field,
            action_button("조회", on_click=on_search_click, run_async=True),
            reset_button_holder,
        ],
    )

    class CustomerInfoPage(ft.Container):
        def did_mount(self):
            self.page.run_thread(lambda: (reload_current_page(), self.page.update()))

    return CustomerInfoPage(expand=True, content=page_layout)
