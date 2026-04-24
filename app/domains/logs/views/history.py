import flet as ft
import components as dogdog
import datetime
import domains

def history_view(page: ft.Page):
    popup = dogdog.Popup(page)
    storage = page.session.store
    if storage.get("select_log"): storage.remove("select_log")
    user_logs = storage.get("history")

    def insert_event(e):
        insert_grid.visible = True if insert_grid.visible == False else False
        page.update()
    insert_log = ft.Container(
        ink=True,
        on_click=lambda e:insert_event(e),
        border_radius=30,
        padding=10,
        content=ft.Column(
            spacing=-10,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon=ft.Icons.ADD, size=30),
                dogdog.basic_text(value="기록추가", size=16, weight="bold")
            ]
        )
    )

    insert_grid = domains.grid.status_update_menu(page=page)
    insert_grid.visible = False
    insert_grid.margin = ft.margin.only(bottom=10)

    storage = page.session.store
    all_log = []
    feeding_log = []
    watering_log = []
    daily_work_log = []
    for pet_log_numeric_id , details in user_logs.items(): # type: ignore
        # if details["log_date"].split()[0] == datetime.datetime.now().strftime("%Y-%m-%d"):
            all_log.append(
                dogdog.log_container(page, pet_log_numeric_id, details))
            if details["category"] == "급여량": 
                feeding_log.append(
                    dogdog.log_container(page, pet_log_numeric_id, details))
            if details["category"] == "음수량": 
                watering_log.append(
                    dogdog.log_container(page, pet_log_numeric_id, details))
            if details["category"] == "산책": 
                daily_work_log.append(
                    dogdog.log_container(page, pet_log_numeric_id, details))

    logs_tab = [
        ft.Tab(label="전체"),
        ft.Tab(label="급여량"),
        ft.Tab(label="음수량"),
        ft.Tab(label="활동량"),
    ]

    def content_column(content):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN, expand=True, controls=content, margin=ft.margin.only(bottom=10)
        )
    
    def delete_popup(e):
        page.pop_dialog()
        if storage.get("select_log"): 
            print(storage.get("select_log").keys()) # type: ignore
            storage.remove("select_log")
    
    def setting_content(visible):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(
                    "삭제", disabled=False, scale=1, visible=visible,
                    on_click=lambda e:popup.show_popup_open(
                        e, case="event_popup", title="오늘의 기록", text="선택하신 기록을 삭제하시겠습니까?", focus=False,
                        on_click=lambda e:delete_popup(e)
                    )),
                dogdog.flat_button(
                    "수정", disabled=False, scale=1, bgcolor="#FEF3B9", visible=visible, # type: ignore
                    on_click=None),
            ] # type: ignore
        )

    logs_content = [
        content_column(all_log),
        content_column(feeding_log),
        content_column(watering_log),
        content_column(daily_work_log),
    ]

    logs_tabs = ft.Tabs(
        selected_index=0,
        length=len(logs_tab),
        expand=True,
        content=ft.Column(
            margin=ft.margin.only(bottom=30),
            expand=True,
            spacing=0,
            controls=[
                ft.Row(margin=ft.margin.only(left=10, right=10, bottom=10), alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    dogdog.basic_text(datetime.datetime.now().strftime("%Y.%m.%d"), weight="bold", size=18),
                    insert_log
                ]),
                insert_grid,
                ft.TabBar(indicator_size=ft.TabBarIndicatorSize.TAB, divider_height=0,
                    tabs=logs_tab, label_text_style=dogdog.TextStyle(size=14)), # type: ignore
                ft.Divider(height=1),
                ft.TabBarView(expand=True, margin=ft.margin.only(top=10), 
                    controls=logs_content) if len(all_log) > 0 else ft.Container( # type: ignore
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=dogdog.basic_text("작성된 기록이 없습니다", size=20, weight="bold")
                ),
                setting_content(True if len(all_log) > 0 else False)
    ]))

    return logs_tabs