# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains as domains
import components as dogdog
from .home.home_controller import HomeController


# -------------------------------------------------------------------------------------------------------
def home_tile(
    page: ft.Page,
    popup,
    content_page: str,
    change_page_callback=None,
    on_refresh_callback=None,
):
    # ---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------
    # Controller Init & PubSub
    # ---------------------------------------------------------------------------------------------------
    controller = HomeController(page)

    # ---------------------------------------------------------------------------------------------------
    # Default Layout
    # ---------------------------------------------------------------------------------------------------
    main_container_content = []
    body_column = ft.Column(spacing=15, expand=True, margin=ft.margin.only(bottom=20))
    body_scroll_column = ft.Column(
        spacing=15,
        expand=True,
        scroll=ft.ScrollMode.HIDDEN,
        margin=ft.margin.only(bottom=20),
    )
    home_background, top_banner = dogdog.home_layout(page=page, view="feeding")

    # ---------------------------------------------------------------------------------------------------
    # Routing Event
    # ---------------------------------------------------------------------------------------------------
    def appbar_on_change(e, on_change_page):
        change_page_callback(on_change_page)  # type: ignore

    # ---------------------------------------------------------------------------------------------------
    # Home Tile Routeing
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/home":
        home_background, top_banner = dogdog.home_layout(page=page, view="home")
        main_container_content.append(top_banner)
        main_container_content.append(body_column)
        # -----------------------------------------------------------------------------------------------
        body_column.controls.append(
            domains.home.now_history(
                page=page, 
                popup=popup, 
                stats_data=controller.get_today_record_stats(),
                history_logs=controller.get_formatted_history(count=3)
            )
        )
        body_column.expand = False
        body_column.margin = None
        # -----------------------------------------------------------------------------------------------
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(
                    page=page, 
                    content_page=content_page,
                    inventory_stats=controller.get_food_inventory_stats()
                ),
                on_click=lambda e: appbar_on_change(e, "/feeding"),
            )
        )
        body_scroll_column.controls.append(
            domains.grid.status_update_menu(page=page, popup=popup)
        )

        # -----------------------------------------------------------------------------------------------
        # PubSub: 대시보드 동기화 이벤트 구독 및 컴포넌트 부분 업데이트
        # -----------------------------------------------------------------------------------------------
        async def refresh_dashboard_task(msg):
            if msg == "update_dashboard" and content_page == "/home":
                pet_id = page.session.store.get("current_pet_id")
                if pet_id:
                    # 최신 데이터 API 패치
                    await controller.fetch_dashboard_data(pet_id)
                    
                    # 1. 상단 '오늘의 기록' 컴포넌트 교체
                    if len(body_column.controls) > 0:
                        body_column.controls[0] = domains.home.now_history(
                            page=page, 
                            popup=popup, 
                            stats_data=controller.get_today_record_stats(),
                            history_logs=controller.get_formatted_history(count=3)
                        )
                        body_column.update()
                        
                    # 2. 하단 '사료 잔여량' 컴포넌트 교체 (index 0)
                    if len(body_scroll_column.controls) > 0:
                        body_scroll_column.controls[0] = dogdog.content_container(
                            content_list=domains.home.feeding_food_count(
                                page=page, 
                                content_page=content_page,
                                inventory_stats=controller.get_food_inventory_stats()
                            ),
                            on_click=lambda e: appbar_on_change(e, "/feeding"),
                        )
                        body_scroll_column.update()

        # 기존 구독된 함수가 있다면 제거하여 중복 실행 방지
        page.pubsub.unsubscribe_all()
        page.pubsub.subscribe(lambda msg: page.run_task(refresh_dashboard_task, msg))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/log":
        home_background, top_banner = dogdog.home_layout(page=page, text="Log")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        body_scroll_column.controls = domains.log.log_view(page)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/shop":
        home_background, top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.shop.shop_feeding_guide(page=page))
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home.feeding_food_count(
                    page=page, 
                    content_page=content_page,
                    inventory_stats=controller.get_food_inventory_stats()
                ),
                on_click=lambda e: appbar_on_change(e, "/feeding"),
            )
        )
        body_scroll_column.controls.append(domains.shop.product_guide(page=page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/contents":
        home_background, top_banner = dogdog.home_layout(page=page, text="Content")
        main_container_content.append(top_banner)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/mypage":
        home_background, top_banner = dogdog.home_layout(page=page, text="마이페이지")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls = domains.mypage_view.mypage_view(page)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/history":
        home_background, top_banner = dogdog.home_layout(page=page, text="오늘의 기록")
        main_container_content.append(top_banner)
        main_container_content.append(domains.history.history_view(page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding":
        home_background, top_banner = dogdog.home_layout(
            page=page, text="급여 중인 제품"
        )
        main_container_content.append(top_banner)
        main_container_content.append(
            domains.feeding.feeding_tabs_view(
                page=page,
                on_refresh_callback=on_refresh_callback,
                feeding_detail_data=controller.get_feeding_detail_data()
            )
        )
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_edit":
        home_background, top_banner = dogdog.home_layout(
            page=page, text="제품 정보 변경"
        )
        main_container_content.append(top_banner)
        main_container_content.append(
            domains.feeding_add_edit.feeding_add_edit(page=page, view="edit")
        )
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_add":
        home_background, top_banner = dogdog.home_layout(page=page, text="제품 등록")
        main_container_content.append(top_banner)
        main_container_content.append(
            domains.feeding_add_edit.feeding_add_edit(page=page, view="add")
        )
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/notification":
        home_background, top_banner = dogdog.home_layout(page=page, text="알림")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(
            domains.notification.notification_dummy(page)
        )
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/notification_setting":
        home_background, top_banner = dogdog.home_layout(page=page, text="알림 설정")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(
            domains.notification.notification_setting(page)
        )
    # ---------------------------------------------------------------------------------------------------
    elif "/shop/" in content_page:
        home_background, top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.margin = None
        if "product/" in content_page:
            body_scroll_column.controls.append(
                domains.shop_product_detail.shop_product_detail(
                    page=page, popup=popup, content_page=content_page
                )
            )
    # ---------------------------------------------------------------------------------------------------
    return home_background, main_container_content
