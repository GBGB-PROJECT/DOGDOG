import datetime
import flet as ft

# 🔥 httpx 방식 API 호출로 변경
from api.erp_httpx_api import count_customer_orders, fetch_customer_orders
from components.common.erp_view_widgets import build_text, date_value_box, calendar_icon_box, action_button
from components.common.erp_view_style import *
from components.common.erp_pagination import calc_total_pages, build_pagination_bar
from components.common.erp_datepicker import normalize_datepicker_value, normalize_datepicker_date
from components.common.erp_view_layout import build_lookup_page_layout, build_lookup_table_area


# =========================================================
# 🔥 고객 주문 관리 화면
# - OPD.sales_order + OPD.sales_order_item JOIN 데이터 조회
# - 🔥 검색조건 단순화: 주문번호 / 고객ID / 전화번호 / 배송지 / 상품
# - 주문일은 검색조건에서 제외하고 DatePicker(start_date/end_date)로만 필터링
# - 50개씩 페이지네이션
# - 🔥 추가: address + detail_address를 합친 배송지 컬럼 표시
# =========================================================







def format_money(value):
    if value is None:
        return ""
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def format_plain_number(value):
    if value is None or value == "":
        return ""
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def build_full_table_cell(
    text,
    expand,
    align_x=0,
    weight=ft.FontWeight.W_400,
    color=TEXT_ROW,
    size=12,
):
    return ft.Container(
        expand=expand,
        alignment=ft.Alignment(align_x, 0),
        tooltip=str(text or ""),
        content=ft.Text(
            value=str(text or ""),
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.CENTER if align_x == 0 else (ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT),
            selectable=True,
        ),
    )


def build_product_display(row):
    # 🔥 상품ID만 노출하지 않고 OPD.product_detail의 브랜드/상품명을 같이 표시
    brand = str(row.get("product_brand") or "").strip()
    product_name = str(row.get("product_name") or "").strip()
    product_id = str(row.get("product_id") or "").strip()
    weight = format_plain_number(row.get("product_weight"))

    name = " ".join([part for part in [brand, product_name] if part]).strip()
    if not name:
        name = "상품명 없음"

    spec_parts = []
    if weight:
        spec_parts.append(f"{weight}g")
    if product_id:
        spec_parts.append(f"#{product_id}")

    spec_text = f" ({' / '.join(spec_parts)})" if spec_parts else ""
    return f"{name}{spec_text}"


def format_datetime_text(value):
    # 🔥 주문일 화면 표시용 포맷
    # - API/DB에서 datetime이 오면 "2026-05-31T20:04:25"처럼 내려올 수 있음
    # - 고객 주문 관리 화면에서는 날짜만 보여주기 위해 T와 시간 제거
    if not value:
        return ""

    text = str(value).strip()

    if "T" in text:
        return text.split("T")[0]

    if " " in text:
        return text.split(" ")[0]

    return text[:10]


def customer_order_db_row_adapter(db_rows: list, page_no: int):
    rows = []
    start_no = ((page_no - 1) * PAGE_SIZE) + 1

    for index, row in enumerate(db_rows, start=start_no):
        rows.append(
            {
                "no": str(index),
                "order_number": row.get("order_number", ""),
                "order_date": format_datetime_text(row.get("order_date", "")),
                "sales_order_id": row.get("sales_order_id", ""),
                "customer_id": row.get("customer_id", ""),
                "recipient": row.get("recipient", ""),
                "phone": row.get("phone", ""),
                "address": row.get("address", ""),
                "product_id": row.get("product_id", ""),
                "product_detail_id": row.get("product_detail_id", ""),
                "product_brand": row.get("product_brand", ""),
                "product_name": row.get("product_name", ""),
                "product_weight": row.get("product_weight", ""),
                "product_display": build_product_display(row),
                "quantity": row.get("quantity", ""),
                "retail_price": format_money(row.get("retail_price", "")),
                "total_amount": format_money(row.get("total_amount", "")),
                "payment_billing_id": row.get("payment_billing_id", ""),
                # 🔥 추가: OPD.payment.pay_number를 결제번호로 상세창에 표시한다.
                "pay_number": row.get("pay_number", ""),
            }
        )

    return rows


