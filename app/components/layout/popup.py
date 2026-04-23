import flet as ft
import components as dogdog
import time
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
                ft.TextButton("Cancel", on_click=self.show_event_popup_close)
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

    async def show_open(self, e):
        self.page.show_dialog(self.api_insert_dialog)
        self.page.update()

    async def show_close(self, e):
        self.page.pop_dialog()
        self.page.update()
    
    def show_event_popup_open(self, e, title:str, text, focus:bool=True, on_click=None):
        self.event_popup.title.value = title # type: ignore
        self.event_popup.content.value = text # type: ignore
        self.event_popup.actions[0].autofocus = focus # type: ignore
        self.event_popup.actions[0].on_click = on_click # type: ignore

        self.page.show_dialog(self.event_popup)
        self.page.update()

    
    def show_event_popup_close(self, e):
        self.page.pop_dialog()
        self.page.update()