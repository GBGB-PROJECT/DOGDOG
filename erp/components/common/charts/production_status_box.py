import flet as ft
from components import common as cm

def _vertical_progress(value: float):
    ## ProgressBar는 0.0에서 1.0 사이 => 1.0 초과 시 1.0을 출력함
    display_value = min(value, 1.0)

    return ft.Container(
        width=28,
        height=150,
        alignment=ft.Alignment(0, 0),
        content=ft.RotatedBox(
            quarter_turns=3,
            content=ft.ProgressBar(
                width=140,
                value=value,
                bgcolor=cm.BORDER_LIGHT,
                color=cm.BAR_ACTIVE,
                border_radius=10,
                bar_height=10,
            ),
        ),
    )

def _mini_progress_panel(title: str, values: list[float], mom_text: str):
    # 증감률 수치에 따른 색상 분기 (음수면 빨간색 계열, 양수면 민트색 계열)
    is_negative = "-" in mom_text
    mom_bg_color = "#FEE2E2" if is_negative else "#99F6E4"  # 연빨강 vs 연민트
    mom_text_color = "#B91C1C" if is_negative else "#0D9488" # 진빨강 vs 진청록
    
    bars = [_vertical_progress(v) for v in values]  # ☑️ 

    y_labels = ft.Column(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        height=150,
        controls=[
            ft.Text("1.0", size=11, color=cm.TEXT_SECONDARY),
            ft.Text("0.5", size=11, color=cm.TEXT_SECONDARY),
            ft.Text("0", size=11, color=cm.TEXT_SECONDARY),
        ],
    )

    return ft.Container(
        expand=True,
        height=220,
        bgcolor="#F8F9FA",
        border_radius=14,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            title,
                            size=15,
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.Container(
                            height=30,
                            padding=ft.padding.symmetric(horizontal=10),
                            border_radius=8,
                            bgcolor=mom_bg_color,
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                mom_text,
                                size=12,
                                color=mom_text_color,
                                weight=ft.FontWeight.W_500,
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    spacing=10,
                    controls=[
                        y_labels,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            expand=True,
                            controls=bars,
                        ),
                    ],
                ),
            ],
        ),
    )

def build_production_status_box(data: dict):
# [수정] 컨트롤러가 이미 'data' 내부를 주므로 바로 접근합니다.
    production_rate = data.get("production_rate", [0]*6)
    defect_rate = data.get("defect_rate", [0]*6)
    base_date = data.get("base_date", "날짜 없음")
    prod_mom = data.get("production_mom", "0%")
    def_mom = data.get("defect_mom", "0%")

    return ft.Container(
        expand=True,
        bgcolor=cm.CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#EFF0F1"), # 새깔이 이곳?
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            f"입고현황 ({base_date})",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=cm.TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=26,
                            icon_color=cm.TEXT_PRIMARY,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    controls=[
                        _mini_progress_panel("목표 입고 달성", production_rate,prod_mom),
                        _mini_progress_panel("불량률", defect_rate,def_mom),
                    ],
                ),
            ],
        ),
    )