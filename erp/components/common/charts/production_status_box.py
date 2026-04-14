import flet as ft


CARD_BG = "#FFFFFF"
INNER_BG = "#FFFFFF"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"
BORDER_LIGHT = "#D9DDE3"
BAR_ACTIVE = "#0B4F8A"


def _vertical_progress(value: float):
    # value: 0.0 ~ 1.0
    return ft.Container(
        width=28,
        height=150,
        alignment=ft.Alignment(0, 0),
        content=ft.RotatedBox( 
            quarter_turns=3,
            content=ft.ProgressBar(
                width=140,
                value=value,
                bgcolor=BORDER_LIGHT,
                color=BAR_ACTIVE,
                border_radius=10,
                bar_height=10,
            ),
        ),
    )


def _mini_progress_panel(title: str, values: list[float]):
    bars = [_vertical_progress(v) for v in values[:8]]

    y_labels = ft.Column(  # 🟠 추가: Y축 라벨 (1k ~ 5k)
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        height=150,  # 🟠 progress bar 높이와 맞춤
        controls=[
            ft.Text("5k", size=11, color=TEXT_SECONDARY),
            ft.Text("4k", size=11, color=TEXT_SECONDARY),
            ft.Text("3k", size=11, color=TEXT_SECONDARY),
            ft.Text("2k", size=11, color=TEXT_SECONDARY),
            ft.Text("1k", size=11, color=TEXT_SECONDARY),
        ],
    )

    return ft.Container(
        expand=True,
        height=220,
        bgcolor=INNER_BG,  # ✅ 내부 상자 배경만 있고 테두리는 없음
        border_radius=14,
        padding=16,
        content=ft.Column(
            spacing=12,
            controls=[
                ft.Row(  # ☑️ 수정: 제목 Text 단독 -> 우측 배지 포함 Row
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            title,
                            size=15,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.Container(  # ☑️ 추가: 제목 극우측의 작은 상태 박스
                            height=30,
                            padding=ft.padding.symmetric(horizontal=10),
                            border_radius=8,
                            bgcolor="#99F6E4",  # ☑️ 밝은 청록색
                            alignment=ft.Alignment(0, 0),
                            content=ft.Text(
                                "+12%",
                                size=12,
                                color=TEXT_PRIMARY,
                                weight=ft.FontWeight.W_500,
                            ),
                        ),
                    ],
                ),

                ft.Row(  # 🟠 수정: bars만 있던 구조 → Y축 + bars 구조로 확장
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    spacing=10,
                    controls=[
                        y_labels,  # 🟠 추가: 왼쪽 Y축
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.END,
                            expand=True,  # 🟠 추가: bars 영역 확장
                            controls=bars,
                        ),
                    ],
                ),
            ],
        ),
    )


def build_production_status_box():
    left_values = [0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20]
    right_values = [0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20, 0.20]

    return ft.Container(
        expand=True,
        bgcolor=CARD_BG,
        border_radius=16,
        border=ft.border.all(1, "#E0E1E2"),  # 🟥 추가: 카드 전체 테두리
        padding=20,
        content=ft.Column(
            spacing=20,
            controls=[
                # 상단 제목줄
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            "생산현황 (2026/04/13)",
                            size=20,
                            weight=ft.FontWeight.W_700,
                            color=TEXT_PRIMARY,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            icon_size=26,
                            icon_color=TEXT_PRIMARY,
                        ),
                    ],
                ),

                # 내부 좌우 박스 2개
                ft.Row(
                    spacing=16,
                    controls=[
                        _mini_progress_panel("생산 달성률", left_values),
                        _mini_progress_panel("불량률", right_values),
                    ],
                ),
            ],
        ),
    )