import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------


class Popup:
    def __init__(self, page: ft.Page):
        self.page = page

        self.event_popup = ft.AlertDialog(
            modal=True,
            title=dogdog.basic_text(value="Quit"),
            content=dogdog.basic_text(value="Exit?"),
            bgcolor=ft.Colors.WHITE,
            actions_alignment=ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("OK"),
                ft.TextButton("Cancel", on_click=self.show_popup_close),
            ],
        )

        self.loading_dialog = ft.AlertDialog(
            modal=True,
            open=False,
            bgcolor=ft.Colors.TRANSPARENT,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                width=20,
                controls=[ft.ProgressRing(color=ft.Colors.BLUE_400)],
            ),
        )

        self.bottom_sheet_controls = []
        self.bottom_sheet_popup = ft.AlertDialog(
            alignment=ft.Alignment(0, 1),
            expand=True,
            inset_padding=0,
            content_padding=0,
            action_button_padding=0,
            actions_padding=0,
            scrollable=True,
            content=ft.Container(
                width=3000,
                padding=20,
                bgcolor=ft.Colors.WHITE,
                border_radius=ft.BorderRadius.only(
                    top_left=20,
                    top_right=20,
                ),
                content=ft.Column(
                    tight=True,
                    expand=True,
                    spacing=10,
                    controls=self.bottom_sheet_controls,
                ),
            ),
        )

        self.feeding_guide_controls = []
        self.feeding_guide = ft.AlertDialog(
            modal=True,
            expand=True,
            inset_padding=0,
            content_padding=0,
            action_button_padding=0,
            actions_padding=0,
            scrollable=True,
            content=ft.Container(
                width=300,
                padding=20,
                bgcolor="#FEF3B9",
                border_radius=20,
                content=ft.Column(
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                    controls=self.feeding_guide_controls,
                ),
            ),
        )

        # Bottom Sheet Setting (popup)
        # self.your_bottom_sheet = self.popup.bottom_sheet_popup
        # self.your_bottom_sheet_contents = self.popup.bottom_sheet_controls
        # self.your_bottom_sheet_contents.clear()

        # Bottom Sheet Open (popup)
        # if class.your_bottom_sheet not in page.overlay:
        #     page.overlay.append(class.your_bottom_sheet)
        # else:
        #     page.overlay.clear()
        #     page.overlay.append(class.your_bottom_sheet)
        # class.your_bottom_sheet.open = True
        # page.update()

        # Bottom Sheet Close (popup)
        # self.your_bottom_sheet.open = False
        # self.page.update()

    def show_popup_close(self, e):
        self.page.pop_dialog()
        self.page.update()

    async def show_api_insert_open(self, e=None):
        """API 통신 시작 시 빙글빙글 로딩 창을 띄웁니다."""
        self.page.dialog = self.loading_dialog
        self.loading_dialog.open = True
        self.page.update()

    async def show_api_insert_close(self, e=None):
        """API 통신 종료 시 로딩 창을 닫습니다."""
        self.loading_dialog.open = False
        self.page.update()

    def show_feeding_guide_open(self, pet_name, guide_intake):
        """AI 급여 권장량 팝업을 열고 데이터를 주입합니다."""
        if self.feeding_guide not in self.page.overlay:
            self.page.overlay.append(self.feeding_guide)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(self.feeding_guide)

        self.feeding_guide_controls.clear()

        # 1. 메시지 구성
        guide_message = dogdog.basic_text(
            spans=[
                ft.TextSpan("똑똑 AI가 계산한\n", style=dogdog.TextStyle(size=12)),
                ft.TextSpan(f"{pet_name}에게\n", style=dogdog.TextStyle(size=18)),
                ft.TextSpan("딱 맞춘 하루 권장량", style=dogdog.TextStyle(size=18)),
            ],
            weight="bold",
        )
        guide_message.text_align = ft.TextAlign.CENTER

        # 2. 권장량 수치 주입 (동적 바인딩)
        feeding_guide = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=0,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Image(
                            src="speech_bubble.png", height=100, color=ft.Colors.WHITE
                        ),
                        dogdog.basic_text(f"{guide_intake}g", weight="bold", size=40),
                    ],
                    spacing=-90,
                ),
                ft.Image(src="dogbowl.png", height=100, margin=ft.margin.only(top=20)),
            ],
        )

        # 3. 닫기 버튼
        home_view_feeding_guide_cancel = ft.IconButton(
            icon=ft.Icons.CANCEL_ROUNDED,
            icon_color="#E6001A",
            icon_size=30,
            on_click=lambda e: self.show_feeding_guide_close(e, self.feeding_guide),
        )

        # 4. 컨트롤 주입 및 팝업 활성화
        self.feeding_guide_controls.append(guide_message)
        self.feeding_guide_controls.append(feeding_guide)
        self.feeding_guide_controls.append(home_view_feeding_guide_cancel)

        self.feeding_guide.open = True
        self.page.update()

    def show_feeding_guide_close(self, e, feeding_guide_popup):
        feeding_guide_popup.open = False

        callback = getattr(self.page, "on_feeding_guide_closed", None)
        if callback:
            self.page.on_feeding_guide_closed = None
            self.page.run_task(callback)
            
        self.page.update()
