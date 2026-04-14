import flet as ft
import flet_charts as fch


CARD_BG = "#F5F5F5"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"

CHART_LINE_COLOR = "#0B4F8A"
CHART_POINT_COLOR = "#0EA5E9"
CHART_GRID_COLOR = "#E5E7EB"

CHART_HEIGHT = 240
CHART_MAX_Y = 80  # ☑️ 수정: 데이터 값(20~80)에 맞게 Y축 최대값을 80으로 변경


def build_sales_linechart():
    selected_metric = {"value": "1개월"}

    chart_data_map = {
        "1주일": [
            ("4/1", 20),
            ("4/2", 40),
            ("4/3", 20),
            ("4/4", 80),
            ("4/5", 50),
            ("4/6", 60),
            ("4/7", 20),
        ],
        "1개월": [
            ("1월", 20),
            ("2월", 40),
            ("3월", 20),
            ("4월", 80),
            ("5월", 50),
            ("6월", 70),
            ("7월", 20),
        ],
        "1년": [
            ("2021", 20),
            ("2023", 40),
            ("2024", 20),
            ("2025", 80),
            ("2026", 50),
        ],
    }

    chart_container = ft.Container(expand=True)
    metric_selector_container = ft.Container()

    def get_current_chart_data():
        return chart_data_map[selected_metric["value"]]

    def build_metric_label(text: str):
        is_selected = selected_metric["value"] == text

        return ft.Container(
            on_click=lambda e, metric=text: change_metric(metric, e),
            ink=True,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=6, vertical=4),
            content=ft.Text(
                f"• {text}",
                size=13,
                color=TEXT_PRIMARY if is_selected else TEXT_SECONDARY,
                weight=ft.FontWeight.W_600,
            ),
        )

    def build_line_chart():
        chart_data = get_current_chart_data()

        if not chart_data:
            return ft.Container(
                expand=True,
                height=CHART_HEIGHT,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "기록이 없습니다.",
                    color=TEXT_PRIMARY,
                    size=16,
                    weight=ft.FontWeight.W_500,
                ),
            )

        points = []  # ☑️ 수정: normal/highlight 제거 → 하나로 통합
        bottom_labels = []

        x_step = 2  # ☑️ 추가: X축 간격 확장 (연도 잘림 방지 핵심)

        for i, (label_text, value) in enumerate(chart_data):
            x_value = i * x_step  # ☑️ 수정: 간격 확장 적용

            points.append(
                fch.LineChartDataPoint(
                    x_value,
                    value,
                    point=True,  # ☑️ 추가: 모든 점 표시
                )
            )

            bottom_labels.append(
                fch.ChartAxisLabel(
                    value=x_value,  # ☑️ 수정: 라벨도 같은 좌표 사용
                    label=ft.Text(
                        label_text,
                        size=12,
                        color=TEXT_TERTIARY,
                        weight=ft.FontWeight.W_500,
                    ),
                )
            )

        return fch.LineChart(
            expand=True,
            height=CHART_HEIGHT,
            min_x=0,
            max_x=(len(chart_data) - 1) * x_step,  # ☑️ 수정: 확장된 X범위 반영
            min_y=0,
            max_y=CHART_MAX_Y,
            interactive=True,
            border=ft.border.all(0, ft.Colors.TRANSPARENT),

            left_axis=fch.ChartAxis(
                labels=[  # ☑️ 추가: 좌측 Y축 라벨
                    fch.ChartAxisLabel(
                        value=20,
                        label=ft.Text("20k", size=12, color=TEXT_TERTIARY),
                    ),
                    fch.ChartAxisLabel(
                        value=40,
                        label=ft.Text("40k", size=12, color=TEXT_TERTIARY),
                    ),
                    fch.ChartAxisLabel(
                        value=60,
                        label=ft.Text("60k", size=12, color=TEXT_TERTIARY),
                    ),
                    fch.ChartAxisLabel(
                        value=80,
                        label=ft.Text("80k", size=12, color=TEXT_TERTIARY),
                    ),
                ],
                label_size=42,  # ☑️ 수정: 좌측 공간 확보
            ),

            bottom_axis=fch.ChartAxis(
                labels=bottom_labels,
                label_size=36,
            ),

            horizontal_grid_lines=fch.ChartGridLines(
                interval=20,  # ☑️ 수정: 20단위 맞춤
                color=CHART_GRID_COLOR,
                width=1,
            ),

            vertical_grid_lines=fch.ChartGridLines(
                interval=x_step,  # ☑️ 수정: X 간격과 동기화
                color=ft.Colors.TRANSPARENT,
                width=0,
            ),

            data_series=[
                fch.LineChartData(
                    points=points,  # ☑️ 수정: 하나만 사용
                    stroke_width=3,
                    color=CHART_LINE_COLOR,
                    curved=False,  # ☑️ 수정: 직선 차트
                    rounded_stroke_cap=True,
                    point=True,  # ☑️ 추가: 전체 점 표시
                ),
            ],
        )

    def refresh_metric_selector():
        metric_selector_container.content = ft.Row(
            spacing=10,
            controls=[
                build_metric_label("1주일"),
                build_metric_label("1개월"),
                build_metric_label("1년"),
            ],
        )

    def refresh_chart():
        chart_container.content = build_line_chart()

    def change_metric(metric: str, e: ft.ControlEvent):
        selected_metric["value"] = metric
        refresh_metric_selector()
        refresh_chart()
        e.page.update()

    refresh_metric_selector()
    refresh_chart()

    return ft.Container(
        expand=True,
        height=340,
        bgcolor=CARD_BG,
        border_radius=16,
        padding=20,
        content=ft.Column(
            expand=True,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "매출 추이",
                            size=18,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        metric_selector_container,
                    ],
                ),
                chart_container,
            ],
        ),
    )