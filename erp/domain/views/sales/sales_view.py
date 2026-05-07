import flet as ft
from components import common as cm

def erp_sales_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Text(
            value="매출관리 화면",
            size=22,
            color=cm.TEXT_PRIMARY,
            weight=ft.FontWeight.W_700,
        ),
    )