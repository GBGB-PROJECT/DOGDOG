import flet as ft


PAGE_BG = "#F2F2F2"


def erp_sales_view():
    return ft.Container(
        expand=True,
        bgcolor=PAGE_BG,
        padding=20,
        content=ft.Text(
            value="매출관리 화면",
            size=22,
            color="#444444",
            weight=ft.FontWeight.W_700,
        ),
    )