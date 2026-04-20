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
DIALOG_HEIGHT = 900

FIELD_HEIGHT = 42
ROW_HEIGHT = 42
TITLE_HEIGHT = 150

# =========================================================
# ☑️ 문서 전체 공통 폭
# =========================================================
DOC_WIDTH = 1424

# 상단 영역 폭
TITLE_LEFT_WIDTH = 1114
TITLE_RIGHT_WIDTH = 310

APPROVAL_COL_WIDTH = 103

INFO_LABEL_W = 120
INFO_LEFT_VALUE_W = 730
INFO_RIGHT_LABEL_W = 120
INFO_RIGHT_VALUE_W = DOC_WIDTH - INFO_LABEL_W - INFO_LEFT_VALUE_W - INFO_RIGHT_LABEL_W  # 454

# =========================================================
# ☑️ 주문처 / TEL / FAX / 담당자 블록 폭
# =========================================================
CUSTOMER_LABEL_W = 120
MID_LABEL_W = 140
MID_VALUE_W = 260

RIGHT_LABEL_W = 130
RIGHT_INPUT_W = 150
RIGHT_TOTAL_W = RIGHT_LABEL_W + RIGHT_INPUT_W

CUSTOMER_VALUE_W = DOC_WIDTH - CUSTOMER_LABEL_W - MID_LABEL_W - MID_VALUE_W - RIGHT_TOTAL_W
CUSTOMER_BLOCK_HEIGHT = 84

# 하단 품목 폭
COL_NO = 50
COL_LOT = 110
COL_NAME = 120
COL_SPEC = 120
COL_UNIT = 70
COL_BUY = 110
COL_SELL = 110
COL_QTY = 90
COL_BUY_SUM = 120
COL_SELL_SUM = 120
COL_PERIOD = 120

ITEM_TOTAL_WIDTH = (
    COL_NO + COL_LOT + COL_NAME + COL_SPEC + COL_UNIT +
    COL_BUY + COL_SELL + COL_QTY + COL_BUY_SUM + COL_SELL_SUM + COL_PERIOD
)

COL_PERIOD = COL_PERIOD + (DOC_WIDTH - ITEM_TOTAL_WIDTH)


# =========================================================
# ☑️ 숫자 변환 유틸
# =========================================================
def to_int(value):
    # ⭐ 수량/구매단가/판매가 계산 전에 문자열 숫자를 정수로 바꾸는 공통 유틸
    try:
        value = str(value).replace(",", "").strip()
        if value == "":
            return 0
        return int(value)
    except:
        return 0


def format_number(value):
    # ⭐ 계산된 구매가계/판매가계를 10,000 같은 형식으로 표시
    if value in ("", None):
        return ""
    try:
        return f"{int(value):,}"
    except:
        return str(value)


# =========================================================
# ☑️ 공통 셀 박스
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


