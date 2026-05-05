import flet as ft
from components import layout as ly

from components.common import content_move as hcm
from components.common.erp_busy_cursor import register_busy_cursor_host


class ErpFrame(ft.Container):
    _NO_CACHE_ROUTES = {
        "/production/order",
    }

    def __init__(self, page: ft.Page, current_route: str):
        super().__init__()
        self.main_page = page
        self.expand = True
        self.current_route = hcm.normalize_route(current_route)
        self.selected_menu = hcm.get_menu_by_route(self.current_route) or "홈"
        self._view_cache = {}

        def on_menu_click(menu_name: str):
            target_route = hcm.normalize_route(hcm.get_route_by_menu(menu_name))
            if self.current_route == target_route:
                return
            self.main_page.go(target_route)

        self._on_menu_click = on_menu_click
        self.sidebar_area = ft.Container()
        self.content_area = ft.Container(
            expand=True,
            content=self._get_cached_view(self.current_route),
        )

        self.sidebar_area.content = ly.build_erp_sidebar(
            page=page,
            selected_menu=self.selected_menu,
            on_menu_click=self._on_menu_click,
        )

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

    def _get_cached_view(self, route: str):
        normalized_route = hcm.normalize_route(route)
        if normalized_route in self._NO_CACHE_ROUTES:
            return hcm.get_view_by_route(normalized_route)

        if normalized_route not in self._view_cache:
            self._view_cache[normalized_route] = hcm.get_view_by_route(normalized_route)
        return self._view_cache[normalized_route]

    def set_route(self, route: str, *, update: bool = False):
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
        self.content_area.content = self._get_cached_view(self.current_route)

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
