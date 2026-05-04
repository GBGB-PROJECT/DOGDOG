from components import common as com
import flet as ft

class DevPopup:
    def __init__(self, page: ft.Page):
        self.page = page
        self.dlg = ft.AlertDialog(
            modal=True,
            # 1. 제목 중앙 정렬
            title=ft.Container(
                content=ft.Text("현재 개발 중입니다!", size=24, weight=ft.FontWeight.BOLD),
                alignment=ft.Alignment.CENTER,
                padding=ft.padding.only(bottom=-20)  # 제목과 이미지 사이 간격을 위로 당김
            ),
            # 2. 이미지(크기 확대)와 안내 문구를 수직 중앙 정렬
            content=ft.Column(
                controls=[
                    ft.Image(
                        src="dogdog_underdevelopment.png",
                        width=300,
                        height=300,
                        fit="contain",
                    ),
                    ft.Container(height=5), # 이미지와 텍스트 사이 간격
                    ft.Text(
                        "이용에 불편을 드려 죄송합니다.\n더 나은 서비스를 위해 열심히 준비하고 있습니다.",
                        size=13,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10)
                ],
                tight=True, # 자식 요소들 크기에 맞춰 컨테이너 축소
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            # 3. 버튼 중앙 정렬 및 ERP 브랜드 색상 적용
            actions=[
            ft.ElevatedButton(
                content=ft.Text("닫기",color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD),
                bgcolor=com.MAIN_COLOR, # ERP 트레이드 색상 적용
                color=ft.Colors.WHITE,
                on_click=self.close_popup,
                width=250,
                height=55,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10)
                )
            )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            content_padding=ft.padding.only(top=10, bottom=20, left=20, right=20),
            inset_padding=ft.padding.all(20)
        )

    def show(self, e=None):
        self.page.show_dialog(self.dlg)

    def close_popup(self, e=None):
        self.page.pop_dialog()