def erp_customer_order_view():
    page_title = "고객 주문 관리"

    rows_state = []

    selected_start = {"value": None}
    selected_end = {"value": None}
    search_type_value = {"value": "order_number"}

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

    result_text = ft.Text("불러오는 중입니다.", size=13, color=TEXT_SECONDARY)
    table_rows_holder = ft.Column(spacing=0)
    pagination_holder = ft.Container()

    # 🔥 추가: 검색/날짜 조건 사용 후에만 보이는 초기화 버튼 자리
    reset_button_holder = ft.Container(visible=False)

    # =========================================================
    # 🔥 수정: 배송지 컬럼 추가에 맞춰 컬럼 비율 재조정
    # =========================================================
    col_expand = {
        "no": 3,
        "order_number": 8,
        "order_date": 7,
        "customer_id": 5,
        "recipient": 8,
        "phone": 7,
        "address": 12,
        "product_display": 18,
        "quantity": 4,
        "total_amount": 7,
    }

    search_type_labels = {
        "order_number": "주문번호",
        "customer_id": "고객ID",
        "recipient": "배송수령인",
        "phone": "전화번호",
        "address": "배송지",
        "product": "상품",  # 🔥 상품ID/브랜드/상품명 통합 검색
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
            format_date_text(selected_start["value"]),
            on_click=open_start_picker,
        )
        start_icon_holder.content = calendar_icon_box(on_click=open_start_picker)

        end_field_holder.content = date_value_box(
            format_date_text(selected_end["value"]),
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

        end_date_picker.first_date = selected_start["value"] or datetime.datetime(2000, 1, 1)

        if selected_end["value"]:
            end_date_picker.value = selected_end["value"]
        elif selected_start["value"]:
            end_date_picker.value = selected_start["value"]

        end_date_picker.open = True
        page.update()

    search_type_text = ft.Text(
        search_type_labels[search_type_value["value"]],
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
            or search_type_value["value"] != "order_number"
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
                content=ft.Text(label, size=13, color=FIELD_TEXT, weight=ft.FontWeight.W_500),
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
                        content=ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=18, color="#4B5563"),
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
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            content=ft.Row(
                expand=True,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_full_table_cell("No", col_expand["no"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("주문번호", col_expand["order_number"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("주문일", col_expand["order_date"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("고객ID", col_expand["customer_id"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("배송수령인", col_expand["recipient"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("전화번호", col_expand["phone"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("배송지", col_expand["address"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("상품", col_expand["product_display"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("상품수량", col_expand["quantity"], 0, ft.FontWeight.W_700),
                    build_full_table_cell("상품금액", col_expand["total_amount"], 0, ft.FontWeight.W_700),
                ],
            ),
        )

    def build_detail_line(label, value):
        return ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                ft.Container(
                    width=86,
                    content=ft.Text(label, size=12, color=TEXT_SECONDARY, weight=ft.FontWeight.W_700),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Text(str(value or "-"), size=12, color=TEXT_PRIMARY, selectable=True),
                ),
            ],
        )

    def open_order_detail_modal(e, row):
        # 🔥 추가 API 호출 없이 현재 행 데이터만 보여주므로 화면 렉이 거의 없다.
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("주문상품 상세", size=18, weight=ft.FontWeight.W_700),
            content=ft.Container(
                width=520,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[
                        build_detail_line("주문번호", row.get("order_number")),
                        build_detail_line("주문ID", row.get("sales_order_id")),
                        build_detail_line("주문일", row.get("order_date")),
                        build_detail_line("고객ID", row.get("customer_id")),
                        build_detail_line("배송수령인", row.get("recipient")),
                        build_detail_line("전화번호", row.get("phone")),
                        build_detail_line("배송지", row.get("address")),
                        build_detail_line("상품", row.get("product_display")),
                        build_detail_line("상품ID", row.get("product_id")),
                        build_detail_line("상품상세ID", row.get("product_detail_id")),
                        build_detail_line("판매단가", row.get("retail_price")),
                        build_detail_line("상품수량", row.get("quantity")),
                        build_detail_line("상품금액", row.get("total_amount")),
                        build_detail_line("결제번호", row.get("pay_number")),
                    ],
                ),
            ),
            actions=[
                ft.TextButton("닫기", on_click=lambda close_e: close_order_detail_modal(close_e, dialog)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        e.page.show_dialog(dialog)
        e.page.update()

    def close_order_detail_modal(e, dialog):
        dialog.open = False
        e.page.update()

    def build_table_row(row):
        return ft.Container(
            padding=ft.Padding.only(left=14, right=14, top=14, bottom=14),
            border=ft.border.only(bottom=ft.BorderSide(1, TABLE_BORDER)),
            bgcolor=CARD_BG,
            ink=True,
            on_click=lambda e, selected_row=row: open_order_detail_modal(e, selected_row),
            content=ft.Row(
                expand=True,
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    build_full_table_cell(row.get("no", ""), col_expand["no"], 0),
                    build_full_table_cell(row.get("order_number", ""), col_expand["order_number"], 0),
                    build_full_table_cell(row.get("order_date", ""), col_expand["order_date"], 0),
                    build_full_table_cell(row.get("customer_id", ""), col_expand["customer_id"], 0),
                    build_full_table_cell(row.get("recipient", ""), col_expand["recipient"], 0),
                    build_full_table_cell(row.get("phone", ""), col_expand["phone"], 0),
                    build_full_table_cell(row.get("address", ""), col_expand["address"], 0),
                    build_full_table_cell(row.get("product_display", ""), col_expand["product_display"], -1),
                    build_full_table_cell(row.get("quantity", ""), col_expand["quantity"], 0),
                    build_full_table_cell(
                        row.get("total_amount", ""),
                        col_expand["total_amount"],
                        0,
                        ft.FontWeight.W_700,
                        "#2563EB",
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
                    content=ft.Text("일치하는 정보가 없습니다.", size=14, color=TEXT_SECONDARY),
                )
            )
            return

        for row in filtered_rows:
            table_rows_holder.controls.append(build_table_row(row))

    def fetch_total_count(keyword=""):
        start_date, end_date = get_selected_date_range()
        return count_customer_orders(
            search_type=search_type_value["value"],
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )

    def fetch_customer_order_rows(keyword="", page_no=1):
        offset = (page_no - 1) * PAGE_SIZE
        start_date, end_date = get_selected_date_range()

        db_rows = fetch_customer_orders(
            search_type=search_type_value["value"],
            keyword=keyword,
            limit=PAGE_SIZE,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return customer_order_db_row_adapter(db_rows, page_no)

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
            on_click=None if disabled or page_no is None else lambda e: e.page.run_thread(lambda: move_page(page_no, e.page)),
            content=ft.Text(
                label,
                size=16,
                color=ft.Colors.WHITE if selected else "#0F172A",
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
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
        search_label = search_type_labels.get(search_type_value["value"], "주문번호")
        keyword_text = pagination_state["keyword"] if pagination_state["keyword"] else "없음"

        result_text.value = (
            f"기간기준: 주문일 / "
            f"기간: {start_text} ~ {end_text} / "
            f"검색조건: {search_label} / "
            f"검색어: {keyword_text} / "
            f"전체 주문상품 {pagination_state['total_count']}건 / "
            f"현재 페이지 주문상품 {len(rows_state)}건 / "
            f"{pagination_state['current_page']} / {pagination_state['total_pages']} 페이지"
        )

    def reload_current_page():
        keyword = pagination_state["keyword"]
        current_page = pagination_state["current_page"]

        total_count = fetch_total_count(keyword=keyword)
        total_pages = calc_total_pages(total_count, PAGE_SIZE)

        if current_page > total_pages:
            current_page = total_pages
            pagination_state["current_page"] = current_page

        rows = fetch_customer_order_rows(keyword=keyword, page_no=current_page)

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

        search_type_value["value"] = "order_number"
        search_type_text.value = search_type_labels["order_number"]
        search_field.value = ""

        pagination_state["keyword"] = ""
        pagination_state["current_page"] = 1

        refresh_picker_fields()
        reload_current_page()
        update_reset_button_visibility()
        e.page.update()

    refresh_picker_fields()

    # 🔥 추가: 처음에는 숨겨두고, 검색/날짜 조건이 생기면 표시
    reset_button_holder.content = action_button("초기화", on_click=on_reset_click, width=78, run_async=True)
    update_reset_button_visibility()

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
            # 🔥 미구현 기능 버튼은 사용자 혼란 방지를 위해 숨김
        ],
    )

    class CustomerOrderPage(ft.Container):
        def did_mount(self):
            self.page.run_thread(lambda: (reload_current_page(), self.page.update()))

    return CustomerOrderPage(expand=True, content=page_layout)
