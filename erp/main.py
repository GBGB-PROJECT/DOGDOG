import os
import webbrowser
import flet as ft

from components.layout.sidebar import build_erp_sidebar
from components.layout.topbar import build_erp_topbar
from domain.views.home_view import erp_home_view
from domain.views.sales_view import erp_sales_view
from domain.views.inventory_view import erp_inventory_view

import components as components
import domain.views as views

PAGE_BG = "#FFFFFF"


def main(page: ft.Page):
    page.title = "ERP"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = PAGE_BG
    page.window_width = 1440
    page.window_height = 900

    # ✅ 상태
    selected_menu = {"value": "홈"}

    # ✅ 영역 미리 선언
    sidebar = ft.Container()
    topbar = build_erp_topbar()
    content_area = ft.Container(expand=True)

    # ✅ 뷰 선택 함수
    def get_view(menu_name: str):
        if menu_name == "홈":
            return erp_home_view()
        if menu_name == "매출관리":
            return erp_sales_view()
        if menu_name == "재고관리":
            return erp_inventory_view()

        return ft.Container(
            expand=True,
            bgcolor=PAGE_BG,
            padding=20,
            content=ft.Text(
                value=f"{menu_name} 화면",
                size=22,
                color="#444444",
                weight=ft.FontWeight.W_700,
            ),
        )

    # ✅ UI 렌더링
    def render_page():
        # sidebar 업데이트
        sidebar.content = build_erp_sidebar(
            selected_menu=selected_menu["value"],
            on_menu_click=on_menu_click,
        )

        # content 업데이트
        content_area.content = get_view(selected_menu["value"])

        page.update()

    # ✅ 메뉴 클릭
    def on_menu_click(menu_name: str):
        selected_menu["value"] = menu_name
        render_page()

    # ✅ 
    main_layout = ft.Row(
        expand=True,
        spacing=0,
        controls=[
            sidebar,
            ft.Column(
                expand=True,
                spacing=0,
                controls=[
                    topbar,
                    content_area,
                ],
            ),
        ],
    )

    # ✅ 최초 렌더
    page.add(main_layout)
    render_page()


# ✅ 실행부 (요구사항 반영)
if __name__ == "__main__":
    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None

    ft.run(
        main,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        port=34636,
    )