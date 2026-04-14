import math
import flet as ft
import flet.canvas as cv


CARD_BG = "#FFFFFF"
TRACK_COLOR = "#D9DDE3"
VALUE_COLOR = "#0B4F8A"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"


def gauge_chart(percent=40, label="목표 달성률", width=260, height=180):  # 🟥 수정: 카드 높이를 늘려 게이지와 텍스트 배치 여유 확보
    stroke_w = 18  # 🟥 수정: 게이지 선 두께를 조금 더 두껍게 조정
    horizontal_padding = 26  # 🟥 수정: 좌우 여백 기준값 추가
    top_padding = 20  # 🟥 수정: 상단 여백 기준값 추가
    bottom_padding = 34  # 🟥 수정: 하단 여백 기준값 추가

    radius = min((width - horizontal_padding * 2) / 2, height - top_padding - bottom_padding)  # 🟥 수정: 카드 크기에 맞춰 반지름 자동 계산
    cx = width / 2
    cy = height - bottom_padding  # 🟥 수정: 반원 중심을 아래로 내려 카드 안에서 정렬 맞춤

    start_angle = math.pi
    sweep_bg = math.pi
    sweep_value = math.pi * (percent / 100)

    return ft.Container(
        width=width,
        height=height,
        bgcolor=CARD_BG,
        border_radius=16,
        padding=0,  # 🟥 수정: 내부 padding 제거해서 Canvas와 카드 기준점 어긋남 방지
        content=ft.Stack(
            controls=[
                cv.Canvas(
                    width=width,
                    height=height,
                    shapes=[
                        cv.Arc(
                            x=cx - radius,
                            y=cy - radius,
                            width=radius * 2,
                            height=radius * 2,
                            start_angle=start_angle,
                            sweep_angle=sweep_bg,
                            paint=ft.Paint(
                                style=ft.PaintingStyle.STROKE,
                                stroke_width=stroke_w,
                                color=TRACK_COLOR,
                                stroke_cap=ft.StrokeCap.BUTT,  # 🟥 핵심: 끝을 네모로
                            ),
                        ),
                        cv.Arc(
                            x=cx - radius,
                            y=cy - radius,
                            width=radius * 2,
                            height=radius * 2,
                            start_angle=start_angle,
                            sweep_angle=sweep_value,
                            paint=ft.Paint(
                                style=ft.PaintingStyle.STROKE,
                                stroke_width=stroke_w,
                                color=VALUE_COLOR,
                                stroke_cap=ft.StrokeCap.BUTT,  # 🟥 핵심: 끝을 네모로
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    width=width,
                    height=height,
                    padding=ft.padding.only(top=78),  # 🟥 수정: 텍스트를 반원 중앙 아래쪽으로 자연스럽게 이동
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.START,  # 🟥 수정: 텍스트 묶음을 위에서부터 쌓이게 변경
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=6,  # 🟥 수정: 퍼센트와 라벨 간격 소폭 증가
                        controls=[
                            ft.Text(
                                f"{percent}%",
                                size=26,  # 🟥 수정: 숫자 크기를 살짝 조정해 과하게 커 보이지 않도록 변경
                                weight=ft.FontWeight.W_700,
                                color=TEXT_PRIMARY,
                            ),
                            ft.Text(
                                label,
                                size=13,
                                color=TEXT_SECONDARY,
                            ),
                             # 🟥 추가: divider
                            ft.Container(
                                width=120,  # 🟥 수정: 320 → 카드 width에 맞게 줄여야 안 튀어나감
                                height=1,
                                bgcolor="#D1D5DB",
                                margin=ft.margin.only(top=6, bottom=2),  # 🟥 추가: 위아래 여백
                            ),

                            # 🟥 수정: 하단 텍스트 중앙 정렬 강화
                            ft.Container(
                                alignment=ft.Alignment(0,0),  # 🟥 추가: 완전 중앙 정렬
                                content=ft.Text(
                                    "누계 실적",
                                    size=10,
                                    color=TEXT_SECONDARY,
                                    text_align=ft.TextAlign.CENTER,  # 🟥 추가: 텍스트 자체도 중앙
                                ),
                            )
                        ],
                    ),
                ),
            ]
        ),
    )

