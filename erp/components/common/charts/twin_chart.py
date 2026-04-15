import flet as ft

CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"

CHART_GRID_COLOR = "#E5E7EB"

BAR_PRIMARY = "#0B4F8A"
BAR_SECONDARY = "#AFAFAF"

CHART_MAX_Y = 100
CHART_HEIGHT = 220


def build_inventory_twin_chart():

    chart_data = [
        ("1월", 45, 36),
        ("2월", 58, 49),
        ("3월", 42, 34),
        ("4월", 76, 63),
        ("5월", 61, 48),
        ("6월", 70, 54),
        ("7월", 52, 43),
    ]

    # ☑️ Y축
    def build_y_axis():
        y_labels = [100, 80, 60, 40, 20, 0]

        return ft.Container(
            width=42,
            height=CHART_HEIGHT,
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                horizontal_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.Text(str(v), size=12, color=TEXT_TERTIARY)
                    for v in y_labels
                ],
            ),
        )

    # ☑️ 차트 영역
    def build_chart_area():

        max_bar_height = 150

        bar_groups = []

        for label, v1, v2 in chart_data:

            h1 = (v1 / CHART_MAX_Y) * max_bar_height
            h2 = (v2 / CHART_MAX_Y) * max_bar_height

            bar_groups.append(
                ft.Container(
                    expand=1,
                    alignment=ft.Alignment(0, 1),
                    content=ft.Column(
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.END,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                                spacing=6,
                                controls=[
                                    ft.Container(
                                        width=14,
                                        height=h1,
                                        bgcolor=BAR_PRIMARY,
                                        border_radius=ft.border_radius.only(
                                            top_left=4,
                                            top_right=4,
                                        ),
                                    ),
                                    ft.Container(
                                        width=14,
                                        height=h2,
                                        bgcolor=BAR_SECONDARY,
                                        border_radius=ft.border_radius.only(
                                            top_left=4,
                                            top_right=4,
                                        ),
                                    ),
                                ],
                            ),
                            ft.Text(
                                label,
                                size=12,
                                color=TEXT_TERTIARY,
                            ),
                        ],
                    ),
                )
            )

        # 그리드
        grid = ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Divider(height=1, color=CHART_GRID_COLOR)
                for _ in range(5)
            ] + [ft.Container()],
        )

        return ft.Stack(
            height=CHART_HEIGHT,
            expand=True,
            controls=[
                grid,
                ft.Container(
                    padding=ft.padding.only(top=16),
                    content=ft.Row(
                        expand=True,
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=bar_groups,
                    ),
                ),
            ],
        )

    # ☑️ 범례
    def build_legend():
        return ft.Row(
            spacing=16,
            controls=[
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=10, height=10, bgcolor=BAR_PRIMARY),
                        ft.Text("입고", size=12),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Container(width=10, height=10, bgcolor=BAR_SECONDARY),
                        ft.Text("출고", size=12),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    controls=[
                        ft.Text("단위: 천원", size=12),
                    ],
                ),
            ],
        )

    return ft.Container(
        height=320,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),
        padding=20,
        content=ft.Column(
            spacing=16,
            controls=[
                ft.Text(
                    "입출고 현황",
                    size=18,
                    weight=ft.FontWeight.W_700,
                    color=TEXT_PRIMARY,
                ),
                build_legend(),
                ft.Row(
                    expand=True,
                    controls=[
                        build_y_axis(),
                        build_chart_area(),
                    ],
                ),
            ],
        ),
    )