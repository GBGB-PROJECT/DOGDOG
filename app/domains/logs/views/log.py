import asyncio
import calendar
import datetime

import flet as ft
import flet_charts as fch

import components as dogdog
from components.common.jun_layout_tokens import (
    # CONTENT_WIDTH,
    SECTION_GAP,
    CALENDAR_RADIUS,
    FILTER_BOX_RADIUS,
    OUTER_PAGE_PADDING,
    STAT_CARD_RADIUS,
    STAT_HEADER_RADIUS,
    SMALL_GAP,
    LARGE_GAP,
)
from components.common.jun_colors import (
    TOP_VANILLA,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    TEXT_TERTIARY,
    SURFACE_WHITE,
    CARD_BG,
    BORDER_DARK,
    FILTER_BORDER,
    CHART_GRID,
    CHART_LINE,
)


# ============================================================
# ✅ 고정값 상수
# ============================================================
CALENDAR_CELL_WIDTH = 36
# CHART_WIDTH = 290
CHART_HEIGHT = 240
CHART_MAX_Y = 8

WEEKDAY_NAMES = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
now = datetime.datetime.now()
DETAIL_BANNER_TEXT = f"{(now - datetime.timedelta(days=6)).strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
SUMMARY_TEXT = "일 평균 000kcal   |   목표 000kcal   |   달성 0회"

CARD_BORDER_COLOR = BORDER_DARK
CARD_BG_COLOR = CARD_BG
CHART_LINE_COLOR = CHART_LINE
CHART_GRID_COLOR = CHART_GRID
FILTER_BORDER_COLOR = FILTER_BORDER


def micro_box(text):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=SMALL_GAP, vertical=4),
        bgcolor=ft.Colors.GREY_200,
        border_radius=6,
        content=dogdog.Txt(
            text,
            size=10,
            color=TEXT_PRIMARY,
            weight=ft.FontWeight.W_500,
        ),
    )


