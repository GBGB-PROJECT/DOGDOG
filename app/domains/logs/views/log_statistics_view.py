import flet as ft
import components as dogdog
from ..controller.log_statistics_controller import LogStatisticsController

class LogStatisticsView(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.controller = LogStatisticsController(page)
        # 상단 수치 텍스트
        self.tooltip_text = ft.Text("0", size=28, weight="bold", color="#E65100")
        self.unit_text = ft.Text("ml", size=16, color="#9E9E9E", weight="bold")
        # 차트 컨테이너
        self.chart_container = ft.Container(height=220, alignment=ft.alignment.center)

    async def did_mount_async(self):
        print("[DEBUG] 🖼️ View: 마운트 완료, 기본 데이터(water) 로드 시작")
        await self.refresh_data("water")

    async def refresh_data(self, category):
        """데이터 로드 후 UI를 강제로 갱신합니다."""
        print(f"[DEBUG] 🔄 View: '{category}' 카테고리로 새로고침 중...")
        await self.controller.fetch_weekly_data(category)
        
        # 단위 업데이트
        units = {"water": "ml", "feeding": "g", "walk": "분"}
        self.unit_text.value = units.get(category, "")
        
        # 상단 수치 초기화 (오늘 값)
        if self.controller.weekly_data:
            today_val = self.controller.weekly_data[6][1]
            self.tooltip_text.value = self.controller.format_value(today_val)
        
        # 차트 리렌더링
        self.update_chart_ui()

    def update_chart_ui(self):
        """Flet 공식 ft.LineChart로 마이그레이션된 UI 갱신 로직"""
        if not self.controller.weekly_data:
            return

        # 1. Y축 최대값 계산 및 방어 로직
        raw_values = [val for _, val in self.controller.weekly_data]
        actual_max = max(raw_values) if raw_values else 0
        max_y_limit = actual_max if actual_max > 10 else 100
        
        # 2. 공식 ft.LineChart 생성
        print(f"[DEBUG] ⚡ View: 공식 ft.LineChart 마이그레이션 (max_y: {max_y_limit})")
        
        self.chart_container.content = ft.Container(
            # [UI 요구사항] 부모 컨테이너 테마 주입 (안전 장치)
            theme=ft.Theme(
                color_scheme=ft.ColorScheme(
                    surface=ft.colors.BROWN_50,
                    on_surface=ft.colors.BROWN_900
                )
            ),
            content=ft.LineChart(
                data_series=[
                    ft.LineChartData(
                        data_points=self.controller.get_chart_points(),
                        curved=True,
                        stroke_width=5,
                        color="#FF9800",
                        show_points=True,
                    )
                ],
                min_y=0,
                max_y=max_y_limit,
                
                left_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(value=0, label=ft.Text("0", size=10, color="transparent")),
                        ft.ChartAxisLabel(value=max_y_limit, label=ft.Text(str(max_y_limit), size=10, color="transparent")),
                    ],
                    show_labels=False,
                ),
                
                # [공식 API] 툴팁 색상 및 스타일 직접 제어
                tooltip_bgcolor="#F5F5DC",
                tooltip_text_style=ft.TextStyle(
                    color="#424242", 
                    weight="bold"
                ),
                
                bottom_axis=ft.ChartAxis(
                    labels=self.controller.get_bottom_labels(),
                    label_size=32,
                ),
                interactive=True,
                expand=True,
                on_chart_event=self.handle_chart_event
            )
        )
        self.update()

    def handle_chart_event(self, e: ft.LineChartEvent):
        """공식 이벤트 핸들러: 포인트 클릭 시 상단 수치 업데이트"""
        # 포인트 클릭 시 상단 텍스트 실시간 반영
        if e.type == "click" and e.point_index is not None:
             val = self.controller.weekly_data[e.point_index][1]
             self.tooltip_text.value = self.controller.format_value(val)
             self.update()

    def build(self):
        return ft.Container(
            padding=24,
            bgcolor="#FFFFFF",
            border_radius=28,
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.with_opacity(0.1, "#000000")),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[self.tooltip_text, self.unit_text]
                    ),
                    ft.Text("주간 활동 통계", size=14, color="#9E9E9E", weight="bold"),
                    ft.Divider(height=25, color="transparent"),
                    self.chart_container,
                    ft.Divider(height=25, color="transparent"),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            self.tab_button("급여량", "feeding"),
                            self.tab_button("음수량", "water"),
                            self.tab_button("산책", "walk"),
                        ]
                    )
                ]
            )
        )

    def tab_button(self, text, category):
        is_selected = self.controller.current_category == category
        return ft.Container(
            content=ft.Text(text, size=13, weight="bold", color="#FFFFFF" if is_selected else "#757575"),
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            bgcolor="#FF9800" if is_selected else "#F5F5F5",
            border_radius=14,
            on_click=lambda _: self.refresh_data(category),
            animate=ft.animation.Animation(300, ft.AnimationCurve.DECELERATE)
        )
