'''
shop/
├── order_page.py              # 전체 화면
├── components/
│   ├── order_info_section.py  # 주문자 정보
│   ├── delivery_info_section.py # 배송 정보
│   ├── order_product_card.py  # 주문 상품
│   ├── payment_summary.py     # 결제 금액
│   └── payment_method.py      # 자동 결제 등록
'''
#flet run --web domains/shop/views/subs_payment.py

import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(APP_DIR))

import flet as ft
import components as dogdog
from domains.shop.views import address

SHOP_RED = "#E6001A"
BORDER = ft.Colors.GREY_300
TEXT_GREY = ft.Colors.GREY_600
DOT_GREY = ft.Colors.GREY_400

LABEL_TEXT_SIZE = 13
VALUE_TEXT_SIZE = 15

# -------------------------------------------------------------------------------------------------
# 주문자 정보
# -------------------------------------------------------------------------------------------------
def orderer_info_section():
    return section_box(
        "주문자 정보",
        ft.Column(
            spacing=0,
            controls=[
                line_input("이름", hint="최대 10자로 작성해주세요"),
                line_input("전화번호", hint="010-0000-0000"),
            ]
        )
    )


# -------------------------------------------------------------------------------------------------
# 배송 정보
# -------------------------------------------------------------------------------------------------
def delivery_info_section(page, address_value=""):
    return section_box(
        "배송 정보",
        ft.Column(
            spacing=0,
            controls=[
                line_input("이름", hint="최대 10자로 작성해주세요"),
                line_input("전화번호", hint="010-0000-0000"),
                line_address_input(page, "배송주소", address_value),
                dropdown_input(
                    label="배송메모(선택)",
                    options=[
                        "요청사항을 선택해주세요.",
                        "문 앞에 배송해주세요.",
                        "경비실에 맡겨주세요.",
                        "배송 전에 연락주세요.",
                        "택배함에 넣어주세요."
                    ]
                ),
            ]
        )
    )


# -------------------------------------------------------------------------------------------------
# 주문 상품
# -------------------------------------------------------------------------------------------------
def order_product_section():
    count_amount = 1
    count_text = ft.Text(str(count_amount), size=14)

    def up_amount(e):
        nonlocal count_amount
        count_amount += 1
        count_text.value = str(count_amount)
        count_text.update()

    def down_amount(e):
        nonlocal count_amount
        if count_amount > 1:
            count_amount -= 1
            count_text.value = str(count_amount)
            count_text.update()


    return section_box(
        "주문 상품",
        ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("상품명", size=14),
                        ft.Text("가장 맛있는 사료, 30일", size=14),
                    ]
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("상품 수량", size=14),
                        ft.Row(
                            spacing=8,
                            controls=[
                                ft.IconButton(ft.Icons.REMOVE_CIRCLE_OUTLINE, icon_size=16, 
                                        icon_color=TEXT_GREY, on_click=down_amount),
                                count_text,
                                ft.IconButton(ft.Icons.ADD_CIRCLE_OUTLINE, icon_size=16, 
                                        icon_color=TEXT_GREY, on_click=up_amount),
                            ]
                        )
                    ]
                ),
            ]
        )
    )

# -------------------------------------------------------------------------------------------------
# 결제 금액 요약
# -------------------------------------------------------------------------------------------------
def payment_summary_section():
    return section_box(
        "최종 결제 금액",
        ft.Column([
            price_row("상품 가격", "90,000원"),
            price_row("똑똑 배송 할인", "-3,000원", red=True),
            price_row("배송비", "0원"),
            price_row("", ""),
            # ft.Divider(),
            price_row("총 결제 금액", "87,000원", bold=True),
        ])
    )


# ----------------------------
# 자동 결제 등록
# ----------------------------
def payment_method_section():
    return section_box(
        "자동 결제 등록",
        ft.Row(
            spacing=8,
            controls=[
                method_button("카드"),
                method_button("간편결제"),
            ]
        )
    )


# -------------------------------------------------------------------------------------------------
# 약관 동의
# -------------------------------------------------------------------------------------------------
def agreement_section():
    return ft.Container(
        padding=ft.padding.only(left=0, right=15, top=5, bottom=12),
        content=ft.Row(
            spacing=3,
            controls=[
                ft.Checkbox(value=False, scale=0.9, overlay_color=TEXT_GREY),
                ft.Text(
                    "주문하실 상품 및 결제, 주문정보를 확인했으며 이에 동의합니다. (필수)",
                    size=11.5,
                    color=TEXT_GREY,
                )
            ]
        )
    )


# -------------------------------------------------------------------------------------------------
# 결제 버튼
# -------------------------------------------------------------------------------------------------
def payment_button():
    return ft.Container(
        expand=9,
        height=50,
        ink=True,
        on_click=lambda e: print("결제 요청"),
        bgcolor="#E6001A",
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        content=ft.Text(
            value="결제하기",
            size=14,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.WHITE,
        )
    )


