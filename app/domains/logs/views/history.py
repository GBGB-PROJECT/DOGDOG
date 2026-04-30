import flet as ft
import components as dogdog
import datetime
import domains


def history_view(page: ft.Page, logs_data: list, view_date_str: str):
    """
    [View] History View
    컨트롤러로부터 전달받은 logs_data와 view_date_str을 사용하여 타임라인 뷰를 렌더링합니다.
    """
    popup = dogdog.Popup(page)

    def insert_event(e):
        insert_grid.visible = True if insert_grid.visible == False else False
        page.update()

    insert_log = ft.Container(
        ink=True,
        on_click=lambda e: insert_event(e),
        border_radius=30,
        padding=10,
        content=ft.Column(
            spacing=-10,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon=ft.Icons.ADD, size=30),
                dogdog.basic_text(value="기록추가", size=16, weight="bold"),
            ],
        ),
    )

    insert_grid = domains.grid.status_update_menu(page=page, popup=popup)
    insert_grid.visible = False
    insert_grid.margin = ft.margin.only(bottom=10)
    
    all_log = []
    feeding_log = []
    watering_log = []
    daily_work_log = []
    
    # 전달받은 logs_data를 domain 기준으로 필터링하여 컨테이너 생성
    for log in logs_data:
        log_id = log.get("id")
        domain = log.get("domain", "")
        
        container = dogdog.log_container(page, log_id, details=log)
        all_log.append(container)
        
        if domain == "feeding":
            feeding_log.append(container)
        elif domain == "water":
            watering_log.append(container)
        elif domain == "walk":
            daily_work_log.append(container)

    logs_tab = [
        ft.Tab(label="전체"),
        ft.Tab(label="급여량"),
        ft.Tab(label="음수량"),
        ft.Tab(label="활동량"),
    ]

    def content_column(content):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            controls=content,
            margin=ft.margin.only(bottom=10),
        )

    def setting_content(visible):
        delete_popup = popup.event_popup
        delete_popup.title = dogdog.basic_text("오늘의 기록")
        delete_popup.content = dogdog.basic_text("선택하신 기록을 삭제하시겠습니까?")
        delete_popup.actions[0].on_click = lambda e: delete_popup_close(e, options=True)  # type: ignore

        def delete_popup_close(e, options=None):
            delete_popup.open = False
            if options:
                print(e)
            page.update()

        def history_delete(e):
            if delete_popup not in page.overlay:
                page.overlay.append(delete_popup)
            else:
                page.overlay.clear()
                page.overlay.append(delete_popup)
            delete_popup.open = True
            page.update()

        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(
                    "삭제", visible=visible, on_click=lambda e: history_delete(e)
                ),
                dogdog.flat_button(
                    "수정", bgcolor="#FEF3B9", visible=visible, on_click=None
                ),
            ],
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
                ft.Row(
                    margin=ft.margin.only(left=10, right=10, bottom=10),
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        dogdog.basic_text(view_date_str, weight="bold", size=18),
                        insert_log,
                    ],
                ),
                insert_grid,
                ft.TabBar(
                    indicator_size=ft.TabBarIndicatorSize.TAB,
                    divider_height=0,
                    tabs=logs_tab,
                    label_text_style=dogdog.TextStyle(size=14, height=-1),
                ),
                ft.Divider(height=1),
                ft.TabBarView(
                    expand=True, margin=ft.margin.only(top=10), controls=logs_content
                )
                if len(all_log) > 0
                else ft.Container(
                    expand=True,
                    alignment=ft.Alignment.CENTER,
                    content=dogdog.basic_text(
                        "작성된 기록이 없습니다", size=20, weight="bold"
                    ),
                ),
                setting_content(True if len(all_log) > 0 else False),
            ],
        ),
    )

    return logs_tabs
