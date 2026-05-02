import flet as ft
import components as dogdog
from domains.logs.views import grid_view


def history_view(page: ft.Page, logs_data: list, view_date_str: str, controller):
    """
    [View] History View
    UI 렌더링만 담당하며, 이벤트 처리 및 팝업 제어 로직은 controller로 위임합니다.
    """
    # Controller에 필요한 객체들 연결 (Controller에서 UI 조작을 위해 참조)
    controller.page = page
    controller.popup = dogdog.Popup(page)

    def insert_event(e):
        insert_grid.visible = not insert_grid.visible
        page.update()

    insert_log = ft.Container(
        ink=True,
        on_click=insert_event,
        border_radius=30,
        padding=10,
        content=ft.Column(
            spacing=-10,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icon=ft.Icons.ADD, size=30),
                dogdog.basic_text(value="기록추가", size=13, weight="bold"),
            ],
        ),
    )

    # 유물 참조 변경: domains.grid -> grid_view (올바른 뷰 경로)
    insert_grid = grid_view.status_update_menu(page=page, popup=controller.popup, on_refresh_callback=controller.on_refresh_callback)
    insert_grid.visible = False
    insert_grid.margin = ft.margin.only(bottom=10)
    
    all_log = []
    feeding_log = []
    watering_log = []
    daily_work_log = []
    poop_log = []
    health_log = []
    
    controller.log_containers.clear()

    for log in logs_data:
        # [수정 2] PK 다중 탐색 및 유니크 키 생성
        log_id = (
            log.get("id")
            or log.get("pet_food_id")
            or log.get("pet_log_numeric_id")
            or str(log.get("sort_timestamp", 0))
        )
        domain = log.get("domain", "unknown")
        category = log.get("category", "")
        log_key = f"{domain}_{log_id}"

        # 1. 잉크 방어용 래퍼 컨테이너 생성 (전체 탭)
        inner_all = dogdog.log_container(page, log_id, details=log)
        if hasattr(inner_all, "on_click"):
            inner_all.on_click = None  # 내부 컴포넌트 클릭 기능 제거

        container_all = ft.Container(
            content=inner_all,
            on_click=lambda e, l=log: controller.select_log(l, e.control),
            on_long_press=lambda e: None,  # 꾹 누르기 이벤트 강제 흡수 (잉크 방지)
            ink=False,  # 잉크 속성 끄기
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=10,
        )
        controller.register_container(log_key, container_all)
        all_log.append(container_all)

        # 2. 잉크 방어용 래퍼 컨테이너 생성 (필터 탭)
        inner_filter = dogdog.log_container(page, log_id, details=log)
        if hasattr(inner_filter, "on_click"):
            inner_filter.on_click = None

        container_filter = ft.Container(
            content=inner_filter,
            on_click=lambda e, l=log: controller.select_log(l, e.control),
            on_long_press=lambda e: None,
            ink=False,
            bgcolor=ft.Colors.TRANSPARENT,
            border_radius=10,
        )
        controller.register_container(log_key, container_filter)

        # 3. 카테고리별 필터 탭 리스트에 분배
        if domain == "feeding":
            feeding_log.append(container_filter)
        elif domain == "numeric":
            if category == "water":
                watering_log.append(container_filter)
            elif category == "walk":
                daily_work_log.append(container_filter)
            elif category == "poop":
                poop_log.append(container_filter)
            elif category in ["weight", "bcs"]:
                health_log.append(container_filter)

    logs_tab = [
        ft.Tab(label="전체"),
        ft.Tab(label="급여량"),
        ft.Tab(label="음수량"),
        ft.Tab(label="활동기록"),
        ft.Tab(label="배변"),
        ft.Tab(label="건강기록"),
    ]

    def content_column(content):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            controls=content,
            margin=ft.margin.only(bottom=10),
        )

    def setting_content(visible):
        """삭제 및 수정 버튼 섹션 (로직은 controller로 위임)"""
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(
                    "삭제", 
                    visible=visible, 
                    on_click=controller.history_delete
                ),
                dogdog.flat_button(
                    "수정", 
                    bgcolor="#FEF3B9", 
                    visible=visible, 
                    on_click=controller.history_edit
                ),
            ],
        )

    logs_content = [
        content_column(all_log),
        content_column(feeding_log),
        content_column(watering_log),
        content_column(daily_work_log),
        content_column(poop_log),
        content_column(health_log),
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
                setting_content(len(all_log) > 0),
            ],
        ),
    )

    return logs_tabs
