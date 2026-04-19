import flet as ft


# =========================================================
# ☑️ 공통 스타일
# =========================================================
BORDER_COLOR = "#5A5A5A"
HEADER_BG = "#F5F5F5"
WHITE = "#FFFFFF"
TEXT_COLOR = "#111111"
PAGE_BG = "#EDEDED"

DIALOG_WIDTH = 1500
DIALOG_HEIGHT = 920

FIELD_HEIGHT = 42
ROW_HEIGHT = 42
TITLE_HEIGHT = 150

# =========================================================
# ☑️ 문서 전체 공통 폭
# =========================================================
DOC_WIDTH = 1424

# 상단 제목 / 결재 영역
TITLE_LEFT_WIDTH = 1114
TITLE_RIGHT_WIDTH = 310
APPROVAL_COL_WIDTH = 103

# =========================================================
# ☑️ 수신처 블록 폭
# =========================================================
RECEIVER_LABEL_W = 120
RECEIVER_NAME_W = 460

RECEIVER_MID_LABEL_W = 120
RECEIVER_MID_VALUE_W = 240

RECEIVER_RIGHT_LABEL_W = 120
RECEIVER_RIGHT_VALUE_W = DOC_WIDTH - (
    RECEIVER_LABEL_W
    + RECEIVER_NAME_W
    + RECEIVER_MID_LABEL_W
    + RECEIVER_MID_VALUE_W
    + RECEIVER_RIGHT_LABEL_W
)
RECEIVER_BLOCK_HEIGHT = 84

# =========================================================
# ☑️ 발신처 블록 폭
# =========================================================
SENDER_LEFT_LABEL_W = 120
SENDER_INNER_LABEL_W = 115

# 사업자등록번호 / 상호 / 대표자 / 주소 / TEL / FAX
SENDER_BIZ_NO_VALUE_W = DOC_WIDTH - SENDER_LEFT_LABEL_W - SENDER_INNER_LABEL_W
SENDER_COMPANY_LEFT_VALUE_W = 480
SENDER_CEO_LABEL_W = 115
SENDER_CEO_VALUE_W = DOC_WIDTH - (
    SENDER_LEFT_LABEL_W
    + SENDER_INNER_LABEL_W
    + SENDER_COMPANY_LEFT_VALUE_W
    + SENDER_CEO_LABEL_W
)
SENDER_ADDR_VALUE_W = DOC_WIDTH - SENDER_LEFT_LABEL_W - SENDER_INNER_LABEL_W
SENDER_TEL_VALUE_W = 480
SENDER_FAX_LABEL_W = 115
SENDER_FAX_VALUE_W = DOC_WIDTH - (
    SENDER_LEFT_LABEL_W
    + SENDER_INNER_LABEL_W
    + SENDER_TEL_VALUE_W
    + SENDER_FAX_LABEL_W
)

SENDER_BLOCK_HEIGHT = FIELD_HEIGHT * 4  # 168

# =========================================================
# ☑️ 발주 정보 영역 폭
# =========================================================
INFO_LEFT_LABEL_W = 120
INFO_LEFT_VALUE_W = 490
INFO_RIGHT_LABEL_W = 120
INFO_RIGHT_VALUE_W = DOC_WIDTH - (
    INFO_LEFT_LABEL_W + INFO_LEFT_VALUE_W + INFO_RIGHT_LABEL_W
)

# =========================================================
# ☑️ 품목 테이블 폭
#     마지막 납품기한 폭은 DOC_WIDTH에 맞게 자동 보정
# =========================================================
COL_NO = 50
COL_LOT = 110
COL_NAME = 150
COL_SPEC = 140
COL_UNIT = 70
COL_QTY = 110
COL_PRICE = 120
COL_SUPPLY = 130
COL_TAX = 120
COL_DEADLINE = 110

ITEM_TOTAL_WIDTH = (
    COL_NO
    + COL_LOT
    + COL_NAME
    + COL_SPEC
    + COL_UNIT
    + COL_QTY
    + COL_PRICE
    + COL_SUPPLY
    + COL_TAX
    + COL_DEADLINE
)

COL_DEADLINE = COL_DEADLINE + (DOC_WIDTH - ITEM_TOTAL_WIDTH)

