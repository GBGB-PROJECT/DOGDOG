from components import common as cm
from erp.domain.controller.home.erp_home_controller import *
import flet as ft
import flet_charts as fch

CHART_HEIGHT = 300 
MAX_REVENUE_Y = 1_000_000_000  # 좌측 축 최대값: 10억
MAX_VOLUME_Y = 14000           # 우측 축 최대값: 1만 4천

def build_sales_linechart():
    selected_metric = {"value": "1개월"}
    page_ref = {"page": None, "mounted": False}

    chart_container = ft.Container(expand=True)
    metric_selector_container = ft.Container()

    def get_current_chart_data():
        try:
            # API 컨트롤러 호출
            raw_salechart_data =HomeViewMain.sale_chart(selected_metric["value"])

            if not raw_salechart_data:
                return [] 
            ## API를 튜플로 매핑 -> JSON(dict)
            mapped_data = [
                (
                    item.get("period", ""),
                    item.get("revenue",0),
                    item.get("volume",0)
                )
                for item in raw_salechart_data
            ]
            return mapped_data
        except Exception as e:
            print(f"차트 데이터 로드 실패: {e}")
            return []

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
                color=cm.TEXT_PRIMARY if is_selected else cm.TEXT_SECONDARY,
                weight=ft.FontWeight.W_600,
            ),
        )

    def build_combo_chart():  # ☑️ 추가: 막대 그래프 + 직선 그래프를 함께 보여주는 콤보 차트
        chart_data = get_current_chart_data()

        if not chart_data:
            return ft.Container(
                expand=True,
                height=CHART_HEIGHT,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "기록이 없습니다.",
                    color=cm.TEXT_PRIMARY,
                    size=16,
                    weight=ft.FontWeight.W_500,
                ),
            )

        # 현재 데이터 기준으로 동적 계산(최소 기본값 설정, 모두 0 대비)
        current_max_rev = max([val for _, val, _ in chart_data] + [0])
        current_max_vol = max([val for _, _, val in chart_data] + [0])

        top_y_rev = current_max_rev * 1.2 if current_max_rev > 0 else 100_000_000
        top_y_vol = current_max_vol * 1.2 if current_max_vol > 0 else 1_000

        line_points = []  # ☑️ 추가: 선 그래프 포인트
        bottom_labels = []  # ☑️ 추가: 하단 라벨
        bar_row_controls = []  # ☑️ 수정: Stack 정렬 대신 동일 간격 Row 슬롯 방식으로 변경

        empty_bottom_labels = [] # 차트의 하단 공간(36px)만 유지하기 위한 빈 라벨
        label_row_controls = []  # 실제 글씨를 띄울 텍스트 전용 슬롯 리스트

        x_step = 2  # ☑️ 추가: 기존 선 그래프와 동일한 X축 간격 유지
        max_bar_height = 240  # ☑️ 추가: 막대 최대 높이
        chart_bottom_space = 36  # ☑️ 추가: 하단 라벨 공간 확보
        axis_space = 46  # ☑️ 추가: left_axis label_size와 동일하게 맞춤

        # ☑️ 추가: 선 그래프의 시작/끝을 반 칸씩 안쪽으로 넣어서
        #          막대 Row 슬롯의 중심점과 정확히 일치시키기 위한 범위
        min_x = -(x_step / 2)
        max_x = ((len(chart_data) - 1) * x_step) + (x_step / 2)

        for i, (label_text, line_value, bar_value) in enumerate(chart_data):  # ☑️ 추가: 선값/막대값 분리
            x_value = i * x_step  # ☑️ 추가: X축 좌표 계산

            if line_value > 0:
                tooltip_str = f"[{label_text}]\n매출: {int(line_value) // 1000:,}천 원\n판매량: {int(bar_value):,} 개"
                line_points.append(
                    fch.LineChartDataPoint(
                        x=x_value, 
                        y=line_value, 
                        point=True,
                        tooltip=tooltip_str,  # 2. tooltip 속성에 포맷팅된 문자열 주입    
                    )
                )
            
            empty_bottom_labels.append(
                fch.ChartAxisLabel(value=x_value, label=ft.Text(""))
            )

            label_row_controls.append(
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 1),
                    content=ft.Text(label_text, size=12, color= cm.PIE_BLUE, weight=ft.FontWeight.W_500),
                )
            )

            bottom_labels.append(
                fch.ChartAxisLabel(
                    value=x_value,
                    label=ft.Text(
                        size=12,
                        color=cm.PIE_BLUE,
                        weight=ft.FontWeight.W_500,
                    ),
                )
            )

            # 판매량이 0이면 막대높이를 0으로, 혹은 비율로 계산함
            bar_height = (bar_value / top_y_vol) * max_bar_height if top_y_vol > 0 and bar_value > 0 else 0

            bar_row_controls.append(
                ft.Container(
                    expand=True,  # ☑️ 추가: 각 데이터 포인트마다 동일 슬롯 확보
                    alignment=ft.Alignment(0, 1),  # ☑️ 추가: 슬롯 중앙 하단 정렬
                    content=ft.Container(
                        width=18,  # ☑️ 추가: 막대 너비
                        height=bar_height,
                        border_radius=0,  # ☑️ 추가: 막대 모서리 둥글게
                        bgcolor=cm.BAR_COLOR,
                    ),
                )
            )

        bar_layer = ft.Container(  # ☑️ 수정: 선 그래프 포인트 간격과 동일한 슬롯 구조로 막대 배치
            expand=True,
            height=CHART_HEIGHT,
            padding=ft.padding.only(left=axis_space, right=axis_space, top=20, bottom=chart_bottom_space),
            content=ft.Row(
                expand=True,
                spacing=0,
                controls=bar_row_controls,
            ),
        )

        label_layer = ft.Container(
            expand=True,
            height=CHART_HEIGHT,
            padding=ft.padding.only(left=axis_space, right=axis_space, bottom=8),
            content=ft.Row(
                expand=True,
                spacing=0,
                controls=ft.Row(expand=True, spacing=0, controls=label_row_controls),
            )
        )
        # 동적 축 자동 생성
        def format_rev(val):
            # 값이 크면 억, 작으면 만단위로 나눠줌
            if val >= 100_000_000: return f"{val/100_000_000:g}억"
            elif val >= 10_000 : return f"{val/10_000:g}만"
            return f"{val:g}"

        def format_vol(val):
            if val >= 1000: return f"{val/1000:g}k"
            return f"{val:g}"
        
        left_axis_labels = []
        right_axis_labels = []

        # 4칸으로 나누기 위한 간격 계산
        for i in range(1, 5):
            rev_val = (top_y_rev / 4) * i
            vol_val = (top_y_vol / 4) * i
            
            left_axis_labels.append(fch.ChartAxisLabel(value=rev_val, label=ft.Text("")))
            # 우측 축(판매량)도 위치값은 매출(rev_val)에 맞추고 텍스트만 판매량을 보여줍니다.
            right_axis_labels.append(fch.ChartAxisLabel(value=rev_val, label=ft.Text("")))

        line_layer = fch.LineChart(  # ☑️ 추가: 기존 선 그래프 레이어
            expand=True,
            height=CHART_HEIGHT,
            min_x=min_x,  # ☑️ 수정: 좌우 반 칸 여백 추가
            max_x=max_x,  # ☑️ 수정: 좌우 반 칸 여백 추가
            min_y=0,
            max_y=top_y_rev,
            interactive=True,
            border=ft.border.all(0, ft.Colors.TRANSPARENT),
            left_axis=fch.ChartAxis(labels=left_axis_labels, label_size=axis_space),
            right_axis=fch.ChartAxis(labels=right_axis_labels, label_size=axis_space),
            bottom_axis=fch.ChartAxis(labels=bottom_labels, label_size=32),
            horizontal_grid_lines=fch.ChartGridLines(interval=top_y_rev/4, color=cm.CHART_GRID_COLOR, width=1),
            vertical_grid_lines=fch.ChartGridLines(interval=x_step, color=ft.Colors.TRANSPARENT, width=0),
            data_series=[
                fch.LineChartData(
                    points=line_points,
                    stroke_width=3,
                    color=cm.CHART_LINE_AND_TEXT_COLOR,
                    point=True,
                ),
            ],
        )

        return ft.Stack(  # ☑️ 추가: 막대 그래프 뒤 + 직선 그래프 앞
            expand=True,
            controls=[
                bar_layer,
                label_layer,
                line_layer,  
            ],
        )

    def refresh_metric_selector():
        metric_selector_container.content = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,  # 🟥 수정: 좌우 분리
            controls=[
                ft.Row(  # 🟥 추가: 왼쪽 → 필터 묶음
                    spacing=10,
                    controls=[
                        build_metric_label("1주일"),
                        build_metric_label("1개월"),
                        build_metric_label("1년"),
                    ],
                ),
                ft.IconButton(  # 🟥 추가: 오른쪽 → + 버튼
                    icon=ft.Icons.ADD,
                    icon_size=26,
                    icon_color=cm.TEXT_PRIMARY,
                ),
            ],
        )

    def refresh_chart():
        chart_container.content = build_combo_chart()  # ☑️ 수정: 직선 차트 대신 막대+직선 콤보 차트로 변경

    def show_chart_loading():
        chart_container.content = ft.Container(
            expand=True,
            height=CHART_HEIGHT,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "차트 데이터를 불러오는 중입니다.",
                color=cm.TEXT_SECONDARY,
                size=14,
                weight=ft.FontWeight.W_500,
            ),
        )

    def change_metric(metric: str, e: ft.ControlEvent):
        page = page_ref["page"]
        if page is None:
            return

        selected_metric["value"] = metric
        refresh_metric_selector()
        show_chart_loading()
        page.update()

        def worker():
            if not page_ref["mounted"]:
                return
            refresh_chart()
            if page_ref["mounted"]:
                page.update()

        page.run_thread(worker)

    refresh_metric_selector()
    show_chart_loading()

    class SalesLineChartCard(ft.Container):
        def did_mount(self):
            page = self.page
            page_ref["page"] = page
            page_ref["mounted"] = True

            def worker():
                if not page_ref["mounted"]:
                    return
                refresh_chart()
                if page_ref["mounted"]:
                    page.update()

            page.run_thread(worker)

        def will_unmount(self):
            page_ref["mounted"] = False
            page_ref["page"] = None

    return SalesLineChartCard(
        expand=True,
        height=380, # 🟥 수정: 좌측 게이지 2개와 균형을 맞추기 위해 전체 카드 높이를 상향
        bgcolor=cm.CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),
        padding=20,
        content=ft.Column(
            expand=True,
            spacing=16,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=12,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            controls=[
                                ft.Text("매출 추이", size=18, weight=ft.FontWeight.W_700, color=cm.TEXT_PRIMARY),
                                # 🟥 데이터 레이블 설명 추가 (좌측은 매출, 우측은 판매량 명시)
                                ft.Text("■ 판매량", size=12, color=cm.BAR_COLOR),
                                ft.Text("● 매출액", size=12, color=cm.CHART_LINE_AND_TEXT_COLOR)
                            ]
                        ),
                        metric_selector_container,
                    ],
                ),
                chart_container,
            ],
        ),
    )
