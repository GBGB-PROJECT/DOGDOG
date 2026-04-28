'''
shop/
├── order_page.py              # 전체 화면
├── components/
│   ├── order_info_section.py  # 주문자 정보
│   ├── delivery_info_section.py # 배송 정보
│   ├── order_product_card.py  # 주문 상품
│   ├── coupon_point_section.py # 쿠폰 & 적립금
│   ├── payment_summary.py     # 결제 금액
│   └── payment_method.py      # 자동 결제 등록
'''
import flet as ft
import components as dogdog


def shop_payment_content():

    return ft.Column(
        scroll=ft.ScrollMode.AUTO,
        spacing=20,
        controls=[
            orderer_info_section(),
            delivery_info_section(),
            order_product_section(),
            coupon_point_section(),
            payment_summary_section(),
            payment_method_section(),
            agreement_section(),
            payment_button(),
        ]
    )


# ----------------------------
# 주문자 정보
# ----------------------------
def orderer_info_section():
    return section_box(
        "주문자 정보",
        ft.Column([
            dogdog.input_textfield(label="이름"),
            dogdog.input_textfield(label="전화번호"),
        ])
    )


# ----------------------------
# 배송 정보
# ----------------------------
def delivery_info_section():
    return section_box(
        "배송 정보",
        ft.Column([
            dogdog.input_textfield(label="수령인"),
            dogdog.input_textfield(label="전화번호"),
            dogdog.input_textfield(label="주소"),
        ])
    )


# ----------------------------
# 주문 상품
# ----------------------------
def order_product_section():
    return section_box(
        "주문 상품",
        ft.Column([
            ft.Row([
                ft.Text("상품명 예시"),
                ft.Text("1개"),
                ft.Text("12,000원"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ])
    )


# ----------------------------
# 쿠폰 & 적립금
# ----------------------------
def coupon_point_section():
    return section_box(
        "쿠폰 & 적립금",
        ft.Column([
            dogdog.input_textfield(label="쿠폰 코드 입력"),
            dogdog.input_textfield(label="적립금 사용"),
        ])
    )


# ----------------------------
# 결제 금액 요약
# ----------------------------
def payment_summary_section():
    return section_box(
        "결제 금액",
        ft.Column([
            price_row("상품 금액", "12,000원"),
            price_row("배송비", "3,000원"),
            price_row("할인", "-2,000원"),
            ft.Divider(),
            price_row("총 결제 금액", "13,000원", bold=True),
        ])
    )


# ----------------------------
# 자동 결제 등록
# ----------------------------
def payment_method_section():
    return section_box(
        "자동 결제 등록",
        ft.Column([
            ft.Text("카드를 등록하면 자동으로 결제됩니다."),
            dogdog.flat_button("카드 등록", on_click=lambda e: None),
        ])
    )


# ----------------------------
# 약관 동의
# ----------------------------
def agreement_section():
    return section_box(
        "약관 동의",
        ft.Column([
            ft.Checkbox(label="전체 동의"),
            ft.Checkbox(label="결제 및 개인정보 동의"),
        ])
    )


# ----------------------------
# 결제 버튼
# ----------------------------
def payment_button():
    return ft.Container(
        padding=10,
        content=ft.ElevatedButton(
            text="결제하기",
            width=float("inf"),
            height=50,
            bgcolor="#F20A1A",  # shop용 빨간색
            color="white",
            on_click=lambda e: print("결제 요청"),
        )
    )


# ----------------------------
# 공통 박스 UI
# ----------------------------
def section_box(title, content):
    return ft.Container(
        padding=15,
        bgcolor="white",
        border_radius=10,
        content=ft.Column([
            dogdog.basic_text(title, size=16),
            content
        ])
    )


def price_row(label, value, bold=False):
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        controls=[
            ft.Text(label, weight=ft.FontWeight.BOLD if bold else None),
            ft.Text(value, weight=ft.FontWeight.BOLD if bold else None),
        ]
    )

def shop_page(page: ft.Page):

    return ft.Column(
        controls=[
            # (다른 사람이 만들 부분)
            # dogdog.shop_top_bar()
            # dogdog.sub_top_bar()

            shop_payment_content(),

            # dogdog.bottom_nav()
        ]
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