# =========================================================
# ☑️ 하단 합계 / 참고사항 폭
# =========================================================
SUMMARY_LABEL_W = 120
SUMMARY_VALUE_W = 650
SUMMARY_RIGHT_VALUE_W = DOC_WIDTH - SUMMARY_LABEL_W - SUMMARY_VALUE_W

NOTE_LABEL_W = 120
NOTE_VALUE_W = DOC_WIDTH - NOTE_LABEL_W

CONDITION_LABEL_W = 120
CONDITION_VALUE_W = DOC_WIDTH - CONDITION_LABEL_W

# =========================================================
# ☑️ 숫자 유틸
# =========================================================
def to_int(value):
    # ⭐ 수량/단가/합계 계산 전에 문자열 숫자를 정수로 바꾸는 공통 유틸
    try:
        value = str(value).replace(",", "").strip()
        if value == "":
            return 0
        return int(value)
    except Exception:
        return 0


def format_number(value):
    # ⭐ 계산된 금액(공급가, 세액, 총합계)을 30,000 같은 형식으로 표시
    if value in ("", None):
        return ""
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


# =========================================================
# ☑️ 공통 셀
# =========================================================
def box_label(text, width=None, height=FIELD_HEIGHT, bold=False):
    return ft.Container(
        width=width,
        height=height,
        bgcolor=HEADER_BG,
        alignment=ft.Alignment(0, 0),
        border=ft.border.all(1, BORDER_COLOR),
        content=ft.Text(
            text,
            size=13,
            color=TEXT_COLOR,
            weight=ft.FontWeight.W_700 if bold else ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
        ),
    )


def box_input(control, width=None, height=FIELD_HEIGHT, bgcolor=WHITE):
    return ft.Container(
        width=width,
        height=height,
        border=ft.border.all(1, BORDER_COLOR),
        bgcolor=bgcolor,
        alignment=ft.Alignment(0, 0),
        content=control,
    )


def build_textfield(
    value="",
    text_align=ft.TextAlign.LEFT,
    read_only=False,
    on_change=None,
    dense=True,
):
    return ft.TextField(
        value=value,
        border=ft.InputBorder.NONE,
        filled=False,
        text_size=13,
        cursor_height=18,
        content_padding=ft.Padding(left=8, right=8, top=10, bottom=10),
        text_align=text_align,
        read_only=read_only,
        on_change=on_change,
        dense=dense,
    )


