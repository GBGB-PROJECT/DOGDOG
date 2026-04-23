import flet as ft
import components as dogdog
import datetime

def onboarding_top_bar(case=None):
    content = ft.Column(
        spacing=0,
        controls=[
            dogdog.basic_text(value="About your Dog", weight="Bold", size=30),
            dogdog.basic_text(value="반려동물의 기본 정보를 입력하세요", weight="Bold", size=15),
        ],
    )
    if case == 1: content = ft.Column(
        spacing=0,
        controls=[
            dogdog.basic_text(value="Welcome to 똑똑", weight="bold", size=30),
            ft.Container(height=12),
            dogdog.basic_text(
                value="똑똑🚪✊ 우리집 강아지가 마지막 한알을 먹기 전\n문앞에 사료가 도착합니다.", 
                weight="bold", size=14
            )
        ]
    )

    return ft.Container(height=120, padding=ft.Padding.only(top=40), content=content)