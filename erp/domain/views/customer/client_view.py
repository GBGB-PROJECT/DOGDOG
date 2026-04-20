import flet as ft
import datetime

from components import common as cm
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import CLIENT_FIELDS


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
        value=value,
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
# ☑️ 저장 데이터 -> 고객 테이블 row 변환
# =========================================================
def client_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "client_name": saved_data.get("client_name", ""),
        "client_id": saved_data.get("client_id", ""),
        "phone": saved_data.get("phone", ""),
        "zip_code": saved_data.get("zip_code", ""),
        "address": saved_data.get("address", ""),
        "address_detail": saved_data.get("address_detail", ""),
        "birth_date": saved_data.get("birth_date", ""),
        "gender": saved_data.get("gender", ""),
        "client_grade": saved_data.get("client_grade", ""),
        "is_subscribed": saved_data.get("is_subscribed", ""),
        "note": saved_data.get("note", ""),
    }


# =========================================================
# ☑️ 고객관리 화면
# =========================================================
def erp_client_view():
    page_title = "고객관리 > 고객정보관리"

    dummy_rows = [
        {
            "no": "1",
            "client_name": "김민수",
            "client_id": "CLIENT001",
            "phone": "010-1111-2222",
            "zip_code": "06236",
            "address": "서울특별시 강남구 테헤란로",
            "address_detail": "101동 1203호",
            "birth_date": "1994-05-14",
            "gender": "남",
            "client_grade": "VIP",
            "is_subscribed": "Y",
            "note": "정기구매 고객",
        },
        {
            "no": "2",
            "client_name": "이서연",
            "client_id": "CLIENT002",
            "phone": "010-3333-4444",
            "zip_code": "13529",
            "address": "경기도 성남시 분당구",
            "address_detail": "202호",
            "birth_date": "1998-11-02",
            "gender": "여",
            "client_grade": "일반",
            "is_subscribed": "N",
            "note": "",
        },
    ]

    rows_state = [dict(row) for row in dummy_rows]

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "client_name"}

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    result_text = ft.Text(
        value="아직 조회하지 않았습니다.",
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

    col_expand = {
        "no": 4,
        "client_name": 8,
        "client_id": 9,
        "phone": 10,
        "zip_code": 7,
        "address": 13,
        "address_detail": 10,
        "birth_date": 8,
        "gender": 5,
        "client_grade": 7,
        "is_subscribed": 6,
        "note": 9,
    }

    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    search_type_labels = {
        "client_name": "고객명",
        "client_id": "고객 ID",
        "phone": "전화번호",
        "client_grade": "고객등급",
        "is_subscribed": "구독여부",
    }

    search_key_map = {
        "client_name": "client_name",
        "client_id": "client_id",
        "phone": "phone",
        "client_grade": "client_grade",
        "is_subscribed": "is_subscribed",
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
                    build_table_cell("no", col_expand["no"], 0, ft.FontWeight.W_700),
                    build_table_cell("고객명", col_expand["client_name"], -1, ft.FontWeight.W_700),
                    build_table_cell("고객 ID", col_expand["client_id"], -1, ft.FontWeight.W_700),
                    build_table_cell("전화번호", col_expand["phone"], -1, ft.FontWeight.W_700),
                    build_table_cell("우편번호", col_expand["zip_code"], 0, ft.FontWeight.W_700),
                    build_table_cell("주소", col_expand["address"], -1, ft.FontWeight.W_700),
                    build_table_cell("상세주소", col_expand["address_detail"], -1, ft.FontWeight.W_700),
                    build_table_cell("생년월일", col_expand["birth_date"], 0, ft.FontWeight.W_700),
                    build_table_cell("성별", col_expand["gender"], 0, ft.FontWeight.W_700),
                    build_table_cell("고객등급", col_expand["client_grade"], 0, ft.FontWeight.W_700),
                    build_table_cell("구독여부", col_expand["is_subscribed"], 0, ft.FontWeight.W_700),
                    build_table_cell("비고", col_expand["note"], -1, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_table_row(row):
        subscribe_color = {
            "Y": "#16A34A",
            "N": "#DC2626",
        }.get(row.get("is_subscribed", ""), TEXT_PRIMARY)

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
                    build_table_cell(row.get("client_name", ""), col_expand["client_name"], -1),
                    build_table_cell(row.get("client_id", ""), col_expand["client_id"], -1),
                    build_table_cell(row.get("phone", ""), col_expand["phone"], -1),
                    build_table_cell(row.get("zip_code", ""), col_expand["zip_code"], 0),
                    build_table_cell(row.get("address", ""), col_expand["address"], -1),
                    build_table_cell(row.get("address_detail", ""), col_expand["address_detail"], -1),
                    build_table_cell(row.get("birth_date", ""), col_expand["birth_date"], 0),
                    build_table_cell(row.get("gender", ""), col_expand["gender"], 0),
                    build_table_cell(row.get("client_grade", ""), col_expand["client_grade"], 0),
                    build_table_cell(
                        row.get("is_subscribed", ""),
                        col_expand["is_subscribed"],
                        0,
                        ft.FontWeight.W_700,
                        subscribe_color,
                    ),
                    build_table_cell(row.get("note", ""), col_expand["note"], -1),
                ],
            ),
        )

    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()
        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def run_search():
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

        keyword = (search_field.value or "").strip()
        actual_key = search_key_map.get(search_type_value["value"], "client_name")

        filtered_rows = []

        for row in rows_state:
            is_match = True

            if keyword:
                target_value = str(row.get(actual_key, ""))
                if keyword.lower() not in target_value.lower():
                    is_match = False

            if is_match:
                filtered_rows.append(row)

        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"조회 건수: {len(filtered_rows)}건"
        )

        refresh_table(filtered_rows)
        result_text.page.update()

    search_field.on_submit = lambda e: run_search()

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
        for field in CLIENT_FIELDS:
            page.session.store.set(f"client_{field['key']}", "")

    def handle_register_success(saved_data: dict):
        next_no = len(rows_state) + 1
        new_row = client_row_adapter(saved_data, next_no)
        rows_state.append(new_row)
        refresh_table(rows_state)

    def open_register_modal(e):
        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title="고객 등록",
            edit_title="고객 정보 수정",
            fields=CLIENT_FIELDS,
            session_prefix="client",
            close_handler=close_register_modal,
            on_submit_success=handle_register_success,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        e.page.update()

    dim_bg.on_click = close_register_modal

    refresh_picker_fields()
    refresh_table(rows_state)

    action_controls = [
        action_button("조회", on_click=lambda e: run_search(), width=78),
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