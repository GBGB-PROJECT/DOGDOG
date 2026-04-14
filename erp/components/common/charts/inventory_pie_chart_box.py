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
        padding=ft.padding.symmetric(vertical=4),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        ft.Container(
                            width=10,
                            height=10,
                            border_radius=999,
                            bgcolor=color,
                        ),
                        ft.Text(
                            label,
                            size=12,
                            color=TEXT_PRIMARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    ],
                ),
                ft.Text(
                    percent,
                    size=12,
                    color=TEXT_SECONDARY,
                    weight=ft.FontWeight.W_600,
                ),
            ],
        ),
    )


def build_inventory_pie_chart_box():
    return ft.Container(
        width=480,  # ☑️ 수정: 기존 440 -> 480 / 카드 전체 조금 더 확대
        height=320,  # ☑️ 수정: 기존 250 -> 270 / 카드 높이도 확대
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),
        padding=18,  # ☑️ 수정: 기존 16 -> 18 / 내부 여백 확대
        content=ft.Column(
            spacing=18,  # ☑️ 수정: 기존 16 -> 18 / 내부 간격 확대
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "재고 현황 (2026/04/01)",
                            size=19,  # ☑️ 수정: 기존 18 -> 19
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=24,  # ☑️ 수정: 기존 22 -> 24
                            icon_color=TEXT_PRIMARY,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=14,  # ☑️ 수정: 기존 12 -> 14 / 차트-범례 사이 간격 확대
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=160,  # ☑️ 수정: 기존 140 -> 160 / 차트 영역 확대
                            height=140,  # ☑️ 수정: 기존 120 -> 140
                            alignment=ft.Alignment(0, 0),
                            content=fch.PieChart(
                                sections=[
                                    fch.PieChartSection(
                                        value=60,
                                        color=PIE_BLUE,
                                        radius=17,  # ☑️ 수정: 기존 15 -> 17 / 차트 크기 확대
                                    ),
                                    fch.PieChartSection(
                                        value=25,
                                        color=PIE_SKY,
                                        radius=17,  # ☑️ 수정
                                    ),
                                    fch.PieChartSection(
                                        value=15,
                                        color=PIE_LIGHT,
                                        radius=17,  # ☑️ 수정
                                    ),
                                ],
                                sections_space=4,
                                center_space_radius=46,  # ☑️ 수정: 기존 40 -> 46 / 가운데 반경 확대
                                center_space_color=CARD_BG,
                            ),
                        ),
                        ft.Container(
                            expand=True,
                            content=ft.Column(
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.START,
                                spacing=9,  # ☑️ 수정: 기존 8 -> 9 / 범례 간격 소폭 확대
                                controls=[
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(
                                                "카테고리",
                                                size=12,
                                                color=TEXT_MUTED,
                                            ),
                                            ft.Text(
                                                "%",
                                                size=12,
                                                color=TEXT_MUTED,
                                            ),
                                        ],
                                    ),
                                    ft.Container(
                                        width=220,  # ☑️ 수정: 기존 200 -> 220 / divider 길이 확대
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