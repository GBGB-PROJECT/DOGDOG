import flet as ft
from components import layout as ly
from components.common.erp_busy_cursor import install_busy_cursor, set_busy_cursor

# ☑️ route 기준 메뉴/뷰 연결용
from components.common import content_move as hcm


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
            # 🔥 추가: 화면 이동이 시작되면 전체 화면 커서를 PROGRESS로 변경
            set_busy_cursor(self.main_page, True)
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
            selected_menu=self.selected_menu,
            on_menu_click=self._on_menu_click,
        )

        # ☑️ 전체 레이아웃 조립
        # 🔥 추가: 전체 ERP 프레임을 GestureDetector로 감싸서
        # 🔥 조회/화면 이동 중 마우스 커서를 PROGRESS 모양으로 바꿀 수 있게 한다.
        self.busy_cursor_area = ft.GestureDetector(
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
        install_busy_cursor(page, self.busy_cursor_area)
        self.content = self.busy_cursor_area

    def set_route(self, route: str):
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

        self.current_route = normalized_route
        self.selected_menu = resolved_menu or "홈"

        # 🔥 우측 본문만 교체
        self.content_area.content = hcm.get_view_by_route(self.current_route)

        # 🔥 확장 사이드바/선택 표시만 갱신
        self.sidebar_area.content = ly.build_erp_sidebar(
            selected_menu=self.selected_menu,
            on_menu_click=self._on_menu_click,
        )
