from components import common as cm
import flet as ft

class custom_popup():
    def __init__(self, page: ft.Page):
        self.page = page
        # 팝업 객체를 미리 담아둘 변수를 생성합니다.
        self.dialog = None

    def _close_dig(self, e):
        # 팝업을 닫고 업데이트합니다.
        if self.dialog:
            self.dialog.open = False
            self.page.update()

    def confirm_popupbox(self, message="등록이 완료되었습니다."):
        # 1. 새로운 팝업창 객체를 생성합니다.
        self.dialog = ft.AlertDialog(
            modal=True,
            content_padding=ft.padding.all(30),
            content=ft.Column(
                controls=[
                    ft.Image(src="check_icon.png", width=100, height=100, fit="contain"),
                    ft.Container(height=10),
                    ft.Text(message, size=20, weight='bold', text_align="center"),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Row(controls=[ft.Text("Continue", color=cm.BOX_BG, weight='bold')
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor=cm.MAIN_COLOR,
                        width=250,
                        height=50,  
                        border_radius=ft.border_radius.all(30), 
                        ink=True,                               
                        on_click=self._close_dig,
                    )
                ],
                tight=True,
                horizontal_alignment="center"
            ),
        )
        # 2. [가장 중요] 페이지의 최상단 레이어(overlay)에 팝업을 추가합니다.
        self.page.overlay.append(self.dialog)
        # 3. 팝업을 열고 화면을 새로고침합니다.
        self.dialog.open = True
        self.page.update()

    def error_popup(self, message="작성하신 내용을\n다시 입력해주세요."):
        self.dialog = ft.AlertDialog(
            modal=True,
            content_padding=ft.padding.all(30),
            content=ft.Column(
                controls=[
                    ft.Image(src="incorrect_icon.png", width=100, height=100, fit="contain"),
                    ft.Container(height=10),
                    ft.Text(message, size=20, weight='bold', text_align="center"),
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Row(controls=[ft.Text("Continue", color=cm.BOX_BG, weight='bold')
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        bgcolor=cm.INCORRECT_POPUPCOLOR,
                        width=250,
                        height=50,  
                        border_radius=ft.border_radius.all(30), 
                        ink=True,                               
                        on_click=self._close_dig,
                    )
                ],
                tight=True,
                horizontal_alignment="center"
            ),
        )
        self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.update()