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

# select_log = {}
def log_container(page: ft.Page, pet_log_numeric_id, details):
    bgcolor = None
    
    def click_test(e):
        content.bgcolor = ft.Colors.GREY_300 if content.bgcolor == None else None
        content.update() # 클릭 시 색상 변경을 위해 꼭 필요합니다!

    # 1. 시간 변환 로직 (API의 display_time "13:23" 활용)
    display_time = details.get("display_time", "00:00")
    time_parts = display_time.split(":")
    hour = int(time_parts[0])
    minute = time_parts[1]
    
    ampm = "오전" if hour < 12 else "오후"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0: display_hour = 12
    log_time = f"{ampm} {display_hour}:{minute}"

    # 2. 메시지 변환 로직 (API의 domain과 amount, unit 활용)
    domain = details.get("domain", "")
    amount = details.get("amount", 0)
    unit = details.get("unit", "")
    
    if domain == "feeding":
        message = f"사료를 {amount}{unit} 먹었습니다."
    elif domain == "water":
        message = f"물을 {amount}{unit} 마셨습니다."
    elif domain == "walk":
        message = f"산책을 {amount}분 했습니다."
    else:
        message = f"기록을 {amount}{unit} 남겼습니다." # 혹시 모를 기타 기록 방어코드

    # 3. UI 조립
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
                dogdog.basic_text(message, size=14, color=ft.Colors.GREY_700),
                dogdog.basic_text(log_time, size=14, color=ft.Colors.GREY_700)
            ]
        )
    )
    
    return content
# def log_container(page: ft.Page, pet_log_numeric_id, details):
#     # select_log.clear()
#     # storage = page.session.store
#     bgcolor = None
#     def click_test(e):
#         content.bgcolor = ft.Colors.GREY_300 if content.bgcolor == None else None
#         # if not select_log.get(pet_log_numeric_id):
#         #     select_log.update({pet_log_numeric_id:pet_log_numeric_id})
#         # else: select_log.pop(pet_log_numeric_id,None)
#         # storage.set("select_log",select_log)
#     time = details["log_date"].split()[1].split(":")
#     ampm = "오전" if int(time[0]) < 12 else "오후"
#     hour = time[0] if int(time[0]) < 12 else int(time[0]) - 12
#     if hour == 0: hour = 12
#     message = (
#         f"물을 {details['log_status']}ml를 마셨습니다." if details['category'] == "음수량" else 
#         f"사료를 {details['log_status']}g을 먹었습니다." if details['category'] == "급여량" else 
#         f"산책을 {details['log_status']}분 했습니다." if details['category'] == "산책" else None
#     )
#     log_time = f"{ampm} {hour}:{time[1]}"

#     content = ft.Container(
#         padding=ft.Padding.only(right=10, left=10),
#         width=3000,
#         ink=True,
#         on_click=click_test,
#         bgcolor=bgcolor,
#         height=50,
#         border_radius=10,
#         border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
#         content=ft.Row(
#             alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
#             controls=[
#             dogdog.basic_text(str(message), size=14, color=ft.Colors.GREY_700),
#             dogdog.basic_text(log_time, size=14, color=ft.Colors.GREY_700)
#     ]))
    
#     return content