import flet as ft
from components import layout as ly

# ☑️ route 기준 메뉴/뷰 연결용
from components.common import content_move as hcm
from components.common.erp_busy_cursor import register_busy_cursor_host


class ErpFrame(ft.Container):
    def __init__(self, page: ft.Page, current_route: str):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.current_route = hcm.normalize_route(current_route)
        self.selected_menu = hcm.get_menu_by_route(self.current_route) or "홈"

        # ☑️ 메뉴 클릭 시 route 변경
        def on_menu_click(menu_name: str):
            target_route = hcm.get_route_by_menu(menu_name)
            target_route = hcm.normalize_route(target_route)

            # 🔥 같은 route를 다시 누르면 불필요한 재렌더링 방지
            if self.current_route == target_route:
                return

            # 🔥 화면 이동 안정화
            # - 현재 프로젝트는 page.go() 기반으로 route_change가 정상 동작한다.
            # - push_route() 사용 시 로그인/메뉴 이동이 멈추는 환경이 있어 page.go()로 고정한다.
            self.main_page.go(target_route)

        self._on_menu_click = on_menu_click

        # ☑️ 사이드바 영역을 따로 관리
        self.sidebar_area = ft.Container()

        # ☑️ 본문 도화지
        self.content_area = ft.Container(
            expand=True,
            content=hcm.get_view_by_route(self.current_route),
        )

        # ☑️ 초기 사이드바 세팅
        self.sidebar_area.content = ly.build_erp_sidebar(
            page=page,
            selected_menu=self.selected_menu,
            on_menu_click=self._on_menu_click,
        )

        # ☑️ 전체 레이아웃 조립
        # 🔥 전체 ERP 프레임을 GestureDetector로 감싸서 화면 이동/조회 중 전체 커서를 바꿀 수 있게 함
        self._root_busy_cursor = ft.GestureDetector(
            mouse_cursor=ft.MouseCursor.BASIC,
            content=ft.Row(
                expand=True,
                spacing=0,
                controls=[
                    self.sidebar_area,
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            ly.build_erp_topbar(page),
                            self.content_area,
                        ],
                    ),
                ],
            ),
        )
        register_busy_cursor_host(page, self._root_busy_cursor)
        self.content = self._root_busy_cursor

    def set_route(self, route: str, *, update: bool = False):
        """
        🔥 화면 전환 속도 개선
        - ErpFrame/topbar/전체 Row는 재생성하지 않는다.
        - route 변경 시 사이드바 선택 상태와 우측 본문만 교체한다.
        """
        normalized_route = hcm.normalize_route(route)
        resolved_menu = hcm.get_menu_by_route(normalized_route)

        if resolved_menu is None:
            normalized_route = hcm.DEFAULT_AUTH_ROUTE
            resolved_menu = hcm.get_menu_by_route(normalized_route)

        if self.current_route == normalized_route:
            return False

        previous_menu = self.selected_menu
        self.current_route = normalized_route
        self.selected_menu = resolved_menu or "홈"

        # 🔥 우측 본문만 교체
        self.content_area.content = hcm.get_view_by_route(self.current_route)

        # 🔥 확장 사이드바/선택 표시만 갱신
        sidebar_changed = previous_menu != self.selected_menu
        if sidebar_changed:
            self.sidebar_area.content = ly.build_erp_sidebar(
                page=self.main_page,
                selected_menu=self.selected_menu,
                on_menu_click=self._on_menu_click,
            )

        if update:
            self.content_area.update()
            if sidebar_changed:
                self.sidebar_area.update()

        return True
