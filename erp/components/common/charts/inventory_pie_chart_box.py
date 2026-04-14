import flet as ft
import flet_charts as fch


CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
TEXT_MUTED = "#9CA3AF"

PIE_BLUE = "#0B4F8A"
PIE_SKY = "#4DA3D9"
PIE_LIGHT = "#BFD9EA"


def _legend_item(color: str, label: str, percent: str):
    return ft.Container(
        padding=ft.padding.symmetric(vertical=6),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(
                            width=12,
                            height=12,
                            border_radius=999,
                            bgcolor=color,
                        ),
                        ft.Text(
                            label,
                            size=14,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                ),
                ft.Text(
                    percent,
                    size=14,
                    color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        ),
    )


def build_inventory_pie_chart_box():
    return ft.Container(
        width=600,
        height=300,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),  # 🟥 추가: 카드 전체 테두리
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                # 상단 제목줄
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "재고 현황 (2026/04/01)",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=26,
                            icon_color=TEXT_PRIMARY,
                        ),
                    ],
                ),

                # 차트 + 범례
                ft.Row(
                    expand=True,
                    spacing=24,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                        width=220,
                        height=180,
                        alignment=ft.Alignment(0, 0),
                        content=fch.PieChart(
                        sections=[
                            fch.PieChartSection(
                                value=60,
                                color=PIE_BLUE,
                                radius=25,  # ☑️ 차트 두께 줄임 
                            ),
                            fch.PieChartSection(
                                value=25,
                                color=PIE_SKY,
                                radius=25,
                            ),
                            fch.PieChartSection(
                                value=15,
                                color=PIE_LIGHT,
                                radius=25,
                            ),
                        ],
                        sections_space=6,  # ☑️ 유지 (간격 핵심)
                        center_space_radius=75,  # ☑️ 차트 크기 확대 
                        center_space_color=CARD_BG,
                        expand=True,
                    )
                    ),

                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=12,
                                controls=[
                                    # ✅ 헤더
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(
                                                "카테고리",
                                                size=13,
                                                color=TEXT_MUTED,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                            ft.Text(
                                                "%",
                                                size=13,
                                                color=TEXT_MUTED,
                                                weight=ft.FontWeight.W_600,
                                            ),
                                        ],
                                    ),
                                    # ✅ 짧은 divider
                                    ft.Container(
                                        width=320,
                                        height=1,
                                        bgcolor="#D1D5DB",
                                    ),
                                    _legend_item(PIE_BLUE, "건사료", "60%"),
                                    _legend_item(PIE_SKY, "습식사료", "25%"),
                                    _legend_item(PIE_LIGHT, "간식", "15%"),
                                ],
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )