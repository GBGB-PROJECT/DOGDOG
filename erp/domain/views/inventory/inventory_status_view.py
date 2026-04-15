import flet as ft
from components import common as cm


def erp_inventory_status_view():
    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Text(
                    value="상품 재고 관리 > 재고 현황",
                    size=24,
                    color="#222222",
                    weight=ft.FontWeight.W_700,
                ),
                # ☑️ 추가: 상단 년월 + chevron
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=lambda e: print("이전"),
                        ),
                        ft.Text(
                            value="2026년 4월",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color="#222222",
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CHEVRON_RIGHT,
                            icon_size=20,
                            on_click=lambda e: print("다음"),
                        ),
                    ],
                ),
                # ☑️ 🔥 여기 핵심 (가로 2칸)
            ft.Row(
                spacing=16,
                expand=True,
                controls=[

                    # 박스 1
                    ft.Container(
                        expand=1,  # 🔥 가로 비율
                        height=180,  # 🔥 높이 고정
                        bgcolor="#F9FAFB",
                        border_radius=12,
                        padding=16,
                        border=ft.border.all(1, "#E5E7EB"),
                        content=ft.Text("박스 1"),
                    ),

                    # 박스 2
                    ft.Container(
                        expand=1,
                        height=180,
                        bgcolor="#F9FAFB",
                        border_radius=12,
                        padding=16,
                        border=ft.border.all(1, "#E5E7EB"),
                        content=ft.Text("박스 2"),
                    ),
                ],
            ),
        ],
    ),
)