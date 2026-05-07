import flet as ft
from components import common as cm


def erp_product_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=14,
            controls=[
                ft.Text(
                    value="상품관리",
                    size=20,
                    weight=ft.FontWeight.W_700,
                    color="#111827",
                ),
                ft.Text(
                    value="좌측 하위 메뉴에서 상품관리 기능을 선택하세요.",
                    size=13,
                    color="#6B7280",
                ),
            ],
        ),
    )