def log_view(page: ft.Page):
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.bgcolor = SURFACE_WHITE
    page.appbar = None

    today = datetime.date.today()

    current_year = today.year
    current_month = today.month
    selected_date = today

    selected_banner = {"index": None}
    selected_metric = "급여량"

    calendar_container = ft.Container()
    detail_banner_area = ft.Container()
    chart_container = ft.Container(padding=20)
    metric_selector_container = ft.Container()

    chart_data_map = {
        "급여량": [
            ("월요일", 2.8),
            ("화요일", 3.0),
            ("수요일", 3.4),
            ("목요일", 3.1),
            ("금요일", 3.6),
            ("토요일", 3.8),
            ("일요일", 3.3),
        ],
        "음수량": [],
        "몸무게": [
            ("월요일", 2.2),
            ("화요일", 2.3),
            ("수요일", 4.2),
            ("목요일", 2.0),
            ("금요일", 5.0),
            ("토요일", 6.2),
            ("일요일", 3.9),
        ],
    }

    # ============================================================
    # ✅ 달력 관련 함수
    # ============================================================
    def month_title(year, month):
        return datetime.date(year, month, 1).strftime("%B %Y")

    def select_day(day):
        nonlocal selected_date
        selected_date = datetime.date(current_year, current_month, day)
        refresh_calendar()
        page.update()

    def handle_day_click(day):
        tapped_date = datetime.date(current_year, current_month, day).strftime(
            "%Y.%m.%d"
        )
        page.session.store.set("select_log_date", tapped_date)
        page.go("/history")
        select_day(day)

    def prev_month(e):
        nonlocal current_year, current_month

        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1

        refresh_calendar()
        page.update()

    def next_month(e):
        nonlocal current_year, current_month

        if current_month == 12:
            current_month = 1
            current_year += 1
        else:
            current_month += 1

        refresh_calendar()
        page.update()

    def day_cell(day):
        if day == 0:
            return ft.Container(
                width=CALENDAR_CELL_WIDTH,
                height=CALENDAR_CELL_WIDTH,
            )

        is_selected = (
            selected_date.year == current_year
            and selected_date.month == current_month
            and selected_date.day == day
        )

        return ft.Container(
            width=CALENDAR_CELL_WIDTH,
            height=CALENDAR_CELL_WIDTH,
            alignment=ft.Alignment(0, 0),
            on_click=lambda e, d=day: handle_day_click(d),
            content=ft.Container(
                width=28,
                height=28,
                border_radius=14,
                bgcolor=TOP_VANILLA if is_selected else None,
                alignment=ft.Alignment(0, 0),
                content=dogdog.Txt(
                    str(day),
                    size=14,
                    color=TEXT_PRIMARY,
                    weight=ft.FontWeight.W_500,
                ),
            ),
        )

    def weekday_row(calendar_width):
        return ft.Row(
            width=calendar_width,
            spacing=0,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    width=CALENDAR_CELL_WIDTH,
                    alignment=ft.Alignment(0, 0),
                    content=dogdog.Txt(
                        name,
                        size=10,
                        color=TEXT_MUTED,
                        weight=ft.FontWeight.W_500,
                    ),
                )
                for name in WEEKDAY_NAMES
            ],
        )

    def calendar_header(calendar_width):
        chevron_area_width = 72  # 👉 오른쪽 화살표 2개가 차지할 공간 확보

        return ft.Container(
            width=calendar_width,
            height=32,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(-1, 0),  # 👉 제목을 좌측 정렬
                        padding=ft.padding.only(
                            left=4, right=SMALL_GAP
                        ),  # 👉 살짝 왼쪽 붙이고 오른쪽도 조금 띄움
                        content=dogdog.Txt(
                            month_title(current_year, current_month),
                            size=17,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_PRIMARY,
                            text_align=ft.TextAlign.LEFT,  # 👉 텍스트 자체도 왼쪽 정렬
                        ),
                    ),
                    ft.Container(
                        width=chevron_area_width,  # 👉 제목이 이 영역까지 침범하지 못하게 고정
                        alignment=ft.Alignment(1, 0),
                        content=ft.Row(
                            spacing=0,
                            tight=True,
                            alignment=ft.MainAxisAlignment.END,
                            controls=[
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_LEFT,
                                    icon_size=18,
                                    icon_color=TEXT_TERTIARY,
                                    style=ft.ButtonStyle(padding=4),
                                    on_click=prev_month,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT,
                                    icon_size=18,
                                    icon_color=TEXT_TERTIARY,
                                    style=ft.ButtonStyle(padding=4),
                                    on_click=next_month,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    def refresh_calendar():
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(current_year, current_month)
        calendar_width = float("inf") * 7

        week_rows = [
            ft.Row(
                width=calendar_width,
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[day_cell(day) for day in week],
            )
            for week in month_days
        ]

        calendar_container.content = ft.Container(
            # width=CONTENT_WIDTH,
            bgcolor=SURFACE_WHITE,
            border_radius=CALENDAR_RADIUS,
            padding=ft.padding.only(left=14, right=14, top=18, bottom=18),
            content=ft.Column(
                tight=True,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    calendar_header(calendar_width),
                    weekday_row(calendar_width),
                    ft.Column(
                        tight=True,
                        spacing=SMALL_GAP,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=week_rows,  # type: ignore
                    ),
                ],
            ),
        )

    # ============================================================
    # ✅ 배너 관련 함수
    # ============================================================
    def change_selected_banner(index):
        selected_banner["index"] = index
        detail_banner_area.content = build_detail_banner()
        page.update()

    async def open_weekly_banner(e):
        change_selected_banner(0)
        await asyncio.sleep(0.3)
        page.session.store.set("select_log_week", DETAIL_BANNER_TEXT)
        page.go("/history")
        # page.open_log_weekly()

    def build_detail_banner():
        return dogdog.banner(
            image_src="대추.jpg",
            text=DETAIL_BANNER_TEXT,
            selected=(selected_banner["index"] == 0),
            on_click=open_weekly_banner,
        )

    # ============================================================
    # ✅ 차트 관련 함수
    # ============================================================
    def get_current_chart_data():
        return chart_data_map[selected_metric]

    def refresh_chart():
        chart_container.content = build_line_chart()

    def refresh_metric_selector():
        metric_selector_container.content = ft.Row(
            spacing=10,
            controls=[
                build_metric_label("급여량"),
                build_metric_label("음수량"),
                build_metric_label("몸무게"),
            ],
        )

    def change_metric(metric):
        nonlocal selected_metric
        selected_metric = metric
        refresh_metric_selector()
        refresh_chart()
        page.update()

    def build_metric_label(text):
        is_selected = selected_metric == text

        return ft.Container(
            on_click=lambda e, metric=text: change_metric(metric),
            ink=True,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=4, vertical=4),
            content=dogdog.Txt(
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
                # width=CHART_WIDTH,
                height=CHART_HEIGHT,
                alignment=ft.Alignment(0, 0),
                content=dogdog.Txt(
                    "기록이 없습니다.",
                    color=TEXT_PRIMARY,
                    size=16,
                    weight=ft.FontWeight.W_500,
                ),
            )

        normal_points = []
        highlight_points = []
        bottom_labels = []

        for i, (day_text, value) in enumerate(chart_data):
            normal_points.append(fch.LineChartDataPoint(i, value))
            bottom_labels.append(
                fch.ChartAxisLabel(
                    value=i,
                    label=dogdog.Txt(
                        day_text,
                        size=13,
                        color=TEXT_TERTIARY,
                        weight=ft.FontWeight.W_500,
                    ),
                )
            )

        max_point = sorted(
            enumerate(chart_data),
            key=lambda item: item[1][1],
            reverse=True,
        )[:1]

        highlight_indexes = [idx for idx, _ in max_point]

        for i, (_, value) in enumerate(chart_data):
            if i in highlight_indexes:
                highlight_points.append(fch.LineChartDataPoint(i, value))

        case = fch.LineChart(
            data_series=[
                fch.LineChartData(
                    points=normal_points,
                    stroke_width=3,
                    color=CHART_LINE_COLOR,
                    curved=True,
                    rounded_stroke_cap=True,
                ),
                fch.LineChartData(
                    points=highlight_points,
                    stroke_width=0,
                    point=True,
                    color=TOP_VANILLA,
                ),
            ],
            min_x=0,
            max_x=len(chart_data) - 1,
            min_y=0,
            max_y=CHART_MAX_Y,
            # width=CHART_WIDTH,
            height=CHART_HEIGHT,
            interactive=True,
            border=ft.border.all(0, ft.Colors.TRANSPARENT),
            left_axis=fch.ChartAxis(
                labels=[],
                label_size=0,
            ),
            bottom_axis=fch.ChartAxis(
                labels=bottom_labels,
                label_spacing=1,
                label_size=36,
            ),
            horizontal_grid_lines=fch.ChartGridLines(
                interval=1.5,
                color=CHART_GRID_COLOR,
                width=1,
            ),
            vertical_grid_lines=fch.ChartGridLines(
                interval=1,
                color=ft.Colors.TRANSPARENT,
                width=0,
            ),
        )

        return case

    # ============================================================
    # ✅ 화면 섹션 함수
    # ============================================================
    def seven_days_title():
        return dogdog.Txt(
            "일주일 상세 기록",
            size=16,
            weight=ft.FontWeight.W_500,
            color=TEXT_PRIMARY,
        )

    def last_seven_days_box():
        return ft.Container(
            width=90,
            height=34,
            border=ft.border.all(1, FILTER_BORDER_COLOR),
            border_radius=FILTER_BOX_RADIUS,
            alignment=ft.Alignment(0, 0),
            content=dogdog.Txt(
                "Last 7 Days",
                size=11,
                color=TEXT_PRIMARY,
                weight=ft.FontWeight.W_500,
            ),
        )

    def dog_stat_card_section():
        return ft.Container(
            # width=CONTENT_WIDTH,
            bgcolor=CARD_BG_COLOR,
            border=ft.border.all(1, CARD_BORDER_COLOR),
            border_radius=STAT_CARD_RADIUS,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=48,
                        bgcolor=TOP_VANILLA,
                        border_radius=ft.border_radius.only(
                            top_left=STAT_HEADER_RADIUS,
                            top_right=STAT_HEADER_RADIUS,
                        ),
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        padding=ft.padding.only(left=14, right=14, top=14, bottom=10),
                        content=ft.Stack(
                            controls=[
                                ft.Container(
                                    alignment=ft.Alignment(0, -1),
                                    content=dogdog.Txt(
                                        "츄츄 기록 통계",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=TEXT_PRIMARY,
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.all(14),
                        content=ft.Column(
                            spacing=SECTION_GAP,
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        metric_selector_container,
                                        last_seven_days_box(),
                                    ],
                                ),
                                chart_container,
                            ],
                        ),
                    ),
                ],
            ),
        )

    def grey_summary_section():
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                micro_box(SUMMARY_TEXT),
            ],
        )

    # ============================================================
    # ✅ 초기 렌더링
    # ============================================================
    refresh_metric_selector()
    refresh_chart()
    refresh_calendar()
    detail_banner_area.content = build_detail_banner()

    main_content = [
        calendar_container,
        seven_days_title(),
        detail_banner_area,
        dog_stat_card_section(),
        grey_summary_section(),
    ]

    return main_content
