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
            actions_alignment = ft.MainAxisAlignment.END,
            actions=[
                ft.TextButton("OK"),
                ft.TextButton("Cancel", on_click=self.show_popup_close)
            ]
        )
        page.overlay.append(self.event_popup) if self.event_popup in page.overlay else None

        self.api_insert_dialog = ft.AlertDialog(
            modal=True,
            bgcolor=ft.Colors.TRANSPARENT,
            content=ft.Row(alignment=ft.MainAxisAlignment.CENTER,
                width=20, controls=[ft.ProgressRing(color=ft.Colors.BLUE_400)])
        )
        page.overlay.append(self.api_insert_dialog) if self.api_insert_dialog in page.overlay else None

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
                    spacing=10
                )
            )
        )

        page.overlay.append(self.bottom_sheet_popup) if self.bottom_sheet_popup in page.overlay else None

    async def show_api_insert_open(self, e):
        self.page.show_dialog(self.api_insert_dialog)
        self.page.update()

    async def show_api_insert_close(self, e):
        self.page.pop_dialog()
        self.page.update()

    def show_popup_open(self, e, case, title:str="", text=None, focus:bool=True, on_click=None):
        if case == "bottom_sheet":
            self.page.show_dialog(self.bottom_sheet_popup)
        elif case == "event_popup":
            self.event_popup.title.value = title # type: ignore
            self.event_popup.content.value = text # type: ignore
            self.event_popup.actions[0].autofocus = focus # type: ignore
            self.event_popup.actions[0].on_click = on_click # type: ignore
            self.page.show_dialog(self.event_popup)
        self.page.update()

    def show_popup_close(self, e):
        self.page.pop_dialog()
        self.page.update()
        
def popup_bottom_sheet():
    return 