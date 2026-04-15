import flet as ft
from ..common import color as c

def build_erp_topbar():
    return ft.Container(
        height=68,
        bgcolor=c.MAIN_COLOR,
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.NOTIFICATIONS_NONE,
                    color=ft.Colors.WHITE,
                    size=20,
                ),
                ft.Container(width=24),
                # 🔥🔥🔥 [기존 CircleAvatar → 이미지로 교체]
                ft.Container(
                    width=32,   # 🔥 기존 radius=16 → 지름 32로 맞춤
                    height=32,
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src="leader.png",
                        fit=ft.BoxFit.COVER,
                    ),
                ),
                ft.Container(width=10),
                ft.Column(
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            value="나팀장",
                            color=ft.Colors.WHITE,
                            size=13,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            value="lmlmjang@gmail.com",
                            color=c.SUBTEXT_COLOR,
                            size=10,
                        ),
                    ],
                ),
                ft.Container(width=8),
                ft.Icon(
                    ft.Icons.KEYBOARD_ARROW_DOWN,
                    color=ft.Colors.WHITE,
                    size=18,
                ),
            ],
        ),
    )