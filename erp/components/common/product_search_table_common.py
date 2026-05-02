import flet as ft

from components.common.erp_busy_cursor import busy_cursor_control, with_busy_cursor
import datetime

# 👊 수정: 같은 common 패키지 아래 modals 폴더를 상대경로로 import
# ⭐ 등록 버튼 클릭 시 띄울 모달 UI를 가져오는 import
from .modals.modal import build_modal


# =========================================================
# 👊 공통 이동: 상품 검색/테이블 화면에서 함께 쓰는 스타일
# =========================================================
# ⭐ 조회 바 / 입력창 / 테이블 전반에 쓰는 공통 색상값들
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
# 👊 공통 이동: 텍스트 공통 빌더
# =========================================================
# ⭐ 테이블/제목/안내문구에 공통으로 쓰는 Text 생성 함수
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
# 👊 공통 이동: 중량 표시 포맷터
# =========================================================
# ⭐ 숫자만 들어오면 kg를 자동으로 붙여서 테이블 표시용 문자열로 변환
# ⭐ 이미 kg / g 같은 단위가 붙어 있으면 그대로 유지
# ⭐ 상품 마스터 / 상품 상세 / 재고 상세 등에서 함께 쓰는 공통 함수
def format_weight_display(value):
    text = str(value or "").strip()
    if not text:
        return ""

    lowered = text.lower()

    # 🔥 이미 단위가 붙어 있으면 그대로 사용
    if lowered.endswith("kg") or lowered.endswith("g"):
        return text

    # 🔥 숫자만 들어온 경우 기본 단위 kg 자동 부착
    return f"{text}kg"


# =========================================================
# 👊 공통 이동: 날짜 표시 필드
# =========================================================
# ⭐ 시작일/종료일 날짜가 표시되는 박스 UI
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
# 👊 공통 이동: 달력 아이콘 버튼
# =========================================================
# ⭐ DatePicker를 열기 위한 달력 아이콘 박스
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
# 👊 공통 이동: 공통 버튼
# =========================================================
# ⭐ 조회 / 인쇄 / 다운로드 / 등록 버튼을 같은 스타일로 만들기 위한 함수
def action_button(text, on_click=None, width=78):
    # 🔥 상품 검색 공통 버튼에도 progress cursor 적용
    return busy_cursor_control(
        ft.Container(
            width=width,
            height=38,
            bgcolor=BUTTON_BG,
            border=ft.Border.all(1, BUTTON_BORDER),
            border_radius=6,
            alignment=ft.Alignment(0, 0),
            on_click=with_busy_cursor(on_click),
            content=ft.Text(
                value=text,
                size=13,
                color=BUTTON_TEXT,
                weight=ft.FontWeight.W_500,
            ),
        )
    )



# =========================================================
# 👊 공통 이동: 테이블 셀 공통 빌더
# =========================================================
# ⭐ 헤더 셀 / 데이터 셀을 공통 방식으로 만드는 함수
# ⭐ expand와 align_x로 컬럼 너비 비율과 정렬 방향을 제어함
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
# 👊 추가: 기본 row 변환기
# =========================================================
# ⭐ 모달에서 저장된 입력값(saved_data)을
# ⭐ 현재 테이블 한 줄(row) 형식으로 바꿔주는 기본 변환 함수
# ⭐ 상품 마스터 / 상품 상세 등에서 공통으로 사용할 수 있는 기본 구조
# ⭐ 중량 key는 spec_weight 하나로 통일해서 처리함
def default_register_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_code": saved_data.get("product_code", ""),
        "product_name": saved_data.get("product_name", ""),
        "product_type": saved_data.get("product_type", ""),
        "brand": saved_data.get("brand", ""),
        "manufacturer": saved_data.get("manufacturer", ""),
        "consumer_price": saved_data.get("consumer_price", ""),
        # ☑️ spec_weight로 통일
        # "spec_weight": format_weight_display(
        #     saved_data.get("spec_weight", "")
        # ),
        "barcode": saved_data.get("barcode", ""),
        "stock_unit": saved_data.get("stock_unit", ""),
        "sale_status": saved_data.get("sale_status", ""),
    }


