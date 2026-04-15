import flet as ft
from components import common as cm


def erp_inventory_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    value="재고관리",
                    size=24,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),
                ft.Text(
                    value="재고관리 메인 화면",
                    size=16,
                    color="#666666",
                ),
            ],
        ),
    )