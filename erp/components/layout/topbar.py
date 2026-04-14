import flet as ft


TOPBAR_BG = "#004C8C"
TEXT_COLOR = ft.Colors.WHITE
SUBTEXT_COLOR = "#9CC3DF"


def build_erp_topbar():
    return ft.Container(
        height=68,
        bgcolor=TOPBAR_BG,
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.NOTIFICATIONS_NONE,
                    color=TEXT_COLOR,
                    size=20,
                ),
                ft.Container(width=24),
                ft.CircleAvatar(
                    radius=16,
                    bgcolor="#CDA25A",
                    content=ft.Text(
                        value="나",
                        color=TEXT_COLOR,
                        size=12,
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
                            color=TEXT_COLOR,
                            size=13,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            value="lmlmjang@gmail.com",
                            color=SUBTEXT_COLOR,
                            size=10,
                        ),
                    ],
                ),
                ft.Container(width=8),
                ft.Icon(
                    ft.Icons.KEYBOARD_ARROW_DOWN,
                    color=TEXT_COLOR,
                    size=18,
                ),
            ],
        ),
    )