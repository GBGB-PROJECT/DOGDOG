import flet as ft


def erp_customer_view():
    # 🔥 수정: 고객관리 대분류 클릭 시 기존 목록 화면을 바로 띄우지 않고 메인 텍스트만 표시
    return ft.Container(
        expand=True,
        bgcolor="#F5F5F5",
        alignment=ft.Alignment(0, 0),
        content=ft.Text(
            value="고객관리",
            size=28,
            weight=ft.FontWeight.W_700,
            color="#111827",
        ),
    )
