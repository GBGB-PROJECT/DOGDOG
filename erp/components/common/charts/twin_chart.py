import math
import flet as ft

CARD_BG = "#FFFFFF"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
TEXT_TERTIARY = "#9CA3AF"

CHART_GRID_COLOR = "#E5E7EB"

BAR_PRIMARY = "#0B4F8A"
BAR_SECONDARY = "#AFAFAF"

# ☑️ 기본 최대값
CHART_MAX_Y = 100

# 🔥 생산관리 차트 고정 최대값
# - 현재는 생산관리 차트에서 직접 사용하지 않음
# - 다른 코드 참조 가능성 때문에 상수는 유지
PRODUCTION_FIXED_MAX_Y = 80000

# 🔥 재고현황 차트 고정 최대값
# - 입출고/재고 차트는 기존 기준 그대로 유지
STOCK_FIXED_MAX_Y = 80000

# ☑️ 전체 차트 높이/플롯 높이 분리
PLOT_HEIGHT = 300
BOTTOM_LABEL_AREA = 34
CHART_HEIGHT = PLOT_HEIGHT + BOTTOM_LABEL_AREA

# 🔥 Y축 구간 수
Y_AXIS_DIVISIONS = 4


# =========================================================
# 🔥 기존 공통 차트용 보기 좋은 축 최대값 계산
# =========================================================
def _nice_ceil(value):
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0

    if value <= 0:
        return CHART_MAX_Y

    exponent = math.floor(math.log10(value))
    base = 10 ** exponent
    fraction = value / base

    if fraction <= 1:
        nice_fraction = 1
    elif fraction <= 2:
        nice_fraction = 2
    elif fraction <= 5:
        nice_fraction = 5
    else:
        nice_fraction = 10

    return int(nice_fraction * base)


# =========================================================
# 🔥 생산관리 전용 축 최대값 계산
# - 281K가 500K까지 튀는 문제 방지
# - 50K 단위로만 올림
# 예: 281,000 -> 300,000
# =========================================================
def _ceil_by_unit(value, unit=50000):
    try:
        value = float(value or 0)
    except (TypeError, ValueError):
        value = 0

    if value <= 0:
        return CHART_MAX_Y

    unit = int(unit or 50000)

    if value <= CHART_MAX_Y:
        return CHART_MAX_Y

    return int(math.ceil(value / unit) * unit)


# =========================================================
# 🔥 차트 최대값 계산
# - fixed_max_y가 있으면 기존 고정축 사용
# - axis_step_unit이 있으면 생산관리 전용 축 계산
# - 둘 다 없으면 기존 방식 사용
# =========================================================
def _calc_chart_max_y(chart_data, fixed_max_y=None, axis_step_unit=None):
    max_value = 0

    for _, v1, v2 in chart_data:
        try:
            max_value = max(max_value, float(v1 or 0), float(v2 or 0))
        except (TypeError, ValueError):
            continue

    if fixed_max_y:
        fixed_max_y = int(fixed_max_y)

        if max_value <= fixed_max_y:
            return fixed_max_y

        # 🔥 재고/입출고 차트 기존 동작 유지
        return int(math.ceil(max_value / 20000) * 20000)

    if max_value <= CHART_MAX_Y:
        return CHART_MAX_Y

    # 🔥 생산관리에서만 사용
    if axis_step_unit:
        return _ceil_by_unit(max_value, axis_step_unit)

    return _nice_ceil(max_value)


# =========================================================
# 🔥 Y축 라벨 표시
# - 기존처럼 K 단위 유지
# - 300,000 -> 300K
# =========================================================
def _format_y_axis_value(value):
    try:
        value = int(round(float(value or 0)))
    except (TypeError, ValueError):
        value = 0

    k_value = value / 1000

    if k_value.is_integer():
        return f"{int(k_value):,}K"

    return f"{k_value:,.1f}K"


# =========================================================
# 🔥 Y축 라벨 생성
# =========================================================
def _build_y_axis_labels(max_y):
    step = max_y / Y_AXIS_DIVISIONS
    labels = []

    for index in range(Y_AXIS_DIVISIONS, 0, -1):
        value = step * index
        labels.append(_format_y_axis_value(value))

    return labels


# =========================================================
# ☑️ 공통 twin chart
# - 기본 동작은 기존 입출고/재고 차트 그대로 유지
# - 생산관리만 axis_step_unit 옵션으로 축만 조정
# =========================================================
def build_twin_chart(
    title="입출고 현황",
    legend_primary="입고",
    legend_secondary="출고",
    unit_text="단위: K",
    chart_data=None,
    fixed_max_y=None,

    # 🔥 생산관리 전용 옵션
    # - 기본값 None이라 입출고/재고 차트에 영향 없음
    axis_step_unit=None,
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

    # 🔥 DB 데이터가 tuple/list 섞여 들어와도 안전하게 처리
    chart_data = [
        (str(item[0]), item[1] or 0, item[2] or 0)
        for item in chart_data
    ]

    chart_max_y = _calc_chart_max_y(
        chart_data,
        fixed_max_y=fixed_max_y,
        axis_step_unit=axis_step_unit,
    )

    y_axis_labels = _build_y_axis_labels(chart_max_y)
    y_step = PLOT_HEIGHT / Y_AXIS_DIVISIONS

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
        try:
            safe_v1 = float(v1 or 0)
        except (TypeError, ValueError):
            safe_v1 = 0

        try:
            safe_v2 = float(v2 or 0)
        except (TypeError, ValueError):
            safe_v2 = 0

        h1 = max((safe_v1 / chart_max_y) * PLOT_HEIGHT, 4) if safe_v1 > 0 else 4
        h2 = max((safe_v2 / chart_max_y) * PLOT_HEIGHT, 4) if safe_v2 > 0 else 4

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

        for _ in range(Y_AXIS_DIVISIONS):
            grid_controls.append(
                ft.Container(
                    height=y_step,
                    border=ft.border.only(
                        top=ft.BorderSide(1, CHART_GRID_COLOR)
                    ),
                )
            )

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
# - 입출고내역 쪽은 기존 그대로
# - 80K / 60K / 40K / 20K 기준 유지
# =========================================================
def build_stock_twin_chart(chart_data=None):
    return build_twin_chart(
        title="입출고 현황",
        legend_primary="입고",
        legend_secondary="출고",
        unit_text="단위: K",
        chart_data=chart_data,
        fixed_max_y=STOCK_FIXED_MAX_Y,
    )


# =========================================================
# 🔥 생산관리 전용 차트
# - 입출고/재고 차트에는 영향 없음
# - 값 라벨 제거
# - Y축만 50K 단위로 정리해서 500K 튀는 문제 방지
# =========================================================
def build_production_twin_chart(chart_data=None):
    return build_twin_chart(
        title="생산 실적",
        legend_primary="생산",
        legend_secondary="불량",
        unit_text="단위: 천원",
        chart_data=chart_data,

        # 🔥 생산관리만 자동 축
        fixed_max_y=None,

        # 🔥 생산관리만 50,000 단위 축 정리
        # 예: 최대값 281,000 -> 300K 표시
        axis_step_unit=50000,
    )