def box_input(control, width=None, height=FIELD_HEIGHT):
    return ft.Container(
        width=width,
        height=height,
        border=ft.border.all(1, BORDER_COLOR),
        bgcolor=WHITE,
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
# ☑️ 생산지시서 모달 클래스
# =========================================================
class ProductionOrderDialog:
    def __init__(self, page: ft.Page):
        self.page = page

        # -------------------------------------------------
        # ☑️ 상단 기본 정보 컨트롤
        # -------------------------------------------------
        self.instruction_date = build_textfield()
        self.doc_no = build_textfield()
        self.contract_no = build_textfield()

        self.delivery_place = build_textfield()
        self.request_dept = build_textfield()
        self.production_manager = build_textfield()

        self.customer_name = build_textfield()
        self.tel = build_textfield()
        self.fax = build_textfield()
        self.person_in_charge = build_textfield()

        self.approval_1 = build_textfield(text_align=ft.TextAlign.CENTER)
        self.approval_2 = build_textfield(text_align=ft.TextAlign.CENTER)
        self.approval_3 = build_textfield(text_align=ft.TextAlign.CENTER)

        # -------------------------------------------------
        # ☑️ 하단 품목 행 데이터
        # -------------------------------------------------
        # ⭐ 생산지시서 품목 입력 행 18개를 생성해서 문서형 입력 UI 구성
        self.item_rows = []
        for i in range(18):
            self.item_rows.append(self.build_item_row(i + 1))

        # -------------------------------------------------
        # ☑️ 다이얼로그 생성
        # -------------------------------------------------
        # ⭐ ERP 프론트 생산지시서 입력 모달 UI 구현
        self.dialog = ft.AlertDialog(
            modal=True,
            inset_padding=10,
            bgcolor=ft.Colors.TRANSPARENT,
            content_padding=0,
            shape=ft.RoundedRectangleBorder(radius=12),
            content=self.build_dialog_content(),
        )

    # =====================================================
    # ☑️ 품목 한 줄 생성
    # =====================================================
    def build_item_row(self, no: int):
        row_data = {}

        def on_amount_change(e=None):
            # ⭐ 수량·구매단가·판매가 입력 시 금액 자동 계산 기능 구현
            qty = to_int(row_data["qty"].value)
            buy_price = to_int(row_data["buy_price"].value)
            sell_price = to_int(row_data["sell_price"].value)

            buy_total = qty * buy_price
            sell_total = qty * sell_price

            # ⭐ 계산 결과를 읽기 전용 필드에 즉시 반영 처리
            row_data["buy_total"].value = format_number(buy_total) if buy_total else ""
            row_data["sell_total"].value = format_number(sell_total) if sell_total else ""
            self.page.update()

        row_data["no"] = no
        row_data["lot_no"] = build_textfield(text_align=ft.TextAlign.CENTER)
        row_data["product_name"] = build_textfield()
        row_data["spec"] = build_textfield()
        row_data["unit"] = build_textfield(text_align=ft.TextAlign.CENTER)
        row_data["buy_price"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            on_change=on_amount_change,
        )
        row_data["sell_price"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            on_change=on_amount_change,
        )
        row_data["qty"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            on_change=on_amount_change,
        )
        row_data["buy_total"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
        )
        row_data["sell_total"] = build_textfield(
            text_align=ft.TextAlign.RIGHT,
            read_only=True,
        )
        row_data["period"] = build_textfield(text_align=ft.TextAlign.CENTER)

        return row_data

    # =====================================================
    # ☑️ 상단 제목 영역
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
                            "생산지시서",
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
                                        box_input(self.approval_2, width=APPROVAL_COL_WIDTH + 1),
                                    ],
                                ),
                                ft.Row(
                                    spacing=0,
                                    controls=[
                                        box_input(build_textfield(), width=APPROVAL_COL_WIDTH, height=108),
                                        box_input(build_textfield(), width=APPROVAL_COL_WIDTH, height=108),
                                        box_input(build_textfield(), width=APPROVAL_COL_WIDTH + 1, height=108),
                                    ],
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 상단 기본 정보 행
    # =====================================================
    def build_info_row(self, left_title, left_control, right_title, right_control):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label(left_title, width=INFO_LABEL_W),
                    box_input(left_control, width=INFO_LEFT_VALUE_W),
                    box_label(right_title, width=INFO_RIGHT_LABEL_W),
                    box_input(right_control, width=INFO_RIGHT_VALUE_W),
                ],
            ),
        )

