import flet as ft
import components as dogdog
import datetime

def now_log(page: ft.Page, popup, now_history):
    def history_event(e):
        popup.show_popup_close(e)
        page.go("/history")

    now_history_content = now_history.content.content.controls # type: ignore
    now_history_content.clear()
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    history_title = dogdog.basic_text(f"오늘의 기록 : {now}", size=18, weight="bold")
    now_history_content.append(history_title)
    now_history_content.append(ft.Divider())
    storage = page.session.store
    for pet_log_numeric_id , details in list(storage.get("history").items())[:3]: # type: ignore
        now_history_content.append(dogdog.log_container(page, pet_log_numeric_id, details=details))
    history_page = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
        ft.TextButton(content=dogdog.basic_text("더보기", size=14,color=ft.Colors.GREY_500), on_click=lambda e:history_event(e))
    ])
    now_history_content.append(history_page)