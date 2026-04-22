import flet as ft
from components import common as cm


def erp_purchase_order_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        alignment=ft.Alignment(0, 0),  # 🔴 중앙 정렬
        content=ft.Text(
            "준비중",
            size=32,
            weight=ft.FontWeight.W_700,
            color="#6B7280",
        ),
    )