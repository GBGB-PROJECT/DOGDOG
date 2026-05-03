import datetime
import calendar
import flet as ft
from api_client import ApiClient
class LogController:
    """
    [Controller] LogController
    역할: 대시보드 로그 뷰(log_view)의 상태 관리 및 비즈니스 로직을 처리합니다.
    - 실제 서버 API와 연동하여 최근 7일간의 요일별 통계 데이터를 제공합니다.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        today = datetime.date.today()

        # 1. [DEBUG] 현재 세션에 저장된 모든 키 출력
        print(f"[DEBUG] 현재 세션 스토어 키 목록: {self.page.session.store.get_keys()}")

        # 2. [핵심] pet_id 다중 키 검색 및 안전 할당
        # 유저가 강아지를 선택할 때 사용했을 수 있는 다양한 키를 순차적으로 확인합니다.
        candidate_keys = ["current_pet_id", "selected_pet_id", "dog_id", "pet_id"]
        extracted_id = None
        for key in candidate_keys:
            extracted_id = page.session.store.get(key)
            if extracted_id:
                print(f"[DEBUG] 세션 매핑 성공: 키('{key}')로부터 ID({extracted_id})를 가져왔습니다.")
                break
        
        # 찾지 못한 경우 기본값 1 할당
        self.pet_id = extracted_id or 1
        print(f"[DEBUG] 최종 매핑된 Pet ID: {self.pet_id}")

        self.api = ApiClient(page)
        # 상태 변수
        self.current_year = today.year
        self.current_month = today.month
        self.selected_date = today
        self.selected_metric = "급여량"
        #self.summary_text = "일 평균 000kcal   |   목표 000kcal   |   달성 0회"
        
        # 실제 서버 데이터가 저장될 맵 (초기값은 빈 리스트)
        self.chart_data_map = {
            "급여량": [],
            "음수량": [],
            "몸무게": [],
        }
        
        # View 컴포넌트 참조 및 빌더
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
        """초기 화면 렌더링 및 비동기 데이터 로드 시작"""
        self.refresh_calendar()
        self.refresh_metric_selector()
        self.refresh_banner()
        # [해결] 초기 로딩 시 서버에서 차트 데이터 가져오기
        self.page.run_task(self.fetch_chart_data)

    async def fetch_chart_data(self):
        """
        [핵심] API 연동 및 데이터 가공 로직
        - GET /api/v1/logs/{pet_id} 호출
        - 최근 7일간의 데이터를 요일별로 합산
        """
        print(f"[LogController] 📡 차트 데이터 연동 시작 (Pet ID: {self.pet_id})")
        
        # 1. 최근 7일간의 날짜 리스트 생성 (YYYY-MM-DD)
        now = datetime.datetime.now()
        date_list = [(now - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
        
        # 2. 메트릭별 임시 합산 딕셔너리 초기화 (Zero Padding)
        metrics_sum = {
            "feeding": {d: 0.0 for d in date_list},
            "water": {d: 0.0 for d in date_list},
            "weight": {d: 0.0 for d in date_list}
        }

        # 3. API 호출 (기간 파라미터 추가로 과거 데이터 누락 방지)
        params = {
            "start_date": date_list[0],  # 6일 전 날짜
            "end_date": date_list[-1],   # 오늘 날짜
        }
        print(f"[LogController] 📡 API 요청 파라미터: {params}")
        
        response = await self.api.get(f"/logs/{self.pet_id}", params=params)
        
        if response and response.status_code == 200:
            res_json = response.json()  # JSON 변환!
            if res_json.get("status") == "success":
                logs = res_json.get("data", [])
            print(f"[LogController] 📥 수신된 로그 개수: {len(logs)}개")
            
            for log in logs:
                ts = log.get("timestamp", "")
                if not ts: continue
                
                # 날짜 추출 (YYYY-MM-DD)
                log_date = ts.split("T")[0]
                
                # 차트 범위 내의 데이터인지 확인
                if log_date in date_list:
                    cat = log.get("category")
                    domain = log.get("domain")
                    amount = float(log.get("amount", 0))
                    
                    # [매핑 로직] 급여량/음수량/몸무게 분류 합산
                    if cat == "feeding":
                        metrics_sum["feeding"][log_date] += amount
                    elif cat == "water":
                        metrics_sum["water"][log_date] += amount
                    elif cat == "weight":
                        # 몸무게는 합산이 아닌 가장 최근 기록으로 갱신
                        metrics_sum["weight"][log_date] = amount

        # 4. 요일 이름 매핑 및 chart_data_map 업데이트
        weekdays_kr = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
        
        def build_result(metric_key):
            result = []
            for d in date_list:
                dt = datetime.datetime.strptime(d, "%Y-%m-%d")
                day_name = weekdays_kr[dt.weekday()]
                val = metrics_sum[metric_key][d]
                result.append((day_name, val))
            return result

        self.chart_data_map["급여량"] = build_result("feeding")
        self.chart_data_map["음수량"] = build_result("water")
        self.chart_data_map["몸무게"] = build_result("weight")

        print(f"[LogController] ✅ 데이터 가공 완료")
        
        # 5. UI 갱신
        self.refresh_chart()
        self.page.update()

    def format_value(self, val):
        """[포맷팅] 정수형 변환 및 천 단위 콤마 적용"""
        try:
            return f"{int(float(val)):,}"
        except (ValueError, TypeError):
            return "0"

    def refresh_chart(self):
        """차트 컨테이너 새로고침"""
        if self.chart_container and self.line_chart_builder:
            self.chart_container.content = self.line_chart_builder()

    def change_metric(self, metric):
        """메트릭 변경 시 실시간으로 데이터를 다시 가져옵니다."""
        print(f"[LogController] 🔄 메트릭 변경: {metric}")
        self.selected_metric = metric
        self.refresh_metric_selector()
        # [해결] 비동기로 데이터 새로고침
        self.page.run_task(self.fetch_chart_data)
        self.page.update()

    # --- 기존 달력 및 배너 관련 로직 ---

    def open_weekly_banner(self, e):
        print("[LogController] 주간 배너 클릭 - 세션 초기화 및 이동")
        self.page.session.store.set("select_log_date", None)
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
                spacing=0, alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[self.day_cell_builder(day) for day in week],
            ) for week in month_days
        ]
        self.calendar_container.content = ft.Container(
            bgcolor="#ffffff", border_radius=12,
            padding=ft.padding.only(left=14, right=14, top=18, bottom=18),
            content=ft.Column(
                tight=True, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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
            self.current_month = 12; self.current_year -= 1
        else: self.current_month -= 1
        self.refresh_calendar(); self.page.update()

    def next_month(self, e):
        if self.current_month == 12:
            self.current_month = 1; self.current_year += 1
        else: self.current_month += 1
        self.refresh_calendar(); self.page.update()

    def handle_day_click(self, day):
        tapped_date = datetime.date(self.current_year, self.current_month, day)
        self.selected_date = tapped_date
        self.page.session.store.set("select_log_week", None)
        self.page.session.store.set("select_log_date", tapped_date.strftime("%Y.%m.%d"))
        self.refresh_calendar()
        self.page.go("/history")

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

    def refresh_banner(self):
        if self.detail_banner_area and self.banner_builder:
            self.detail_banner_area.content = self.banner_builder()