# =========================================================
# 👊 공통 이동: 상품 목록형 검색 화면 전체 빌더
# =========================================================
# ⭐ 이 파일의 핵심 함수
# ⭐ 상품마스터정보관리 / 상품 상세 정보 관리 / 상품별 재고 상세처럼
# ⭐ "조회 바 + 테이블 + 등록 모달" 구조가 같은 화면을 공통으로 생성함
def build_product_search_table_page(
    *,
    page_title,
    page_bg,
    rows,
    search_type_labels=None,
    search_key_map=None,
    col_expand=None,
    register_button_text="등록",
    register_title=None,
    edit_title=None,
    register_fields=None,
    session_prefix=None,
    # =========================================================
    # 👊 추가: 모달 저장값을 테이블 row로 바꾸는 adapter
    # =========================================================
    # ⭐ 화면별로 저장 데이터 구조가 다를 수 있어서
    # ⭐ 외부에서 row 변환 함수를 따로 넘길 수 있게 한 부분
    register_row_adapter=None,
):
    # ⭐ 검색 조건 드롭다운 기본값 설정
    if search_type_labels is None:
        search_type_labels = {
            "product_name": "상품명",
            "product_code": "제품코드",
            "product_type": "상품종류",
            "brand": "브랜드",
            "manufacturer": "제조사",
            "sale_status": "판매 상태",
        }

    # ⭐ 드롭다운에서 선택한 검색 조건을
    # ⭐ 실제 row 딕셔너리 key와 매칭하는 기본 맵
    if search_key_map is None:
        search_key_map = {
            "product_name": "product_name",
            "product_code": "product_code",
            "product_type": "product_type",
            "brand": "brand",
            "manufacturer": "manufacturer",
            "sale_status": "sale_status",
        }

    # ⭐ 테이블 각 컬럼의 너비 비율(expand) 설정
    if col_expand is None:
        col_expand = {
            "no": 5,
            "product_code": 9,
            "product_name": 18,
            "product_type": 9,
            "brand": 9,
            "manufacturer": 13,
            "consumer_price": 11,
            "spec_weight": 9,
            "barcode": 13,
            "stock_unit": 7,
            "sale_status": 9,
        }

    # ⭐ row 변환 함수를 따로 안 넘기면 기본 변환기 사용
    if register_row_adapter is None:
        register_row_adapter = default_register_row_adapter

    # ⭐ 시작일 / 종료일 선택값을 저장하는 상태
    selected_start = {"value": None}
    selected_end = {"value": None}

    # ⭐ 현재 선택된 검색 조건 상태
    search_type_value = {"value": "product_name"}

    # ⭐ 날짜 필드와 달력 버튼은 내용이 바뀌므로 빈 holder를 먼저 만들어 둠
    start_field_holder = ft.Container()
    start_icon_holder = ft.Container(width=38, height=38)
    end_field_holder = ft.Container()
    end_icon_holder = ft.Container(width=38, height=38)

    # ⭐ 조회 결과 안내 문구
    result_text = ft.Text(
        value="아직 조회하지 않았습니다.",
        size=13,
        color=TEXT_SECONDARY,
    )

    # ⭐ 실제 테이블 row들이 들어갈 컨테이너
    table_rows_holder = ft.Column(spacing=0)

    # =========================================================
    # 👊 추가: 실제 등록 반영을 위해 rows를 내부 상태로 관리
    # =========================================================
    # ⭐ 처음 받은 rows를 그대로 쓰지 않고 내부 복사본(rows_state)을 만들어 관리
    # ⭐ 이유: 등록 모달에서 새 row를 append 해야 하기 때문
    rows_state = [dict(row) for row in rows]

    # ⭐ 모달이 열릴 때 뒤에 깔리는 반투명 배경
    dim_bg = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
    )

    # ⭐ 모달 본체가 올라올 레이어
    popup_layer = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

    # ⭐ 테이블 row 공통 간격/패딩값
    row_spacing = 10
    row_padding_x = 14
    row_padding_y = 14

    # ⭐ datetime 값을 화면 표시용 문자열(YYYY.MM.DD)로 바꾸는 함수
    def format_date_text(value):
        if not value:
            return ""
        return value.strftime("%Y.%m.%d")

    # ⭐ 시작일/종료일 필드 UI를 현재 상태값 기준으로 다시 그리는 함수
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

    # ⭐ 시작일 선택 시 실행
    # ⭐ 한국 시간 보정(+9시간)과 종료일 보정 로직 포함
    def on_start_date_change(e):
        if e.control.value:
            corrected_date = e.control.value + datetime.timedelta(hours=9)
            selected_start["value"] = corrected_date

            # ⭐ 시작일이 종료일보다 늦어지면 종료일도 같이 맞춰줌
            if selected_end["value"] and selected_end["value"] < selected_start["value"]:
                selected_end["value"] = selected_start["value"]

        refresh_picker_fields()
        e.page.update()

    # ⭐ 종료일 선택 시 실행
    # ⭐ 시작일보다 빠른 종료일 선택을 막고 자동 보정함
    def on_end_date_change(e):
        if e.control.value:
            corrected_date = e.control.value + datetime.timedelta(hours=9)

            if selected_start["value"] and corrected_date < selected_start["value"]:
                selected_end["value"] = selected_start["value"]
            else:
                selected_end["value"] = corrected_date

        refresh_picker_fields()
        e.page.update()

    # ⭐ 시작일 선택용 DatePicker
    start_date_picker = ft.DatePicker(
        first_date=datetime.datetime(2000, 1, 1),
        last_date=datetime.datetime(2035, 12, 31),
        on_change=on_start_date_change,
    )

    # ⭐ 종료일 선택용 DatePicker
    end_date_picker = ft.DatePicker(
        first_date=datetime.datetime(2000, 1, 1),
        last_date=datetime.datetime(2035, 12, 31),
        on_change=on_end_date_change,
    )

    # ⭐ 시작일 박스나 달력 버튼 클릭 시 DatePicker 열기
    def open_start_picker(e):
        page = e.page
        if start_date_picker not in page.overlay:
            page.overlay.append(start_date_picker)

        if selected_start["value"]:
            start_date_picker.value = selected_start["value"]

        start_date_picker.open = True
        page.update()

    # ⭐ 종료일 박스나 달력 버튼 클릭 시 DatePicker 열기
    # ⭐ 시작일이 선택되어 있으면 종료일의 최소 날짜도 시작일로 맞춤
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

    # ⭐ 현재 검색 조건 텍스트(예: 상품명, 제품코드)
    search_type_text = ft.Text(
        value=search_type_labels[search_type_value["value"]],
        size=13,
        color=FIELD_TEXT,
        weight=ft.FontWeight.W_500,
    )

    # ⭐ 드롭다운에서 검색 조건 선택 시 상태와 화면 텍스트 갱신
    def set_search_type(value: str):
        search_type_value["value"] = value
        search_type_text.value = search_type_labels[value]
        search_type_text.update()

    # ⭐ PopupMenu 안에 들어갈 검색 조건 메뉴 아이템 생성
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

    # ⭐ 검색 조건 드롭다운 전체 UI
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

    # ⭐ 검색어 입력창
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

    # ⭐ 테이블 헤더 한 줄 생성
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
                    build_table_cell("제품코드", col_expand["product_code"], -1, ft.FontWeight.W_700),
                    build_table_cell("상품명", col_expand["product_name"], -1, ft.FontWeight.W_700),
                    build_table_cell("상품종류", col_expand["product_type"], -1, ft.FontWeight.W_700),
                    build_table_cell("브랜드", col_expand["brand"], -1, ft.FontWeight.W_700),
                    build_table_cell("제조사", col_expand["manufacturer"], -1, ft.FontWeight.W_700),
                    build_table_cell("소비자판매가", col_expand["consumer_price"], 1, ft.FontWeight.W_700),
                    # build_table_cell("규격(중량)", col_expand["spec_weight"], 1, ft.FontWeight.W_700),
                    build_table_cell("바코드", col_expand["barcode"], -1, ft.FontWeight.W_700),
                    build_table_cell("재고단위", col_expand["stock_unit"], -1, ft.FontWeight.W_700),
                    build_table_cell("판매 상태", col_expand["sale_status"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    # ⭐ 테이블 데이터 한 줄(row) 생성
    # ⭐ 판매 상태에 따라 글자색도 다르게 처리
    def build_table_row(row):
        sale_status_color = {
            "판매중": "#16A34A",
            "판매중지": "#DC2626",
            "품절": "#D97706",
        }.get(row.get("sale_status", ""), TEXT_PRIMARY)

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
                    build_table_cell(row.get("product_code", ""), col_expand["product_code"], -1),
                    build_table_cell(row.get("product_name", ""), col_expand["product_name"], -1),
                    build_table_cell(row.get("product_type", ""), col_expand["product_type"], -1),
                    build_table_cell(row.get("brand", ""), col_expand["brand"], -1),
                    build_table_cell(row.get("manufacturer", ""), col_expand["manufacturer"], -1),
                    build_table_cell(row.get("consumer_price", ""), col_expand["consumer_price"], 1),
                    build_table_cell(row.get("spec_weight", ""), col_expand["spec_weight"], 1),
                    build_table_cell(row.get("barcode", ""), col_expand["barcode"], -1),
                    build_table_cell(row.get("stock_unit", ""), col_expand["stock_unit"], -1),
                    build_table_cell(
                        row.get("sale_status", ""),
                        col_expand["sale_status"],
                        0,
                        ft.FontWeight.W_700,
                        sale_status_color,
                    ),
                ],
            ),
        )

    # ⭐ 전달받은 row 목록으로 테이블 본문을 다시 그림
    def refresh_table(filtered_rows):
        table_rows_holder.controls.clear()
        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    # ⭐ 조회 버튼/엔터 입력 시 실행되는 핵심 검색 함수
    # ⭐ 선택한 검색 조건 + 검색어를 기준으로 rows_state를 필터링함
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

        actual_key = search_key_map.get(
            search_type_value["value"], "product_name"
        )

        filtered_rows = []

        for row in rows_state:
            is_match = True

            if keyword:
                target_value = str(row.get(actual_key, ""))
                if keyword.lower() not in target_value.lower():
                    is_match = False

            if is_match:
                filtered_rows.append(row)

        # ⭐ 현재 조회 조건/검색어/건수를 화면에 표시
        result_text.value = (
            f"기간: {start_text} ~ {end_text} / "
            f"검색어: {keyword if keyword else '없음'} / "
            f"조회 건수: {len(filtered_rows)}건"
        )

        refresh_table(filtered_rows)
        result_text.page.update()

    # ⭐ 검색창에서 엔터를 쳐도 조회되도록 연결
    search_field.on_submit = lambda e: run_search()

    # ⭐ 아직 미구현인 인쇄 기능용 안내 문구
    def on_print(e):
        result_text.value = "인쇄 기능은 아직 연결 전입니다."
        e.page.update()

    # ⭐ 아직 미구현인 다운로드 기능용 안내 문구
    def on_download(e):
        result_text.value = "다운로드 기능은 아직 연결 전입니다."
        e.page.update()

    # =========================================================
    # 👊 추가: 등록 모달 닫기
    # =========================================================
    # ⭐ dim 배경과 popup 레이어를 숨겨서 등록 모달을 닫는 함수
    def close_register_modal(e):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        e.page.update()

    # =========================================================
    # 👊 추가: 새 등록 전에 session 값 초기화
    # =========================================================
    # ⭐ 이전에 입력했던 값이 다음 등록 모달에 남지 않도록
    # ⭐ session_prefix 기준 필드값을 전부 초기화
    def clear_register_session(page: ft.Page):
        if not register_fields or not session_prefix:
            return

        for field in register_fields:
            page.session.store.set(f"{session_prefix}_{field['key']}", "")

    # =========================================================
    # 👊 추가: 저장 성공 시 실제 테이블에 신규 row 추가
    # =========================================================
    # ⭐ 모달 저장 성공 시 호출됨
    # ⭐ 저장값(saved_data)을 row 형태로 바꿔 rows_state에 추가하고
    # ⭐ 테이블을 즉시 다시 그림
    def handle_register_success(saved_data: dict):
        next_no = len(rows_state) + 1
        new_row = register_row_adapter(saved_data, next_no)
        rows_state.append(new_row)
        refresh_table(rows_state)

    # =========================================================
    # 👊 추가: 등록 모달 열기
    # =========================================================
    # ⭐ 등록 버튼 클릭 시 실행
    # ⭐ session 초기화 → build_modal()로 모달 생성 → 화면에 띄움
    def open_register_modal(e):
        if not register_fields or not session_prefix or not register_title or not edit_title:
            result_text.value = "등록 모달 설정이 아직 연결되지 않았습니다."
            e.page.update()
            return

        clear_register_session(e.page)

        popup_layer.content = build_modal(
            page=e.page,
            register_title=register_title,
            edit_title=edit_title,
            fields=register_fields,
            session_prefix=session_prefix,
            close_handler=close_register_modal,
            # 👊 추가: 저장 성공 시 테이블 반영
            # ⭐ 모달 저장 완료 후 바로 목록에 반영되도록 콜백 연결
            on_submit_success=handle_register_success,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        e.page.update()

    # ⭐ dim 배경 클릭 시 모달 닫힘
    dim_bg.on_click = close_register_modal

    # ⭐ 최초 렌더 시 날짜 UI와 기본 테이블 데이터 표시
    refresh_picker_fields()
    refresh_table(rows_state)

    # ⭐ 조회 바 오른쪽 버튼들 묶음
    action_controls = [
        action_button("조회", on_click=lambda e: run_search(), width=78),
        # 🔥 미구현 기능 버튼은 사용자 혼란 방지를 위해 숨김
    ]

    # ⭐ 등록 관련 설정값이 들어온 경우에만 등록 버튼 표시
    if register_fields and session_prefix and register_title and edit_title:
        action_controls.append(
            action_button(register_button_text, on_click=open_register_modal, width=78)
        )

    # ⭐ 상단 조회 필터 영역 전체
    # ⭐ 날짜 선택 / 검색 조건 / 검색어 / 액션 버튼을 한 줄로 배치
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

    # ⭐ 실제 상품 목록 테이블 영역
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

    # ⭐ 모달을 제외한 본 화면 본문
    # ⭐ 제목 + result_text + table_area로 구성됨
    main_content = ft.Container(
        expand=True,
        bgcolor=page_bg,
        padding=0,
        content=ft.Column(
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
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

    # ⭐ 최종 반환 화면
    # ⭐ Stack을 써서 본문(main_content) 위에 dim_bg와 popup_layer를 겹쳐 띄움
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