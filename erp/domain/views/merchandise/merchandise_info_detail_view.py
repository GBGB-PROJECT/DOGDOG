import flet as ft
import datetime

from components import common as cm
from components.common.modals.modal import build_modal
from components.common.modals.field_defs import PRODUCT_DETAIL_FIELDS
from components.common.product_search_table_common import format_weight_display

# =========================================================
# ☑️ 추가: session prefix 상수화
# =========================================================
SESSION_PREFIX = "merchandise_product_detail"

# =========================================================
# ☑️ 공통 텍스트
# =========================================================
def build_text(
    value,
    size=12,
    color=cm.TEXT_PRIMARY,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.LEFT,
    max_lines=1,
):
    return ft.Text(
        value=value,
        size=size,
        color=color,
        weight=weight,
        text_align=text_align,
        max_lines=max_lines,
        overflow=ft.TextOverflow.ELLIPSIS,
    )


# =========================================================
# ☑️ 숫자/중량 표시 포맷
# =========================================================
# ☑️ 공통화: 중량 표시 포맷은 product_search_table_common.py의
# ☑️ format_weight_display()를 import 해서 함께 사용


# =========================================================
# ☑️ 날짜 표시 필드
# =========================================================
def date_value_box(text, on_click=None):
    return ft.Container(
        width=138,
        height=38,
        bgcolor=cm.PAGE_BG,
        border=ft.Border.all(1, cm.FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=14, right=14),
        alignment=ft.Alignment(-1, 0),
        on_click=on_click,
        content=ft.Text(
            value=text,
            size=13,
            color=cm.FIELD_TEXT,
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
        bgcolor=cm.PAGE_BG,
        border=ft.Border.all(1, cm.FIELD_BORDER),
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
        bgcolor=cm.BUTTON_BG,
        border=ft.Border.all(1, cm.FIELD_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        on_click=on_click,
        content=ft.Text(
            value=text,
            size=13,
            color=cm.BUTTON_TEXT,
            weight=ft.FontWeight.W_500,
        ),
    )


# =========================================================
# ☑️ 상세정보 저장 데이터 -> 테이블 row 변환
# =========================================================
def product_detail_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_code": saved_data.get("product_code", ""),
        "product_name": saved_data.get("product_name", ""),
        "product_image": saved_data.get("product_image", ""),
        "product_detail_page": saved_data.get("product_detail_page", ""),
        "product_type": saved_data.get("product_type", ""),
        "brand": saved_data.get("brand", ""),
        "manufacturer": saved_data.get("manufacturer", ""),
        "consumer_price": saved_data.get("consumer_price", ""),
        "cost": saved_data.get("cost", ""),
        "spec_weight": format_weight_display(saved_data.get("spec_weight", "")),
        "function": saved_data.get("function", ""),
        "description": saved_data.get("description", ""),
        "crude_protein": saved_data.get("crude_protein", ""),
        "crude_fat": saved_data.get("crude_fat", ""),
        "crude_ash": saved_data.get("crude_ash", ""),
        "crude_fiber": saved_data.get("crude_fiber", ""),
        "moisture": saved_data.get("moisture", ""),
        "calcium": saved_data.get("calcium", ""),
        "phosphorus": saved_data.get("phosphorus", ""),
        "calorie": saved_data.get("calorie", ""),
    }


# =========================================================
# ☑️ 가로 스크롤형 테이블 셀
# =========================================================
def build_table_cell(
    text,
    width,
    align_x=-1,
    weight=ft.FontWeight.W_400,
    color=cm.TEXT_ROW,
    size=12,
):
    return ft.Container(
        width=width,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=str(text or ""),
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT,
        ),
    )