# =========================================================
# ☑️ 발주서 모달 클래스
#     🔥 class명 발주서에 맞게 수정
# =========================================================
class PurchaseOrderDialog:
    def __init__(self, page: ft.Page):
        self.page = page

        # -------------------------------------------------
        # ☑️ 상단 결재란
        # -------------------------------------------------
        self.approval_1 = build_textfield(text_align=ft.TextAlign.CENTER)
        self.approval_2 = build_textfield(text_align=ft.TextAlign.CENTER)
        self.approval_3 = build_textfield(text_align=ft.TextAlign.CENTER)

        # -------------------------------------------------
        # ☑️ 수신처
        # -------------------------------------------------
        self.receiver_name = build_textfield()
        self.receiver_tel = build_textfield()
        self.receiver_fax = build_textfield()
        self.receiver_person = build_textfield()

        # -------------------------------------------------
        # ☑️ 발신처
        # -------------------------------------------------
        self.sender_business_no = build_textfield()
        self.sender_company_name = build_textfield()
        self.sender_ceo = build_textfield()
        self.sender_address = build_textfield()
        self.sender_tel = build_textfield()
        self.sender_fax = build_textfield()

        # -------------------------------------------------
        # ☑️ 발주 정보
        # -------------------------------------------------
        self.order_date = build_textfield()
        self.order_no = build_textfield()
        self.contract_no = build_textfield()

        self.delivery_place = build_textfield()
        self.request_dept = build_textfield()
        self.order_manager = build_textfield()

        # -------------------------------------------------
        # ☑️ 하단 참고사항 / 발주조건 / 합계
        # -------------------------------------------------
        # ⭐ 품목별 계산 결과를 바탕으로 총합계를 숫자 형태로 보여주는 필드
        self.total_amount_text = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
        )

        # ⭐ 총합계를 한글 금액으로 변환해서 보여주는 필드
        self.total_amount_krw = build_textfield(read_only=True)

        self.note_text = build_textfield()
        self.payment_condition = build_textfield()

        # -------------------------------------------------
        # ☑️ 품목 행
        # -------------------------------------------------
        # ⭐ 발주 품목 입력 행 20개를 생성해서 문서형 입력 UI 구성
        self.item_rows = []
        for i in range(20):
            self.item_rows.append(self.build_item_row(i + 1))

        # -------------------------------------------------
        # ☑️ 다이얼로그
        # -------------------------------------------------
        # ⭐ ERP 프론트 발주서 입력 모달 UI 구현
        self.dialog = ft.AlertDialog(
            modal=True,
            inset_padding=10,
            bgcolor=ft.Colors.TRANSPARENT,
            content_padding=0,
            shape=ft.RoundedRectangleBorder(radius=12),
            content=self.build_dialog_content(),
        )

    # =====================================================
    # ☑️ 숫자를 한글 금액으로 대충 변환하는 간단 유틸
    #     🔥 완벽한 회계식 표기보다 UI 확인용
    # =====================================================
    def number_to_korean(self, value: int) -> str:
        # ⭐ 총합계를 '삼만삼천원' 같은 한글 금액으로 바꾸는 변환 함수
        if value == 0:
            return "영원"

        units = ["", "만", "억", "조"]
        small_units = ["", "십", "백", "천"]
        nums = ["", "일", "이", "삼", "사", "오", "육", "칠", "팔", "구"]

        result_parts = []
        unit_index = 0

        while value > 0:
            part = value % 10000
            value //= 10000

            if part > 0:
                part_str = ""
                digits = list(map(int, str(part)))
                length = len(digits)

                for i, n in enumerate(digits):
                    if n == 0:
                        continue
                    small_unit = small_units[length - i - 1]

                    if n == 1 and small_unit != "":
                        part_str += small_unit
                    else:
                        part_str += nums[n] + small_unit

                part_str += units[unit_index]
                result_parts.insert(0, part_str)

            unit_index += 1

        return "".join(result_parts) + "원"

    # =====================================================
    # ☑️ 품목 한 줄 생성
    #     🔥 발주서 컬럼 기준으로 재구성
    # =====================================================
    def build_item_row(self, no: int):
        row_data = {}

        def on_amount_change(e=None):
            # ⭐ 수량·단가 입력 시 공급가 및 세액 자동 계산 기능 구현
            qty = to_int(row_data["qty"].value)
            price = to_int(row_data["unit_price"].value)

            supply = qty * price
            tax = int(supply * 0.1)

            # ⭐ 계산 결과를 읽기 전용 필드에 즉시 반영 처리
            row_data["supply_amount"].value = format_number(supply) if supply else ""
            row_data["tax_amount"].value = format_number(tax) if tax else ""

            # ⭐ 품목별 금액 계산 후 총합계도 같이 다시 계산
            self.update_summary()
            self.page.update()

        row_data["no"] = no
        row_data["lot_no"] = build_textfield(text_align=ft.TextAlign.CENTER)
        row_data["product_name"] = build_textfield()
        row_data["spec"] = build_textfield()
        row_data["unit"] = build_textfield(text_align=ft.TextAlign.CENTER)

        row_data["qty"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            on_change=on_amount_change,
        )
        row_data["unit_price"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            on_change=on_amount_change,
        )
        row_data["supply_amount"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
        )
        row_data["tax_amount"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
        )
        row_data["delivery_deadline"] = build_textfield(text_align=ft.TextAlign.CENTER)

        return row_data

    # =====================================================
    # ☑️ 합계 업데이트
    # =====================================================
    def update_summary(self):
        # ⭐ 품목별 금액 합산을 통한 총합계 자동 반영 처리
        total_supply = 0
        total_tax = 0

        for row in self.item_rows:
            total_supply += to_int(row["supply_amount"].value)
            total_tax += to_int(row["tax_amount"].value)

        grand_total = total_supply + total_tax

        # ⭐ 총합계를 숫자 형식으로 표시
        self.total_amount_text.value = format_number(grand_total) if grand_total else ""

        # ⭐ 총합계를 한글 금액으로 변환하여 표시하는 기능
        self.total_amount_krw.value = (
            self.number_to_korean(grand_total) if grand_total else ""
        )

    # =====================================================
    # ☑️ 제목 + 결재란
    # =====================================================
    def build_title_area(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=TITLE_LEFT_WIDTH,
                        height=TITLE_HEIGHT,
                        border=ft.border.all(1, BORDER_COLOR),
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "발 주 서",
                            size=28,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_COLOR,
                        ),
                    ),
                    ft.Container(
                        width=TITLE_RIGHT_WIDTH,
                        height=TITLE_HEIGHT,
                        content=ft.Column(
                            spacing=0,
                            controls=[
                                ft.Row(
                                    spacing=0,
                                    controls=[
                                        box_label("담당", width=APPROVAL_COL_WIDTH),
                                        box_input(self.approval_1, width=APPROVAL_COL_WIDTH),
                                        box_input(self.approval_2, width=APPROVAL_COL_WIDTH),
                                    ],
                                ),
                                ft.Row(
                                    spacing=0,
                                    controls=[
                                        box_input(
                                            build_textfield(),
                                            width=APPROVAL_COL_WIDTH,
                                            height=108,
                                        ),
                                        box_input(
                                            build_textfield(),
                                            width=APPROVAL_COL_WIDTH,
                                            height=108,
                                        ),
                                        box_input(
                                            build_textfield(),
                                            width=APPROVAL_COL_WIDTH,
                                            height=108,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 수신처 블록
    #     구조:
    #     [수신처][입력칸][TEL][입력칸][담당자][입력칸]
    #                     [FAX][입력칸]
    # =====================================================
    def build_receiver_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("수신처", width=RECEIVER_LABEL_W, height=RECEIVER_BLOCK_HEIGHT),
                    box_input(self.receiver_name, width=RECEIVER_NAME_W, height=RECEIVER_BLOCK_HEIGHT),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("TEL", width=RECEIVER_MID_LABEL_W, bold=True),
                                    box_input(self.receiver_tel, width=RECEIVER_MID_VALUE_W),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("FAX", width=RECEIVER_MID_LABEL_W, bold=True),
                                    box_input(self.receiver_fax, width=RECEIVER_MID_VALUE_W),
                                ],
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("담당자", width=RECEIVER_RIGHT_LABEL_W, height=RECEIVER_BLOCK_HEIGHT),
                                    box_input(
                                        self.receiver_person,
                                        width=RECEIVER_RIGHT_VALUE_W,
                                        height=RECEIVER_BLOCK_HEIGHT,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 발신처 블록
    #     이미지 기준으로 4줄 구성
    # =====================================================
    def build_sender_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("발신처", width=SENDER_LEFT_LABEL_W, height=SENDER_BLOCK_HEIGHT),
                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("사업자 등록번호", width=SENDER_INNER_LABEL_W),
                                    box_input(self.sender_business_no, width=SENDER_BIZ_NO_VALUE_W),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("상호", width=SENDER_INNER_LABEL_W),
                                    box_input(self.sender_company_name, width=SENDER_COMPANY_LEFT_VALUE_W),
                                    box_label("대표자", width=SENDER_CEO_LABEL_W),
                                    box_input(self.sender_ceo, width=SENDER_CEO_VALUE_W),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("주소", width=SENDER_INNER_LABEL_W),
                                    box_input(self.sender_address, width=SENDER_ADDR_VALUE_W),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("TEL", width=SENDER_INNER_LABEL_W, bold=True),
                                    box_input(self.sender_tel, width=SENDER_TEL_VALUE_W),
                                    box_label("FAX", width=SENDER_FAX_LABEL_W, bold=True),
                                    box_input(self.sender_fax, width=SENDER_FAX_VALUE_W),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 발주 정보 2열 공통 행
    # =====================================================
    def build_info_row(self, left_title, left_control, right_title, right_control):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label(left_title, width=INFO_LEFT_LABEL_W),
                    box_input(left_control, width=INFO_LEFT_VALUE_W),
                    box_label(right_title, width=INFO_RIGHT_LABEL_W),
                    box_input(right_control, width=INFO_RIGHT_VALUE_W),
                ],
            ),
        )

    # =====================================================
    # ☑️ 품목 헤더
    # =====================================================
    def build_item_header(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("no", width=COL_NO, height=44, bold=True),
                    box_label("LOT NO", width=COL_LOT, height=44, bold=True),
                    box_label("품명", width=COL_NAME, height=44, bold=True),
                    box_label("규격/사양", width=COL_SPEC, height=44, bold=True),
                    box_label("단위", width=COL_UNIT, height=44, bold=True),
                    box_label("수량", width=COL_QTY, height=44, bold=True),
                    box_label("단가", width=COL_PRICE, height=44, bold=True),
                    box_label("공급가계", width=COL_SUPPLY, height=44, bold=True),
                    box_label("세액", width=COL_TAX, height=44, bold=True),
                    box_label("납품기한", width=COL_DEADLINE, height=44, bold=True),
                ],
            ),
        )

    # =====================================================
    # ☑️ 품목 한 줄 UI
    # =====================================================
    def build_item_line(self, row_data):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_input(
                        build_textfield(
                            value=str(row_data["no"]),
                            text_align=ft.TextAlign.CENTER,
                            read_only=True,
                        ),
                        width=COL_NO,
                        height=ROW_HEIGHT,
                    ),
                    box_input(row_data["lot_no"], width=COL_LOT, height=ROW_HEIGHT),
                    box_input(row_data["product_name"], width=COL_NAME, height=ROW_HEIGHT),
                    box_input(row_data["spec"], width=COL_SPEC, height=ROW_HEIGHT),
                    box_input(row_data["unit"], width=COL_UNIT, height=ROW_HEIGHT),
                    box_input(row_data["qty"], width=COL_QTY, height=ROW_HEIGHT),
                    box_input(row_data["unit_price"], width=COL_PRICE, height=ROW_HEIGHT),
                    box_input(row_data["supply_amount"], width=COL_SUPPLY, height=ROW_HEIGHT),
                    box_input(row_data["tax_amount"], width=COL_TAX, height=ROW_HEIGHT),
                    box_input(row_data["delivery_deadline"], width=COL_DEADLINE, height=ROW_HEIGHT),
                ],
            ),
        )

    # =====================================================
    # ☑️ 품목 입력 영역
    # =====================================================
    def build_items_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Column(
                spacing=0,
                controls=[self.build_item_header()]
                + [self.build_item_line(row_data) for row_data in self.item_rows],
            ),
        )

    # =====================================================
    # ☑️ 하단 합계 영역
    # =====================================================
    def build_summary_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("총합계", width=SUMMARY_LABEL_W, height=44, bold=True),
                    box_input(self.total_amount_krw, width=SUMMARY_VALUE_W, height=44),
                    box_input(
                        self.total_amount_text,
                        width=SUMMARY_RIGHT_VALUE_W,
                        height=44,
                        bgcolor=WHITE,
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 참고사항
    # =====================================================
    def build_note_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("참고사항", width=NOTE_LABEL_W, height=56),
                    box_input(self.note_text, width=NOTE_VALUE_W, height=56),
                ],
            ),
        )

    # =====================================================
    # ☑️ 발주조건
    # =====================================================
    def build_condition_section(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("발주조건", width=CONDITION_LABEL_W, height=56),
                    box_input(self.payment_condition, width=CONDITION_VALUE_W, height=56),
                ],
            ),
        )

    # =====================================================
    # ☑️ 저장 데이터 수집
    # =====================================================
    def collect_data(self):
        # ⭐ 입력된 품목 행만 선별하여 데이터 구조화 및 저장 처리
        items = []

        for row in self.item_rows:
            item = {
                "no": row["no"],
                "lot_no": row["lot_no"].value,
                "product_name": row["product_name"].value,
                "spec": row["spec"].value,
                "unit": row["unit"].value,
                "qty": row["qty"].value,
                "unit_price": row["unit_price"].value,
                "supply_amount": row["supply_amount"].value,
                "tax_amount": row["tax_amount"].value,
                "delivery_deadline": row["delivery_deadline"].value,
            }

            # ⭐ 값이 들어간 품목 행만 저장 대상에 포함
            has_value = any(str(v).strip() != "" for k, v in item.items() if k != "no")
            if has_value:
                items.append(item)

        return {
            "receiver_name": self.receiver_name.value,
            "receiver_tel": self.receiver_tel.value,
            "receiver_fax": self.receiver_fax.value,
            "receiver_person": self.receiver_person.value,
            "sender_business_no": self.sender_business_no.value,
            "sender_company_name": self.sender_company_name.value,
            "sender_ceo": self.sender_ceo.value,
            "sender_address": self.sender_address.value,
            "sender_tel": self.sender_tel.value,
            "sender_fax": self.sender_fax.value,
            "order_date": self.order_date.value,
            "order_no": self.order_no.value,
            "contract_no": self.contract_no.value,
            "delivery_place": self.delivery_place.value,
            "request_dept": self.request_dept.value,
            "order_manager": self.order_manager.value,
            "total_amount_text": self.total_amount_text.value,
            "total_amount_krw": self.total_amount_krw.value,
            "note_text": self.note_text.value,
            "payment_condition": self.payment_condition.value,
            "items": items,
        }

    # =====================================================
    # ☑️ 저장 버튼
    # =====================================================
    def save_data(self, e):
        # ⭐ 저장 전에 최신 총합계/한글 금액 상태를 다시 반영
        self.update_summary()

        # ⭐ 저장 버튼 클릭 시 입력 데이터를 수집하여 구조화된 형태로 준비
        data = self.collect_data()

        # ⭐ 저장 버튼 클릭 시 입력 데이터를 수집하여 콘솔에 출력되도록 처리
        print("===== 발주서 저장 데이터 =====")
        print(data)

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("발주서가 저장되었습니다."),
            open=True,
        )
        self.page.update()

    # =====================================================
    # ☑️ 닫기 버튼
    # =====================================================
    def close_dialog(self, e=None):
        self.page.pop_dialog()
        self.page.update()

    # =====================================================
    # ☑️ 전체 콘텐츠
    # =====================================================
    def build_dialog_content(self):
        return ft.Container(
            width=DIALOG_WIDTH,
            height=DIALOG_HEIGHT,
            bgcolor=WHITE,
            border_radius=12,
            padding=20,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                "발주서 입력",
                                size=20,
                                weight=ft.FontWeight.W_700,
                                color=TEXT_COLOR,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                on_click=self.close_dialog,
                            ),
                        ],
                    ),
                    ft.Container(height=16),
                    ft.Container(
                        expand=True,
                        content=ft.Column(
                            scroll=ft.ScrollMode.AUTO,
                            spacing=0,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.build_title_area(),
                                self.build_receiver_section(),
                                self.build_sender_section(),
                                self.build_info_row("발주일자", self.order_date, "납품장소", self.delivery_place),
                                self.build_info_row("발주번호", self.order_no, "요구부서", self.request_dept),
                                self.build_info_row("계약번호", self.contract_no, "발주담당자", self.order_manager),
                                self.build_items_section(),
                                self.build_summary_section(),
                                self.build_note_section(),
                                self.build_condition_section(),
                            ],
                        ),
                    ),
                    ft.Container(height=16),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.ElevatedButton(
                                "닫기",
                                height=42,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=self.close_dialog,
                            ),
                            ft.ElevatedButton(
                                "저장",
                                height=42,
                                style=ft.ButtonStyle(
                                    bgcolor="#2563EB",
                                    color=ft.Colors.WHITE,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                                on_click=self.save_data,
                            ),
                        ],
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 모달 열기
    # =====================================================
    def open(self, e=None):
        self.page.show_dialog(self.dialog)
        self.page.update()


# =========================================================
# ☑️ 메인 실행부
# =========================================================
def main(page: ft.Page):
    page.title = "발주서 모달 예제"
    page.bgcolor = PAGE_BG
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    popup = PurchaseOrderDialog(page)

    purchase_order = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text(
                "발주서 모달창 예제",
                size=26,
                weight=ft.FontWeight.W_700,
            ),
            ft.Container(height=20),
            ft.ElevatedButton(
                "발주서 열기",
                width=220,
                height=50,
                style=ft.ButtonStyle(
                    bgcolor="#111827",
                    color=ft.Colors.WHITE,
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                on_click=popup.open,
            ),
        ],
    )

    page.add(purchase_order)


ft.app(target=main)