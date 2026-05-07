# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def order_success(page: ft.Page, page_name):
    PAYMENT_ID = True
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src="success.png", width=150, height=150),
                dogdog.basic_text(
                    value="똑똑배송 구독이 완료되었습니다." if "subs" in page_name else "주문이 완료되었습니다.", 
                    weight="bold", size=20),
        ]),
        ft.Row([
            dogdog.continue_button(
                value="주문 내역 보기", bgcolor="#E6001A", text_color=ft.Colors.WHITE, 
                on_click=lambda _: page.go("/shop/pay_list"))
        ])
    ] if PAYMENT_ID else [
        dogdog.basic_text(
            value="정상적이지 않은 접근입니다.", weight="bold", size=20),
    ]
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.padding.only(left=10, right=10),
        width=float('inf'),
        expand=True,
        bgcolor="#ffffff",
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=content_column) # type: ignore
    )