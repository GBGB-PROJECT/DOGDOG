import datetime
import calendar
import flet as ft

class LogController:
    """
    [Controller] LogController
    역할: 대시보드 로그 뷰(log_view)의 상태 관리 및 비즈니스 로직을 처리합니다.
    - 달력 상태(년, 월, 선택일) 및 차트 메트릭 상태를 관리합니다.
    - View에서 전달받은 빌더 함수를 사용하여 UI를 부분 업데이트합니다.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        today = datetime.date.today()
        
        # 상태 변수
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.selected_metric = "급여량"
        self.summary_text = "일 평균 000kcal   |   목표 000kcal   |   달성 0회"
        
        # 하드코딩된 차트 데이터 (추후 API 연동 대상)
        self.chart_data_map = {
            "급여량": [
                ("월요일", 2.8), ("화요일", 3.0), ("수요일", 3.4), 
                ("목요일", 3.1), ("금요일", 3.6), ("토요일", 3.8), ("일요일", 3.3),
            ],
            "음수량": [],
            "몸무게": [
                ("월요일", 2.2), ("화요일", 2.3), ("수요일", 4.2), 
                ("목요일", 2.0), ("금요일", 5.0), ("토요일", 6.2), ("일요일", 3.9),
            ],
        }
        
        # View 컴포넌트 참조 및 빌더 (View에서 설정됨)
        self.calendar_container = None
        self.chart_container = None
        self.metric_selector_container = None
        self.detail_banner_area = None
        
        self.day_cell_builder = None
        self.calendar_header_builder = None
        self.line_chart_builder = None
        self.metric_label_builder = None
        self.banner_builder = None

    def init_view(self):
        """초기 화면 렌더링을 위한 데이터 설정 및 컴포넌트 빌드"""
        self.refresh_calendar()
        self.refresh_chart()
        self.refresh_metric_selector()
        self.refresh_banner()

    def refresh_banner(self):
        """배너 영역 새로고침"""
        if self.detail_banner_area and self.banner_builder:
            self.detail_banner_area.content = self.banner_builder()

    def open_weekly_banner(self, e):
        """배너 클릭 시 히스토리 화면으로 이동"""
        print("[LogController] 일주일 배너 클릭")
        now = datetime.datetime.now()
        date_range_str = f"{(now - datetime.timedelta(days=6)).strftime('%Y-%m-%d')} ~ {now.strftime('%Y-%m-%d')}"
        self.page.session.store.set("select_log_week", date_range_str)
        self.page.go("/history")

    def refresh_calendar(self):
        if not self.calendar_container or not self.day_cell_builder:
            return
            
        cal = calendar.Calendar(firstweekday=6)
        month_days = cal.monthdayscalendar(self.current_year, self.current_month)
        
        week_rows = [
            ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[self.day_cell_builder(day) for day in week],
            )
            for week in month_days
        ]
        
        self.calendar_container.content = ft.Container(
            bgcolor="#ffffff",
            border_radius=12,
            padding=ft.padding.only(left=14, right=14, top=18, bottom=18),
            content=ft.Column(
                tight=True, spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.calendar_header_builder(float("inf")),
                    self._weekday_row(),
                    ft.Column(tight=True, spacing=5, controls=week_rows),
                ],
            ),
        )

    def _weekday_row(self):
        names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
        return ft.Row(
            spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Container(
                    width=36, alignment=ft.Alignment(0, 0),
                    content=ft.Text(name, size=10, color="grey", weight="w500")
                ) for name in names
            ],
        )

    def prev_month(self, e):
        if self.current_month == 1:
            self.current_month = 12
            self.current_year -= 1
        else:
            self.current_month -= 1
        self.refresh_calendar()
        self.page.update()

    def next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1
            self.current_year += 1
        else:
            self.current_month += 1
        self.refresh_calendar()
        self.page.update()

    def handle_day_click(self, day):
        tapped_date = datetime.date(self.current_year, self.current_month, day)
        self.selected_date = tapped_date
        self.page.session.store.set("select_log_date", tapped_date.strftime("%Y.%m.%d"))
        self.refresh_calendar()
        self.page.go("/history")

    def change_metric(self, metric):
        self.selected_metric = metric
        self.refresh_metric_selector()
        self.refresh_chart()
        self.page.update()

    def refresh_chart(self):
        if self.chart_container and self.line_chart_builder:
            self.chart_container.content = self.line_chart_builder()

    def refresh_metric_selector(self):
        if self.metric_selector_container and self.metric_label_builder:
            self.metric_selector_container.content = ft.Row(
                spacing=10,
                controls=[
                    self.metric_label_builder("급여량"),
                    self.metric_label_builder("음수량"),
                    self.metric_label_builder("몸무게"),
                ],
            )
