# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains as domains
import components as dogdog
import datetime
# -------------------------------------------------------------------------------------------------------
def home_tile(page: ft.Page, content_page:str, change_page_callback=None):
    # ---------------------------------------------------------------------------------------------------
    # Default Layout
    # ---------------------------------------------------------------------------------------------------
    main_container_content = []
    body_column = ft.Column(spacing=15, expand=True, margin=ft.margin.only(bottom=20))
    body_scroll_column = ft.Column(spacing=15, expand=True, scroll=ft.ScrollMode.HIDDEN, margin=ft.margin.only(bottom=20))
    home_background , top_banner = dogdog.home_layout(page=page, view="feeding")
    # ---------------------------------------------------------------------------------------------------
    # Routing Event
    # ---------------------------------------------------------------------------------------------------
    def appbar_on_change(e, on_change_page): change_page_callback(on_change_page) # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Test Popup
    popup = dogdog.Popup(page=page)
    def history_event(e):
        popup.show_popup_close(e)
        appbar_on_change(e, "/history")
    # ---------------------------------------------------------------------------------------------------
    # Home Tile Routeing
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/home":
        home_background , top_banner = dogdog.home_layout(page=page, view="home")
        main_container_content.append(top_banner)
        main_container_content.append(body_column)
        main_container_content.append(body_scroll_column)
        # -----------------------------------------------------------------------------------------------
        now_history = popup.bottom_sheet_popup
        now_history_content = now_history.content.content.controls # type: ignore
        now_history_content.clear()
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        history_title = dogdog.basic_text(f"오늘의 기록 : {now}", size=18, weight="bold")
        now_history_content.append(history_title)
        now_history_content.append(ft.Divider())
        storage = page.session.store
        count = 3 # 로그 출력양
        for pet_log_numeric_id , details in storage.get("history").items(): # type: ignore
            print(f"pet_log_numeric_id: {pet_log_numeric_id}")
            time = details["log_date"].split()[1].split(":")
            ampm = "오전" if int(time[0]) < 12 else "오후"
            hour = time[0] if int(time[0]) < 12 else int(time[0]) - 12
            if hour == 0: hour = 12
            message = (
                f"물을 {details['log_status']}ml를 마셨습니다." if details["category"] == "음수량" else 
                f"사료를 {details['log_status']}g을 먹었습니다." if details["category"] == "급여량" else 
                f"산책을 {details['log_status']}분 했습니다." if details["category"] == "산책" else None
            )
            log_time = f"{ampm} {hour}:{time[1]}"
            print(message, log_time)
            case = ft.Container(
                padding=ft.Padding.only(right=10, left=10),
                width=3000,
                height=50,
                border_radius=10,
                border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                    dogdog.basic_text(str(message), size=14, color=ft.Colors.GREY_700),
                    dogdog.basic_text(log_time, size=14, color=ft.Colors.GREY_700)
            ]))
            now_history_content.append(case)
            count = count - 1
            if count == 0: break
        history_page = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.TextButton(content=dogdog.basic_text("더보기", size=14,color=ft.Colors.GREY_500), on_click=lambda e:history_event(e))
        ])
        now_history_content.append(history_page)
        # -----------------------------------------------------------------------------------------------
        body_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.now_history(page=page),
                on_click=lambda e:popup.show_popup_open(e, "bottom_sheet")
        ))
        body_column.expand = False
        body_column.margin = None
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(page=page),
                on_click=lambda e:appbar_on_change(e, "/feeding")
        ))
        body_scroll_column.controls.append(domains.grid.status_update_menu(page=page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/log":
        home_background , top_banner = dogdog.home_layout(page=page, text="Log")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/shop":
        home_background , top_banner = dogdog.home_layout(page=page, text="Shop Test")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/contents":
        home_background , top_banner = dogdog.home_layout(page=page, text="Content")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/mypage":
        home_background , top_banner = dogdog.home_layout(page=page, text="My Page")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/history":
        home_background , top_banner = dogdog.home_layout(page=page, text="오늘의 기록")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding":
        home_background , top_banner = dogdog.home_layout(page=page, text="급여 중인 제품")
        main_container_content.append(top_banner)
        main_container_content.append(domains.feeding.feeding_tabs_view(page=page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_edit":
        home_background , top_banner = dogdog.home_layout(page=page, text="제품 정보 변경")
        main_container_content.append(top_banner)
        main_container_content.append(domains.feeding_add_edit.feeding_add_edit(page=page, view="edit"))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_add":
        home_background , top_banner = dogdog.home_layout(page=page, text="제품 등록")
        main_container_content.append(top_banner)
        main_container_content.append(domains.feeding_add_edit.feeding_add_edit(page=page, view="add"))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/notification":
        home_background , top_banner = dogdog.home_layout(page=page, text="알림")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/what_bowel_score":
        home_background , top_banner = dogdog.home_layout(page=page, text="배변 스코어란?")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.margin = ft.margin.only(top=20, bottom=20)
        body_scroll_column.controls.append(domains.guide.what_guide(page=page, content=content_page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/what_bcs":
        home_background , top_banner = dogdog.home_layout(page=page, text="BCS 란?")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.margin = ft.margin.only(top=20, bottom=20)
        body_scroll_column.controls.append(domains.guide.what_guide(page=page, content=content_page))
    # ---------------------------------------------------------------------------------------------------
    return home_background , main_container_content