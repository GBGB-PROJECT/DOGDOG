import math
import datetime
import flet as ft

# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_customer_subscriptions, fetch_customer_subscriptions


# =========================================================
# 🔥 고객 구독 관리 화면
# - 컬럼 순서 재배치
# - 이름 / 구독ID / 고객ID / 플랜ID 같은 고객 관련 정보는 좌측
# - 구독상태는 가장 우측
# - 나머지 순서:
#   신청요일 / 자동배송 / 배송주기 / 할인율 / 배송지 / 전화번호 / 구독시작일
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

PAGE_SIZE = 50


def build_text(value, size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_400):
    return ft.Text(
        value=str(value or ""),
        size=size,
        color=color,
        weight=weight,
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


def build_table_cell(text, expand, align_x=0, weight=ft.FontWeight.W_400, color=TEXT_ROW):
    return ft.Container(
        expand=expand,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=text,
            size=12,
            color=color,
            weight=weight,
        ),
    )


def format_datetime_text(value):
    if not value:
        return ""
    return str(value)[:19]


def customer_subscription_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "name": row.get("name", ""),                    # 🔥 좌측 배치
                "subs_id": row.get("subs_id", ""),
                "customer_id": row.get("customer_id", ""),
                "subs_plan_id": row.get("subs_plan_id", ""),
                "subs_day": row.get("subs_day", ""),
                "is_auto_delivery": row.get("is_auto_delivery", ""),
                "delivery_cycle": row.get("delivery_cycle", ""),
                "subs_sale": row.get("subs_sale", ""),
                "address": row.get("address", ""),
                "phone": row.get("phone", ""),
                "subs_date": format_datetime_text(row.get("subs_date", "")),
                "is_subs_status": row.get("is_subs_status", ""),  # 🔥 극우측 배치
            }
        )

    return rows