# =========================================================
# ☑️ 상품 상세 정보 관리 화면
# =========================================================
def erp_merchandise_info_detail_view():
    page_title = "상품관리 > 상품 상세 정보 관리"

    dummy_rows = [
        {
            "no": "1",
            "product_code": "P-1001",
            "product_name": "하림 가장 맛있는 시간",
            "product_image": "https://example.com/image1.jpg",
            "product_detail_page": "https://example.com/detail1",
            "product_type": "사료",
            "brand": "하림",
            "manufacturer": "하림펫푸드",
            "consumer_price": "32000",
            "cost": "21000",
            "spec_weight": "1.2kg",
            "function": "장건강",
            "description": "반려견용 프리미엄 사료",
            "crude_protein": "24.0",
            "crude_fat": "14.0",
            "crude_ash": "8.0",
            "crude_fiber": "3.5",
            "moisture": "10.0",
            "calcium": "1.2",
            "phosphorus": "1.0",
            "calorie": "360.0",
        },
    ]

    rows_state = [dict(row) for row in dummy_rows]

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "product_name"}

    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    result_text = ft.Text(
        value="아직 조회하지 않았습니다.",
        size=13,
        color=cm.TEXT_SECONDARY,
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

    search_type_labels = {
        "product_name": "상품명",
        "product_code": "제품코드",
        "product_type": "상품종류",
        "brand": "브랜드",
        "manufacturer": "제조사",
        "function": "기능",
    }

    search_key_map = {
        "product_name": "product_name",
        "product_code": "product_code",
        "product_type": "product_type",
        "brand": "brand",
        "manufacturer": "manufacturer",
        "function": "function",
    }

    columns = [
        {"key": "no", "label": "no", "width": 60, "align_x": 0},
        {"key": "product_code", "label": "제품코드", "width": 110, "align_x": -1},
        {"key": "product_name", "label": "상품명", "width": 150, "align_x": -1},
        {"key": "product_image", "label": "상품 이미지", "width": 180, "align_x": -1},
        {"key": "product_detail_page", "label": "상품 상세페이지", "width": 190, "align_x": -1},
        {"key": "product_type", "label": "상품종류", "width": 100, "align_x": -1},
        {"key": "brand", "label": "브랜드", "width": 100, "align_x": -1},
        {"key": "manufacturer", "label": "제조사", "width": 120, "align_x": -1},
        {"key": "consumer_price", "label": "소비자판매가", "width": 110, "align_x": 1},
        {"key": "cost", "label": "원가", "width": 100, "align_x": 1},
        {"key": "spec_weight", "label": "중량", "width": 90, "align_x": 1},
        {"key": "function", "label": "기능", "width": 120, "align_x": -1},
        {"key": "description", "label": "설명", "width": 220, "align_x": -1},
        {"key": "crude_protein", "label": "조단백", "width": 80, "align_x": 1},
        {"key": "crude_fat", "label": "조지방", "width": 80, "align_x": 1},
        {"key": "crude_ash", "label": "조회분", "width": 80, "align_x": 1},
        {"key": "crude_fiber", "label": "조섬유", "width": 80, "align_x": 1},
        {"key": "moisture", "label": "수분", "width": 80, "align_x": 1},
        {"key": "calcium", "label": "칼슘", "width": 80, "align_x": 1},
        {"key": "phosphorus", "label": "인", "width": 80, "align_x": 1},
        {"key": "calorie", "label": "열량", "width": 80, "align_x": 1},
    ]

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
        color=cm.FIELD_TEXT,
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
                    color=cm.FIELD_TEXT,
                    weight=ft.FontWeight.W_500,
                ),
            ),
            on_click=lambda e: set_search_type(value),
        )

    search_type = ft.Container(
        width=140,
        height=38,
        bgcolor=cm.PAGE_BG,
        border=ft.Border.all(1, cm.FIELD_BORDER),
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
            color=cm.TEXT_MUTED,
        ),
        text_size=13,
        border_color=cm.FIELD_BORDER,
        border_radius=6,
        bgcolor=cm.PAGE_BG,
        content_padding=ft.Padding.only(left=12, right=12, top=0, bottom=0),
    )

    def build_table_header():
        return ft.Container(
            bgcolor=cm.TABLE_HEADER_BG,
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
                        cm.TEXT_PRIMARY,
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
            border=ft.border.only(bottom=ft.BorderSide(1, cm.TABLE_BORDER)),
            bgcolor=cm.CARD_BG,
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
        actual_key = search_key_map.get(search_type_value["value"], "product_name")

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

    table_content = ft.Column(
        spacing=0,
        controls=[
            build_table_header(),
            table_rows_holder,
        ],
    )

    table_area = ft.Container(
        expand=True,
        border=ft.border.all(1, cm.FIELD_BORDER),
        border_radius=10,
        bgcolor=cm.CARD_BG,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Row(
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    content=table_content,
                )
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
                                color=cm.TEXT_PRIMARY,
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