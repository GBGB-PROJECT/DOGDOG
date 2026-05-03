import datetime
import flet as ft
import flet_charts as fch
import components as dogdog
from components.common.jun_layout_tokens import (
    SECTION_GAP,
    CALENDAR_RADIUS,
    FILTER_BOX_RADIUS,
    STAT_CARD_RADIUS,
    STAT_HEADER_RADIUS,
    SMALL_GAP,
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
CHART_HEIGHT = 240
CHART_MAX_Y = 8

WEEKDAY_NAMES = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
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


def log_view(page: ft.Page, controller):
    """
    [View] Log View
    UI 렌더링만 담당하며, 모든 상태 관리와 로직은 controller로 위임합니다.
    """
    page.padding = 0
    page.spacing = 0
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.bgcolor = SURFACE_WHITE
    page.appbar = None

    # UI 컴포넌트 참조 저장 (Controller에서 업데이트 시 필요할 수 있음)
    controller.calendar_container = ft.Container()
    controller.detail_banner_area = ft.Container()
    controller.chart_container = ft.Container(padding=20)
    controller.metric_selector_container = ft.Container()

    # ============================================================
    # ✅ 달력 빌더
    # ============================================================
    def day_cell(day):
        if day == 0:
            return ft.Container(width=CALENDAR_CELL_WIDTH, height=CALENDAR_CELL_WIDTH)

        is_selected = (
            controller.selected_date.year == controller.current_year
            and controller.selected_date.month == controller.current_month
            and controller.selected_date.day == day
        )

        # [해결] 비동기 클로저 핸들러 생성 (클릭 시점의 일자 d를 고정)
        def make_day_click_handler(d):
            async def on_click(e):
                # 1. 컨트롤러의 날짜 클릭 로직 실행 (비동기 대응)
                import asyncio
                if asyncio.iscoroutinefunction(controller.handle_day_click):
                    await controller.handle_day_click(d)
                else:
                    controller.handle_day_click(d)
                
                # 2. 세션에 저장할 날짜 포맷팅 (YYYY.MM.DD)
                date_str = f"{controller.current_year}.{controller.current_month:02d}.{d:02d}"
                
                # 3. 세션 스토리지 저장 및 라우팅 이동
                page.session.store.set("select_log_date", date_str)
                page.go("/history") # 상세 기록 페이지로 이동
            
            return on_click

        return ft.Container(
            width=CALENDAR_CELL_WIDTH,
            height=CALENDAR_CELL_WIDTH,
            alignment=ft.Alignment(0, 0),
            # [해결] 기존 lambda를 지우고 안전한 비동기 핸들러로 교체
            on_click=make_day_click_handler(day),
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

    def calendar_header(calendar_width):
        chevron_area_width = 72
        month_year_text = datetime.date(
            controller.current_year, controller.current_month, 1
        ).strftime("%B %Y")

        return ft.Container(
            width=calendar_width,
            height=32,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        expand=True,
                        alignment=ft.Alignment(-1, 0),
                        padding=ft.padding.only(left=4, right=SMALL_GAP),
                        content=dogdog.Txt(
                            month_year_text,
                            size=17,
                            weight=ft.FontWeight.W_500,
                            color=TEXT_PRIMARY,
                        ),
                    ),
                    ft.Container(
                        width=chevron_area_width,
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
                                    on_click=controller.prev_month,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHEVRON_RIGHT,
                                    icon_size=18,
                                    icon_color=TEXT_TERTIARY,
                                    on_click=controller.next_month,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
        )

    # ============================================================
    # ✅ 차트 빌더
    # ============================================================
    def build_line_chart():
        chart_data = controller.chart_data_map.get(controller.selected_metric, [])

        if not chart_data:
            return ft.Container(
                height=CHART_HEIGHT,
                alignment=ft.Alignment(0, 0),
                content=dogdog.Txt(
                    "기록이 없습니다.",
                    color=TEXT_PRIMARY,
                    size=16,
                    weight=ft.FontWeight.W_500,
                ),
            )

        normal_points = [
            fch.LineChartDataPoint(i, v) for i, (_, v) in enumerate(chart_data)
        ]
        bottom_labels = [
            fch.ChartAxisLabel(
                value=i,
                label=dogdog.Txt(
                    day, size=13, color=TEXT_TERTIARY, weight=ft.FontWeight.W_500
                ),
            )
            for i, (day, _) in enumerate(chart_data)
        ]

        # 최대값 강조 (Highlight)
        max_val = max([v for _, v in chart_data]) if chart_data else 0
        highlight_points = [
            fch.LineChartDataPoint(i, v)
            for i, (_, v) in enumerate(chart_data)
            if v == max_val
        ]

        return fch.LineChart(
            data_series=[
                fch.LineChartData(
                    points=normal_points,
                    stroke_width=3,
                    color=CHART_LINE_COLOR,
                    curved=True,
                ),
                fch.LineChartData(
                    points=highlight_points,
                    stroke_width=0,
                    point=True,
                    color=TOP_VANILLA,
                ),
            ],
            min_y=0,
            max_y=CHART_MAX_Y,
            height=CHART_HEIGHT,
            interactive=True,
            bottom_axis=fch.ChartAxis(
                labels=bottom_labels, label_spacing=1, label_size=36
            ),
            horizontal_grid_lines=fch.ChartGridLines(
                interval=1.5, color=CHART_GRID_COLOR, width=1
            ),
        )

    # ============================================================
    # ✅ 화면 섹션 정의
    # ============================================================
    def build_metric_label(text):
        is_selected = controller.selected_metric == text
        return ft.Container(
            on_click=lambda e, m=text: controller.change_metric(m),
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

    def dog_stat_card_section():
        return ft.Container(
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
                        padding=ft.padding.all(14),
                        content=ft.Container(
                            alignment=ft.Alignment(0, 0),  # 정렬 위치
                            content=dogdog.Txt(
                                "우리 아이 기록 통계",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=TEXT_PRIMARY,
                            ),
                        ),
                    ),
                    ft.Container(
                        padding=ft.padding.all(14),
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        controller.metric_selector_container,
                                        ft.Container(
                                            border=ft.border.all(
                                                1, FILTER_BORDER_COLOR
                                            ),
                                            border_radius=FILTER_BOX_RADIUS,
                                            padding=ft.padding.symmetric(
                                                horizontal=10, vertical=5
                                            ),
                                            content=dogdog.Txt(
                                                "Last 7 Days",
                                                size=11,
                                                color=TEXT_PRIMARY,
                                            ),
                                        ),
                                    ],
                                ),
                                controller.chart_container,
                            ],
                        ),
                    ),
                ],
            ),
        )

    # ============================================================
    # ✅ 배너 빌더
    # ============================================================
    def build_detail_banner():
        now = datetime.datetime.now()
        date_range_str = f"{(now - datetime.timedelta(days=6)).strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        
        return dogdog.banner(
            image_src="대추.jpg",
            text=date_range_str,
            selected=False,
            on_click=controller.open_weekly_banner,
        )

    # Controller에 UI 빌더 함수 전달 (Controller에서 UI를 새로고침할 때 사용)
    controller.day_cell_builder = day_cell
    controller.calendar_header_builder = calendar_header
    controller.line_chart_builder = build_line_chart
    controller.metric_label_builder = build_metric_label
    controller.banner_builder = build_detail_banner

    # 초기 데이터 로드 및 렌더링 호출
    controller.init_view()

    return [
        controller.calendar_container,
        dogdog.Txt(
            "일주일 상세 기록", size=16, weight="bold", color=TEXT_PRIMARY
        ),
        controller.detail_banner_area,
        dog_stat_card_section(),
        ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[micro_box(controller.summary_text)],
        ),
    ]
