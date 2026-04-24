import flet as ft
import components as dogdog

def content_container(content_list, on_click=None):
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=10, bottom=10),
        on_click=on_click,
        ink=True,
        border_radius=ft.border_radius.all(10),
        border=ft.Border.all(width=2, color=ft.Colors.GREY_200),
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_100, offset=ft.Offset(x=0, y=3)),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_list
        )
    )

select_log = {}
def log_container(page: ft.Page, pet_log_numeric_id, details):
    select_log.clear()
    storage = page.session.store
    bgcolor = None
    def click_test(e):
        content.bgcolor = ft.Colors.GREY_300 if content.bgcolor == None else None
        if not select_log.get(pet_log_numeric_id):
            select_log.update({pet_log_numeric_id:pet_log_numeric_id})
        else: select_log.pop(pet_log_numeric_id,None)
        storage.set("select_log",select_log)
    time = details["log_date"].split()[1].split(":")
    ampm = "오전" if int(time[0]) < 12 else "오후"
    hour = time[0] if int(time[0]) < 12 else int(time[0]) - 12
    if hour == 0: hour = 12
    message = (
        f"물을 {details["log_status"]}ml를 마셨습니다." if details["category"] == "음수량" else 
        f"사료를 {details["log_status"]}g을 먹었습니다." if details["category"] == "급여량" else 
        f"산책을 {details["log_status"]}분 했습니다." if details["category"] == "산책" else None
    )
    log_time = f"{ampm} {hour}:{time[1]}"

    content = ft.Container(
        padding=ft.Padding.only(right=10, left=10),
        width=3000,
        ink=True,
        on_click=click_test,
        bgcolor=bgcolor,
        height=50,
        border_radius=10,
        border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
            dogdog.basic_text(str(message), size=14, color=ft.Colors.GREY_700),
            dogdog.basic_text(log_time, size=14, color=ft.Colors.GREY_700)
    ]))
    
    return content