# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains as domains
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def home_tile(page: ft.Page, popup, content_page:str, change_page_callback=None):
    # ---------------------------------------------------------------------------------------------------
    # Default Layout
    # ---------------------------------------------------------------------------------------------------
    main_container_content = []
    body_column = ft.Column(spacing=15, expand=True, margin=ft.margin.only(bottom=20))
    body_scroll_column = ft.Column(spacing=15, expand=True, scroll=ft.ScrollMode.HIDDEN, margin=ft.margin.only(bottom=20))
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
        # -----------------------------------------------------------------------------------------------
        body_column.controls.append(domains.home.now_history(page=page, popup=popup))
        body_column.expand = False
        body_column.margin = None
        # -----------------------------------------------------------------------------------------------
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(page=page, content_page=content_page),
                on_click=lambda e:appbar_on_change(e, "/feeding")))
        body_scroll_column.controls.append(domains.grid.status_update_menu(page=page, popup=popup))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/log":
        home_background , top_banner = dogdog.home_layout(page=page, text="Log")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        body_scroll_column.controls = domains.log.log_view(page)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/shop":
        home_background , top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.shop.shop_feeding_guide(page=page))
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(page=page, content_page=content_page),
                on_click=lambda e:appbar_on_change(e, "/feeding")))
        body_scroll_column.controls.append(domains.shop.product_guide(page=page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/contents":
        home_background , top_banner = dogdog.home_layout(page=page, text="Content")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/mypage":
        home_background , top_banner = dogdog.home_layout(page=page, text="마이페이지")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls = domains.mypage_view.mypage_view(page)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/history":
        home_background , top_banner = dogdog.home_layout(page=page, text="오늘의 기록")
        main_container_content.append(top_banner)
        main_container_content.append(domains.history.history_view(page))
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
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.notification.notification_dummy(page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/notification_setting":
        home_background , top_banner = dogdog.home_layout(page=page, text="알림 설정")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.notification.notification_setting(page))
    # ---------------------------------------------------------------------------------------------------
    elif "/shop/" in content_page:
        home_background , top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        if "product/" in content_page:
            body_scroll_column.controls.append(domains.shop_product_detail.shop_product_detail(
                page=page, popup=popup, content_page=content_page))
    # ---------------------------------------------------------------------------------------------------
    return home_background , main_container_content