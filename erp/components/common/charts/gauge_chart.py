import math
import flet as ft
import flet.canvas as cv


CARD_BG = "#F5F5F5"
TRACK_COLOR = "#D9DDE3"
VALUE_COLOR = "#0B4F8A"
TEXT_PRIMARY = "#2B2F36"
TEXT_SECONDARY = "#6B7280"


def gauge_chart(percent=40, label="목표 달성률", width=260, height=160):
    stroke_w = 16
    radius = 92
    cx = width / 2
    cy = 120

    start_angle = math.pi
    sweep_bg = math.pi
    sweep_value = math.pi * (percent / 100)

    return ft.Container(
        width=width,
        height=height,
        bgcolor=CARD_BG,
        border_radius=16,
        padding=12,
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
                                stroke_cap=ft.StrokeCap.ROUND,
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
                                stroke_cap=ft.StrokeCap.ROUND,
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    width=width,
                    height=height,
                    padding=ft.padding.only(top=44),
                    alignment=ft.Alignment(0, 0),
                    content=ft.Column(
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                        controls=[
                            ft.Text(
                                f"{percent}%",
                                size=28,
                                weight=ft.FontWeight.W_700,
                                color=TEXT_PRIMARY,
                            ),
                            ft.Text(
                                label,
                                size=13,
                                color=TEXT_SECONDARY,
                            ),
                        ],
                    ),
                ),
            ]
        ),
    )