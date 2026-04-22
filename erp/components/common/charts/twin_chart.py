import flet as ft

CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"

CHART_GRID_COLOR = "#E5E7EB"

BAR_PRIMARY = "#0B4F8A"
BAR_SECONDARY = "#AFAFAF"

CHART_MAX_Y = 100

# ☑️ 전체 차트 높이/플롯 높이 분리
PLOT_HEIGHT = 300          # 실제 막대와 그리드가 그려지는 높이
BOTTOM_LABEL_AREA = 34     # 하단 월 라벨 영역 높이
CHART_HEIGHT = PLOT_HEIGHT + BOTTOM_LABEL_AREA


# =========================================================
# ☑️ 공통 twin chart
# =========================================================
def build_twin_chart(
    title="입출고 현황",
    legend_primary="입고",
    legend_secondary="출고",
    unit_text="단위: 천원",
    chart_data=None,
):
    if chart_data is None:
        chart_data = [
            ("1월", 20, 35),
            ("2월", 43, 50),
            ("3월", 13, 35),
            ("4월", 40, 65),
            ("5월", 58, 75),
            ("6월", 35, 55),
        ]

    # ☑️ 수정: 0은 따로 그릴 거라서 여기서는 제외
    y_axis_labels = ["100k", "80k", "60k", "40k", "20k"]
    y_step = PLOT_HEIGHT / 5

    # ☑️ Y축
    def build_y_axis():
        return ft.Container(
            width=58,
            height=CHART_HEIGHT,
            padding=ft.padding.only(right=10),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=y_step,
                        alignment=ft.Alignment(1, -1),
                        content=ft.Text(
                            value=label,
                            size=12,
                            color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    )
                    for label in y_axis_labels
                ] + [
                    # ☑️ 수정: 0은 바닥선 기준에 한 번만 출력
                    ft.Container(
                        height=BOTTOM_LABEL_AREA,
                        alignment=ft.Alignment(1, -1),
                        content=ft.Text(
                            value="0",
                            size=12,
                            color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    )
                ],
            ),
        )

    # ☑️ 막대 1쌍
    def build_bar_pair(label, v1, v2):
        h1 = max((v1 / CHART_MAX_Y) * PLOT_HEIGHT, 4)
        h2 = max((v2 / CHART_MAX_Y) * PLOT_HEIGHT, 4)

        return ft.Container(
            expand=True,
            content=ft.Column(
                spacing=0,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        height=PLOT_HEIGHT,
                        alignment=ft.Alignment(0, 1),
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            spacing=14,
                            controls=[
                                ft.Container(
                                    width=34,
                                    height=h1,
                                    bgcolor=BAR_PRIMARY,
                                    border_radius=ft.border_radius.only(
                                        top_left=3,
                                        top_right=3,
                                    ),
                                ),
                                ft.Container(
                                    width=34,
                                    height=h2,
                                    bgcolor=BAR_SECONDARY,
                                    border_radius=ft.border_radius.only(
                                        top_left=3,
                                        top_right=3,
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        height=BOTTOM_LABEL_AREA,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            value=label,
                            size=12,
                            color=TEXT_SECONDARY,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                ],
            ),
        )

    # ☑️ 차트 영역
    def build_chart_area():
        grid_controls = []

        # ☑️ 수정: 100,80,60,40,20 라인
        for _ in range(5):
            grid_controls.append(
                ft.Container(
                    height=y_step,
                    border=ft.border.only(
                        top=ft.BorderSide(1, CHART_GRID_COLOR)
                    ),
                )
            )

        # ☑️ 수정: 0 기준선
        grid_controls.append(
            ft.Container(
                height=0,
                border=ft.border.only(
                    top=ft.BorderSide(1, CHART_GRID_COLOR)
                ),
            )
        )

        grid = ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    height=PLOT_HEIGHT,
                    content=ft.Column(
                        spacing=0,
                        controls=grid_controls,
                    ),
                ),
                ft.Container(height=BOTTOM_LABEL_AREA),
            ],
        )

        bars = ft.Container(
            height=CHART_HEIGHT,
            padding=ft.padding.only(left=10, right=14),
            content=ft.Row(
                expand=True,
                spacing=30,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    build_bar_pair(label, v1, v2)
                    for label, v1, v2 in chart_data
                ],
            ),
        )

        return ft.Container(
            expand=True,
            height=CHART_HEIGHT,
            content=ft.Stack(
                controls=[
                    grid,
                    bars,
                ],
            ),
        )

    # ☑️ 범례
    def build_legend():
        return ft.Row(
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=10,
                            height=10,
                            bgcolor=BAR_PRIMARY,
                            border_radius=2,
                        ),
                        ft.Text(
                            value=legend_primary,
                            size=12,
                            color=TEXT_SECONDARY,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=6,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=10,
                            height=10,
                            bgcolor=BAR_SECONDARY,
                            border_radius=2,
                        ),
                        ft.Text(
                            value=legend_secondary,
                            size=12,
                            color=TEXT_SECONDARY,
                        ),
                    ],
                ),
                ft.Text(
                    value=unit_text,
                    size=12,
                    color=TEXT_SECONDARY,
                ),
            ],
        )

    return ft.Container(
        height=440,
        bgcolor=CARD_BG,
        border_radius=20,
        border=ft.border.all(1, "#E0E1E2"),
        padding=ft.padding.only(left=24, right=24, top=22, bottom=20),
        content=ft.Column(
            expand=True,
            spacing=18,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            title,
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        build_legend(),
                    ],
                ),
                ft.Row(
                    expand=True,
                    spacing=0,
                    controls=[
                        build_y_axis(),
                        build_chart_area(),
                    ],
                ),
            ],
        ),
    )


# =========================================================
# ☑️ 재고 현황 전용 차트
# =========================================================
def build_stock_twin_chart():
    return build_twin_chart(
        title="입출고 현황",
        legend_primary="입고",
        legend_secondary="출고",
        unit_text="단위: 천원",
    )


# =========================================================
# ☑️ 생산관리 전용 차트
# =========================================================
def build_production_twin_chart():
    return build_twin_chart(
        title="생산 실적",
        legend_primary="생산",
        legend_secondary="불량",
        unit_text="단위: 천원",
    )