import flet as ft
from components import common as cm


def erp_inventory_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Text(
            value="재고관리 화면",
            size=22,
            color="#444444",
            weight=ft.FontWeight.W_700,
        ),
    )