import flet as ft
from components import layout as ly
from components import common as cm

# ☑️ route 기준 메뉴/뷰 연결용
from components.common import content_move as hcm


class ErpFrame(ft.Container):
    def __init__(self, page: ft.Page, current_route: str):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.current_route = hcm.normalize_route(current_route)
        self.selected_menu = hcm.get_menu_by_route(self.current_route) or "홈"

        # ☑️ route 기준으로 현재 본문 생성
        current_content = hcm.get_view_by_route(self.current_route)

        # ☑️ 사이드바 영역을 따로 관리
        self.sidebar_area = ft.Container()

        # ☑️ 본문 도화지
        self.content_area = ft.Container(
            expand=True,
            content=current_content,
        )

        # ☑️ 메뉴 클릭 시 route 변경
        def on_menu_click(menu_name: str):
            target_route = hcm.get_route_by_menu(menu_name)

            # 🔥 같은 route를 다시 누르면 불필요한 재렌더링 방지
            if hcm.normalize_route(self.main_page.route) == target_route:
                return

            self.main_page.go(target_route)

        # ☑️ 초기 사이드바 세팅
        self.sidebar_area.content = ly.build_erp_sidebar(
            selected_menu=self.selected_menu,
            on_menu_click=on_menu_click,
        )

        # ☑️ 전체 레이아웃 조립
        self.content = ft.Row(
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
        )