def erp_customer_subscription_view():
    page_title = "고객 구독 관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "subs_id"}

    pagination_state = {
        "current_page": 1,
        "total_count": 0,
        "total_pages": 1,
        "keyword": "",
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

    # =========================================================
    # 🔥 수정: 컬럼 순서 변경에 맞춰 비율 재조정
    # =========================================================
    col_expand = {
        "no": 3,
        "name": 6,
        "subs_id": 4,
        "customer_id": 4,
        "subs_plan_id": 4,
        "subs_day": 5,
        "is_auto_delivery": 4,
        "delivery_cycle": 4,
        "subs_sale": 4,
        "address": 10,
        "phone": 7,
        "subs_date": 8,
        "is_subs_status": 5,
    }

    search_type_labels = {
        "subs_id": "구독ID",
        "customer_id": "고객ID",
        "subs_plan_id": "구독플랜",
        "is_auto_delivery": "자동배송",
        "is_subs_status": "구독상태",
        "subs_day": "신청요일",
        "delivery_cycle": "배송주기",
        "subs_sale": "할인율",
        "address": "배송지",
        "name": "이름",
        "phone": "전화번호",
    }

    def format_date_text(value):
        if not value:
            return ""
        return value.strftime("%Y.%m.%d")

    def get_selected_date_range():
        start_date = selected_start["value"].date() if selected_start["value"] else None
        end_date = selected_end["value"].date() if selected_end["value"] else None
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
        update_reset_button_visibility()
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

        end_date_picker.first_date = selected_start["value"] or datetime.datetime(2000, 1, 1)

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
            or search_type_value["value"] != "subs_id"
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
        width=170,
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
        hint_style=ft.TextStyle(
            size=13,
            color=HINT_TEXT,
        ),
        text_size=13,
        border_color=FIELD_BORDER,
        border_radius=6,
        bgcolor=FIELD_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
    )

    def build_table_header():
        return ft.Container(
            bgcolor=TABLE_HEADER_BG,
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            content=ft.Row(
                expand=True,
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell("No", col_expand["no"], 0, ft.FontWeight.W_700),
                    build_table_cell("이름", col_expand["name"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독ID", col_expand["subs_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("고객ID", col_expand["customer_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독플랜", col_expand["subs_plan_id"], 0, ft.FontWeight.W_700),
                    build_table_cell("신청요일", col_expand["subs_day"], 0, ft.FontWeight.W_700),
                    build_table_cell("자동배송", col_expand["is_auto_delivery"], 0, ft.FontWeight.W_700),
                    build_table_cell("배송주기", col_expand["delivery_cycle"], 0, ft.FontWeight.W_700),
                    build_table_cell("할인율", col_expand["subs_sale"], 0, ft.FontWeight.W_700),
                    build_table_cell("배송지", col_expand["address"], 0, ft.FontWeight.W_700),
                    build_table_cell("전화번호", col_expand["phone"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독시작일", col_expand["subs_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독상태", col_expand["is_subs_status"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        status_color = "#059669" if row.get("is_subs_status") == "구독중" else "#F97316"

        return ft.Container(
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            content=ft.Row(
                expand=True,
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_table_cell(row.get("no", ""), col_expand["no"], 0),
                    build_table_cell(row.get("name", ""), col_expand["name"], 0),
                    build_table_cell(row.get("subs_id", ""), col_expand["subs_id"], 0),
                    build_table_cell(row.get("customer_id", ""), col_expand["customer_id"], 0),
                    build_table_cell(row.get("subs_plan_id", ""), col_expand["subs_plan_id"], 0),
                    build_table_cell(row.get("subs_day", ""), col_expand["subs_day"], 0),
                    build_table_cell(row.get("is_auto_delivery", ""), col_expand["is_auto_delivery"], 0),
                    build_table_cell(row.get("delivery_cycle", ""), col_expand["delivery_cycle"], 0),
                    build_table_cell(row.get("subs_sale", ""), col_expand["subs_sale"], 0),
                    build_table_cell(row.get("address", ""), col_expand["address"], 0),
                    build_table_cell(row.get("phone", ""), col_expand["phone"], 0),
                    build_table_cell(row.get("subs_date", ""), col_expand["subs_date"], 0),
                    build_table_cell(
                        row.get("is_subs_status", ""),
                        col_expand["is_subs_status"],
                        0,
                        ft.FontWeight.W_700,
                        status_color,
                    ),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()

        if not filtered_rows:
            table_rows_holder.controls.append(
                ft.Container(
                    height=120,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        value="일치하는 정보가 없습니다.",
                        size=14,
                        color=TEXT_SECONDARY,
                    ),
                )
            )
            return

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def fetch_total_count(keyword=""):
        start_date, end_date = get_selected_date_range()

        return count_customer_subscriptions(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )

    def fetch_customer_subscription_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        db_rows = fetch_customer_subscriptions(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return customer_subscription_db_row_adapter(db_rows, page_no)

    def move_page(page_no: int, page: ft.Page):
        if page_no < 1 or page_no > pagination_state["total_pages"]:
            return

        pagination_state["current_page"] = page_no
        reload_current_page()
        page.update()

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        return ft.Container(
            width=40,
            height=40,
            border_radius=10,
            bgcolor="#2563EB" if selected else ft.Colors.TRANSPARENT,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e: move_page(page_no, e.page),
            content=ft.Text(
                value=label,
                size=16,
                color=ft.Colors.WHITE if selected else "#0F172A",
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
            ),
        )

    def refresh_pagination():
        total_pages = pagination_state["total_pages"]
        current_page = pagination_state["current_page"]

        if total_pages <= 1:
            pagination_holder.content = None
            return

        page_controls = []

        page_controls.append(
            build_page_button("<", current_page - 1, disabled=(current_page == 1))
        )

        start_page = max(1, current_page - 2)
        end_page = min(total_pages, current_page + 2)

        for page_no in range(start_page, end_page + 1):
            page_controls.append(
                build_page_button(
                    str(page_no),
                    page_no,
                    selected=(page_no == current_page),
                )
            )

        page_controls.append(
            build_page_button(">", current_page + 1, disabled=(current_page == total_pages))
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
        search_label = search_type_labels.get(search_type_value["value"], "구독ID")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간기준: 구독시작일 / "
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 {pagination_state['total_count']}건 / "
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

        rows = fetch_customer_subscription_rows(keyword=keyword, page_no=current_page)

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
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    def on_reset_click(e):
        # 🔥 추가: 검색/날짜 조건을 전부 기본값으로 되돌리고 첫 화면 재조회
        selected_start["value"] = None
        selected_end["value"] = None

        search_type_value["value"] = "subs_id"
        search_type_text.value = search_type_labels["subs_id"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1

        refresh_picker_fields()
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨겨두고, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78)
    update_reset_button_visibility()

    pagination_state["keyword"] = ""
    pagination_state["current_page"] = 1
    reload_current_page()

    return ft.Column(
        expand=True,
        spacing=0,
        controls=[
            ft.Container(
                bgcolor=ft.Colors.WHITE,
                padding=ft.Padding.only(left=24, right=24, top=18, bottom=14),
                content=ft.Row(
                    wrap=True,
                    spacing=12,
                    run_spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        start_field_holder,
                        start_icon_holder,
                        ft.Text(
                            value="~",
                            size=18,
                            color="#374151",
                            weight=ft.FontWeight.W_600,
                        ),
                        end_field_holder,
                        end_icon_holder,
                        search_type,
                        search_field,
                        action_button("조회", on_click=on_search_click),
                        reset_button_holder,
                        action_button("인쇄"),
                        action_button("다운로드", width=92),
                    ],
                ),
            ),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.WHITE,
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