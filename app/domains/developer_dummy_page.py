# import flet as ft
# import components as dogdog

# def dummy_view(page: ft.Page):
#     message = dogdog.basic_text(
#         value="이용에 불편을 드려 죄송합니다.\n더 나은 서비스를 위해 열심히 준비하고 있습니다.", 
#         weight="bold", color=ft.Colors.GREY_600)
#     message.text_align = ft.TextAlign.CENTER
#     return ft.Container(
#         padding=ft.Padding.only(left=20, right=20, top=20),
#         bgcolor="#ffffff",
#         alignment=ft.Alignment.CENTER,
#         content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             controls=[
#                 ft.Image(src="developer_image.png", scale=0.8),
#                 message
#     ]))

import flet as ft
import components as dogdog

def dummy_view(page: ft.Page):
    # 1. 안내 메시지 설정
    message = dogdog.basic_text(
        value="이용에 불편을 드려 죄송합니다.\n더 나은 서비스를 위해 열심히 준비하고 있습니다.", 
        weight="bold", 
        color=ft.Colors.GREY_600
    )
    message.text_align = ft.TextAlign.CENTER
    
    # 2. 메인 컨텐츠 구성
    # 부모인 ScrollColumn 내에서 최대한의 높이를 확보하도록 설정합니다.
    return ft.Column(
        # ⚠️ 핵심: 컬럼이 부모 내에서 사용 가능한 모든 세로 공간을 차지하게 합니다.
        expand=True, 
        # 세로 방향 정중앙 정렬
        alignment=ft.MainAxisAlignment.CENTER,
        # 가로 방향 정중앙 정렬
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=30,
        controls=[
            ft.Image(
                src="developer_image.png", 
                width=200,   # 크기를 명시적으로 지정하면 더 안정적입니다.
                height=200,
                fit=ft.ImageFit.CONTAIN
            ),
            message,
            # 하단 탭바 등에 가려지지 않도록 약간의 여백(Padding) 역할을 하는 투명 컨테이너
            ft.Container(height=50) 
        ]
    )