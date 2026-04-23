# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains as domains
import components as dogdog
from api.user_data import User
# -------------------------------------------------------------------------------------------------------
def home_tile(page: ft.Page, content_page:str, change_page_callback=None):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    storage.set("pet_list", User.pet_list)
    storage.set("customer_detail", User.customer_food_detail)
    # ---------------------------------------------------------------------------------------------------
    # Default Layout
    # ---------------------------------------------------------------------------------------------------
    main_container_content = []
    body_column = ft.Column(spacing=15, expand=True, margin=ft.margin.only(bottom=20))
    body_scorll_column = ft.Column(spacing=15, expand=True, scroll=ft.ScrollMode.HIDDEN, margin=ft.margin.only(bottom=20))
    home_background , top_banner = dogdog.home_layout(page=page, view="feeding")
    # ---------------------------------------------------------------------------------------------------
    # Routing Event
    # ---------------------------------------------------------------------------------------------------
    def appbar_on_change(e, on_change_page): change_page_callback(on_change_page) # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Home Tile Routeing
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/home":
        home_background , top_banner = dogdog.home_layout(page=page, view="home")
        main_container_content.append(top_banner)
        main_container_content.append(body_column)
        main_container_content.append(body_scorll_column)
        body_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.now_history(page=page),
                on_click=lambda e:appbar_on_change(e, "/history")
        ))
        body_column.expand = False
        body_column.margin = None
        body_scorll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(page=page),
                on_click=lambda e:appbar_on_change(e, "/feeding")
        ))
        body_scorll_column.controls.append(domains.grid.status_update_menu(page=page))
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
    return home_background , main_container_content