# =====================================================
    # ☑️ 담당자 블록
    #     🔥 수정:
    #     - 오른쪽 외곽선이 안 보이던 원인 해결
    #     - 왼쪽 라벨은 고정폭
    #     - 오른쪽 입력칸은 expand=True로 남은 폭만 사용
    # =====================================================
    def build_person_block(self):
        return ft.Container(
            width=RIGHT_TOTAL_W,
            height=CUSTOMER_BLOCK_HEIGHT,
            border=ft.border.all(1, BORDER_COLOR),
            bgcolor=WHITE,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Row(
                spacing=0,
                controls=[
                    ft.Container(
                        width=RIGHT_LABEL_W,
                        height=CUSTOMER_BLOCK_HEIGHT,
                        bgcolor=HEADER_BG,
                        alignment=ft.Alignment(0, 0),
                        border=ft.border.only(
                            right=ft.BorderSide(1, BORDER_COLOR),
                        ),
                        content=ft.Text(
                            "담당자",
                            size=13,
                            color=TEXT_COLOR,
                            weight=ft.FontWeight.W_500,
                            text_align=ft.TextAlign.CENTER,
                        ),
                    ),
                    ft.Container(
                        expand=True,  # 🔥 핵심: width=RIGHT_INPUT_W 쓰지 말고 남은 폭만 차지
                        height=CUSTOMER_BLOCK_HEIGHT,
                        bgcolor=WHITE,
                        alignment=ft.Alignment(0, 0),
                        content=self.person_in_charge,
                    ),
                ],
            ),
        )

    # =====================================================
    # ☑️ 주문처 / TEL / FAX / 담당자 블록
    # =====================================================
    def build_customer_block(self):
        return ft.Container(
            width=DOC_WIDTH,
            content=ft.Row(
                spacing=0,
                controls=[
                    box_label("주문처", width=CUSTOMER_LABEL_W, height=CUSTOMER_BLOCK_HEIGHT),
                    box_input(self.customer_name, width=CUSTOMER_VALUE_W, height=CUSTOMER_BLOCK_HEIGHT),

                    ft.Column(
                        spacing=0,
                        controls=[
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("TEL", width=MID_LABEL_W, bold=True),
                                    box_input(self.tel, width=MID_VALUE_W),
                                ],
                            ),
                            ft.Row(
                                spacing=0,
                                controls=[
                                    box_label("FAX", width=MID_LABEL_W, bold=True),
                                    box_input(self.fax, width=MID_VALUE_W),
                                ],
                            ),
                        ],
                    ),

                    self.build_person_block(),
                ],
            ),
        )

    # =====================================================
    # ☑️ 하단 품목 헤더
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
                    box_label("구매단가", width=COL_BUY, height=44, bold=True),
                    box_label("판매가", width=COL_SELL, height=44, bold=True),
                    box_label("수량", width=COL_QTY, height=44, bold=True),
                    box_label("구매가계", width=COL_BUY_SUM, height=44, bold=True),
                    box_label("판매가계", width=COL_SELL_SUM, height=44, bold=True),
                    box_label("생산기간", width=COL_PERIOD, height=44, bold=True),
                ],
            ),
        )

    # =====================================================
    # ☑️ 하단 품목 한 줄 UI
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
                    box_input(row_data["buy_price"], width=COL_BUY, height=ROW_HEIGHT),
                    box_input(row_data["sell_price"], width=COL_SELL, height=ROW_HEIGHT),
                    box_input(row_data["qty"], width=COL_QTY, height=ROW_HEIGHT),
                    box_input(row_data["buy_total"], width=COL_BUY_SUM, height=ROW_HEIGHT),
                    box_input(row_data["sell_total"], width=COL_SELL_SUM, height=ROW_HEIGHT),
                    box_input(row_data["period"], width=COL_PERIOD, height=ROW_HEIGHT),
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
                "buy_price": row["buy_price"].value,
                "sell_price": row["sell_price"].value,
                "qty": row["qty"].value,
                "buy_total": row["buy_total"].value,
                "sell_total": row["sell_total"].value,
                "period": row["period"].value,
            }

            # ⭐ 값이 들어간 품목 행만 저장 대상에 포함
            has_value = any(str(v).strip() != "" for k, v in item.items() if k != "no")
            if has_value:
                items.append(item)

        return {
            "instruction_date": self.instruction_date.value,
            "doc_no": self.doc_no.value,
            "contract_no": self.contract_no.value,
            "delivery_place": self.delivery_place.value,
            "request_dept": self.request_dept.value,
            "production_manager": self.production_manager.value,
            "customer_name": self.customer_name.value,
            "tel": self.tel.value,
            "fax": self.fax.value,
            "person_in_charge": self.person_in_charge.value,
            "items": items,
        }

    # =====================================================
    # ☑️ 저장 버튼
    # =====================================================
    def save_data(self, e):
        # ⭐ 저장 버튼 클릭 시 입력 데이터를 수집하여 구조화된 형태로 준비
        data = self.collect_data()

        # ⭐ 저장 버튼 클릭 시 입력 데이터를 수집하여 콘솔에 출력되도록 처리
        print("===== 생산지시서 저장 데이터 =====")
        print(data)

        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("생산지시서가 저장되었습니다."),
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
    # ☑️ 다이얼로그 전체 콘텐츠
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
                                "생산지시서 입력",
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
                                self.build_info_row("지시일자", self.instruction_date, "납품장소", self.delivery_place),
                                self.build_info_row("문서번호", self.doc_no, "요구부서", self.request_dept),
                                self.build_info_row("계약번호", self.contract_no, "생산담당자", self.production_manager),
                                self.build_customer_block(),
                                self.build_items_section(),
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
# ☑️ 메인
# =========================================================
def main(page: ft.Page):
    page.title = "생산지시서 모달 예제"
    page.bgcolor = PAGE_BG
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO

    popup = ProductionOrderDialog(page)

    production_order = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "생산지시서 모달창 예제",
                    size=26,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "생산지시서 열기",
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

    page.add(production_order)


ft.app(target=main)