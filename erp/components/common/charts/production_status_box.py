import flet as ft
from backend.api.erp_home_view_api import *
from components import common as cm

def _vertical_progress(value: float):
    # value: 0.0 ~ 1.0
    return ft.Container(
        width=28,
        height=150,
        alignment=ft.Alignment(0, 0),
        content=ft.RotatedBox(
            quarter_turns=3,
            content=ft.ProgressBar(
                width=140,
                value=value,
                bgcolor=cm.BORDER_LIGHT,
                color=cm.BAR_ACTIVE,
                border_radius=10,
                bar_height=10,
            ),
        ),
    )

def _mini_progress_panel(title: str, values: list[float]):
    bars = [_vertical_progress(v) for v in values[:7]]  # ☑️ 

    y_labels = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        height=150,
        controls=[
            ft.Text(f"{i}k", size=11, color=cm.TEXT_SECONDARY)
            for i in range(5,0,-1)
        ],
    )

    return ft.Container(
        expand=True,
        height=220,
        bgcolor=cm.PAGE_BG,
        border_radius=14,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            title,
                            size=15,
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.Container(
                            height=30,
                            padding=ft.padding.symmetric(horizontal=10),
                            border_radius=8,
                            bgcolor="#99F6E4",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                "+12%",
                                size=12,
                                color=cm.TEXT_PRIMARY,
                                weight=ft.FontWeight.W_500,
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    spacing=10,
                    controls=[
                        y_labels,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            expand=True,
                            controls=bars,
                        ),
                    ],
                ),
            ],
        ),
    )

def build_production_status_box():
    data = get_production_defect_rate()
    production_rate = data['production_rate']
    defect_rate = data['defect_rate'] 

    return ft.Container(
        expand=True,
        bgcolor=cm.PAGE_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "생산현황 (2026/04/13)",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=26,
                            icon_color=cm.TEXT_PRIMARY,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        _mini_progress_panel("생산 달성률", production_rate),
                        _mini_progress_panel("불량률", defect_rate),
                    ],
                ),
            ],
        ),
    )