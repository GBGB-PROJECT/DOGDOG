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
    
    # 컨트롤러 컨테이너 리스트 초기화
    controller.log_containers = []
    
    # [정렬 100% 준수] 단일 루프 내에서 순서대로 UI 생성 및 배치
    for log in logs_data:
        log_id = log.get("id")
        domain = log.get("domain", "")
        category = log.get("category", "")
        
        # 1. 공통 로그 컨테이너 생성 (이 시점의 순서가 전체 탭의 순서가 됨)
        container = dogdog.log_container(page, log_id, details=log)
        
        # 2. 클릭 이벤트 바인딩
        container.on_click = lambda e, l=log, c=container: controller.select_log(l, c)
        
        # 3. '전체' 탭 및 컨트롤러 관리 리스트에 즉시 추가 (중요: 여기서 append 순서가 곧 화면 순서)
        controller.log_containers.append(container)
        all_log.append(container)
        
        # 4. 나머지 카테고리별 탭용 리스트에 분배 (순서는 그대로 유지됨)
        if domain == "feeding":
            feeding_log.append(container)
        elif domain == "numeric":
            if category == "water":
                watering_log.append(container)
            elif category == "walk":
                daily_work_log.append(container)
            elif category == "poop":
                poop_log.append(container)
            elif category in ["weight", "bcs"]:
                health_log.append(container)

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
