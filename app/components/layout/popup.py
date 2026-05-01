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
            actions_alignment = ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("OK"),
                ft.TextButton("Cancel", on_click=self.show_popup_close)
            ]
        )
        
        self.loading_dialog = ft.AlertDialog(
            modal=True,
            open=False,
            bgcolor=ft.Colors.TRANSPARENT,
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                width=20, controls=[ft.ProgressRing(color=ft.Colors.BLUE_400)])
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
                    controls=self.bottom_sheet_controls
                )
            )
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