# -------------------------------------------------------------------------------------------------
# 공통 박스 UI
# -------------------------------------------------------------------------------------------------
# 구역 박스
def section_box(title, content):
    return ft.Container(
        padding=15,
        content=ft.Column([
            dogdog.basic_text(title, size=16, weight="bold"),
            content,
            ft.Divider(),
        ])
    )

# 금액 line
def price_row(label, value, bold=False, red=False):
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text(label, 
                    weight=ft.FontWeight.BOLD if bold else None,
                    color="#E6001A" if red else None),
            ft.Text(value, 
                    weight=ft.FontWeight.BOLD if bold else None,
                    color="#E6001A" if red else None),
        ]
    )

# line input
def line_input(label, value="", hint=None, password=False):
    text_field=ft.TextField(
        value=value,
        hint_text=hint,
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_500
        ),
        password=password,
        border=ft.InputBorder.NONE,
        text_size=VALUE_TEXT_SIZE,
        content_padding=ft.padding.only(bottom=10),
    )
    
    def clear_text(e):
        text_field.value = ""
        text_field.update()
    
    return ft.Container(
        margin=ft.margin.only(bottom=12),
        height=52,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(label, size=LABEL_TEXT_SIZE, color=TEXT_GREY),
                        text_field,
                    ],
                ),
                ft.Container(
                    alignment=ft.Alignment(0, 2),
                    content=ft.IconButton(
                        icon=ft.Icons.CANCEL,
                        icon_size=16,
                        icon_color=TEXT_GREY,
                        on_click=clear_text,
                    )
                )
            ],
        ),
    )



# 배송 주소 --------------------------------
def line_address_input(page, label, address_value=""):
    address_field = ft.TextField(
        value=address_value,
        hint_text="배송주소를 등록해주세요.",
        hint_style=ft.TextStyle(
            color=ft.Colors.GREY_500
        ),
        border=ft.InputBorder.NONE,
        height=30,
        text_size=VALUE_TEXT_SIZE,
        content_padding=ft.padding.only(bottom=10),
    )

    def open_address_page(e):
        page.clean()
        def receive_address(data):
            page.clean()
            shop_page(page, address_value=data.get('full_address'))

        address.main(page, on_complete=receive_address)
    
    return ft.Container(
        margin=ft.margin.only(bottom=12),
        height=52,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=0,
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(label, size=LABEL_TEXT_SIZE, color=TEXT_GREY),
                        address_field,
                    ],
                ),
                ft.Container(
                    alignment=ft.Alignment(0, 0.8),
                    content=method_button(
                        "주소검색", expand=False, width=70, on_click=open_address_page),
                ),
            ],
        ),
    )


# 박스
def method_button(text, expand=True, width=None, on_click=lambda e: print("클릭")):
    return ft.Container(
        expand=expand,
        height=26,
        width=width,
        on_click=on_click,
        bgcolor=ft.Colors.GREY_300,
        border_radius=4,
        alignment=ft.Alignment.CENTER,
        content=ft.Text(text, size=13),
    )

# 배송 요청사항 드롭다운
def dropdown_input(label, value=None, options=None):
    return ft.Container(
        height=58,
        border=ft.border.only(bottom=ft.BorderSide(1, BORDER)),
        content=ft.Column(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text(label, size=LABEL_TEXT_SIZE, color=TEXT_GREY),
                ft.Row(
                    controls=[
                        ft.Dropdown(
                            expand=True,  # 길게
                            value=value,
                            hint_text="요청사항을 선택해주세요.",
                            hint_style=ft.TextStyle(
                                color=ft.Colors.GREY_500
                            ),
                            options=[
                                ft.DropdownOption(key=opt, text=opt)
                                for opt in (options or [])
                            ],
                            bgcolor=ft.Colors.WHITE,
                            border=ft.InputBorder.NONE,
                            height=34,
                            text_size=VALUE_TEXT_SIZE,
                            content_padding=ft.padding.only(left=0, right=0),
                            trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                            selected_trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                        ),
                    ],
                ),
            ],
        ),
    )

# ---------------------------------------------------------------------------------------------------
def shop_payment_content(page, address_value=""):
    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=0,
        controls=[
            orderer_info_section(),
            delivery_info_section(page, address_value),
            order_product_section(),
            payment_summary_section(),
            payment_method_section(),
            agreement_section(),
            payment_button(),
        ]
    )

def shop_page(page: ft.Page, address_value=""):
    page.bgcolor = ft.Colors.WHITE
    page.scroll = ft.ScrollMode.AUTO
    page.add(
        ft.Container(
            padding=20,
            content=shop_payment_content(page, address_value),
        )
    )

if __name__ == "__main__":
    import webbrowser
    import os

    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None

    ft.run(
        shop_page,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        port=34636,
    )