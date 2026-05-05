from components import common as com
import flet as ft

class DevPopup:
    def __init__(self, page: ft.Page):
        self.page = page
        self.dlg = ft.AlertDialog(
            modal=True,
            title=ft.Container(
                content=ft.Text("현재 개발 중 입니다!", size=24, weight=ft.FontWeight.BOLD),
                alignment=ft.Alignment.CENTER,
                padding=ft.padding.only(bottom=15)  # 제목과 이미지 사이 간격 좁힘
            ),
            content=ft.Column(
                controls=[
                    ft.Image(
                        src="dogdog_underdevelopment.png",
                        width=250,  # 이미지 크기 강조
                        height=250,
                        fit="contain",
                    ),
                    ft.Container(height=5),  # 이미지와 텍스트 사이 넓은 간격 (1번 스타일)
                    ft.Text(
                        "이용에 불편을 드려 죄송합니다.\n더 나은 서비스를 위해 열심히 준비하고 있습니다.",
                        size=14,
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                        #line_height=1.5  # 가독성을 위한 줄간격
                    ),
                    ft.Container(height=10),
                ],
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            # 3. 버튼 중앙 정렬 및 ERP 브랜드 색상 적용
            actions=[
                ft.Container(
                    content=ft.ElevatedButton(
                        content=ft.Text("닫기", color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD),
                        bgcolor=com.MAIN_COLOR,
                        on_click=self.close_popup,
                        width=300,  # 버튼 너비를 확장하여 안정감 부여
                        height=55,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=15)
                        )
                    ),
                    padding=ft.padding.only(bottom=15) # 하단 여백
                )
            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            content_padding=ft.padding.symmetric(horizontal=20),
            shape=ft.RoundedRectangleBorder(radius=25), # 팝업 전체 테두리 둥글게
        )

    def show(self, e=None):
        self.page.show_dialog(self.dlg)

    def close_popup(self, e=None):
        self.page.pop_dialog()