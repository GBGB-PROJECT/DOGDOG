# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains as domains
import components as dogdog
import domains
from .home.controller.home_controller import HomeController
from domains.logs.controller.log_controller import LogController


# -------------------------------------------------------------------------------------------------------
async def home_tile(
    page: ft.Page,
    popup,
    content_page: str,
    change_page_callback=None,
    on_refresh_callback=None,
):
    # ---------------------------------------------------------------------------------------------------
    # [지침 1] home_tile 진입부 '강제 청소' (유령 팝업 원천 차단)
    # ---------------------------------------------------------------------------------------------------
    page.overlay.clear()
    page.dialog = None
    page.update()

    # ---------------------------------------------------------------------------------------------------
    # Controller Init & PubSub
    # ---------------------------------------------------------------------------------------------------
    controller = HomeController(page)

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
    if content_page == "/home":
        # [수정 1] 들여쓰기 교정 및 라우트 진입 시 강제 청소
        page.overlay.clear()
        page.dialog = None
        page.update()

        # [ISSUE] 부분 업데이트 시 UI 레이스 컨디션 및 하얀 화면 발생 (2026-05-05)
        # [TODO] 향후 PubSub 기반의 부분 업데이트 로직으로 고도화 필요. 현재는 안정성을 위해 홈 직행 리셋 방식 사용.
        # needs_refresh = page.session.store.get('needs_refresh')
        # if needs_refresh:
        #     pet_id = page.session.store.get("current_pet_id")
        #     if pet_id:
        #         print(f"👉 [Home] 대시보드 갱신 예약 감지. Zero-Base 재건축 시작.")
        #         
        #         # [수정 2] 기존 객체 완전 삭제 및 재건축 (문지기 로직)
        #         body_column.controls.clear()
        #         body_scroll_column.controls.clear()
        #         main_container_content.clear()
        #         
        #         # 데이터 강제 재요청
        #         await controller.fetch_dashboard_data(pet_id)
        #         
        #         # 세션 정합성 재검증
        #         customer_detail = page.session.store.get("customer_detail")
        #         if not customer_detail or "dashboard_sync" not in customer_detail:
        #             await controller.fetch_dashboard_data(pet_id)
        #
        #         page.session.store.set('needs_refresh', False)
        #         # 이제 아래 로직에서 최신 데이터를 주입받은 새 위젯들이 append 됨

        home_background , top_banner = dogdog.home_layout(page=page, view="home")
        main_container_content.append(top_banner)
        main_container_content.append(body_column)
        # -----------------------------------------------------------------------------------------------
        async def on_timeline_click(e):
            # [해결 1] 상세 페이지 이동 전 세션 청소 및 초기화
            import datetime
            page.session.store.set("select_log_week", None)# 주간 뷰 잔상 제거
            page.session.store.set("select_log_date", datetime.datetime.now().strftime("%Y.%m.%d")) # 오늘 날짜 강제
            
            pet_id = page.session.store.get("current_pet_id")
            if pet_id:
                logs = await controller.get_today_timeline_logs(pet_id)
                # 추출된 유틸리티 함수를 호출하여 팝업을 띄우고 데이터 주입
                domains.home_view.open_now_history_popup(page, popup, logs)
        body_column.controls.append(
            domains.home_view.now_history(
                page=page, 
                popup=popup, 
                stats_data=controller.get_today_record_stats(),
                history_logs=controller.get_formatted_history(count=3),
                on_click=on_timeline_click
            )
        )
        body_column.expand = False
        body_column.margin = None
        # -----------------------------------------------------------------------------------------------
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home_view.feeding_food_count(
                    page=page, 
                    content_page=content_page,
                    inventory_stats=controller.get_food_inventory_stats()
                ),
                on_click=lambda e: appbar_on_change(e, "/feeding"),
            )
        )
        body_scroll_column.controls.append(
            domains.grid_view.status_update_menu(page=page, popup=popup)
        )

        # -----------------------------------------------------------------------------------------------
        # PubSub: 대시보드 동기화 이벤트 구독 및 컴포넌트 부분 업데이트
        # -----------------------------------------------------------------------------------------------
        async def refresh_dashboard_task(msg):
            if msg == "update_dashboard" and content_page == "/home":
                pet_id = page.session.store.get("current_pet_id")
                if pet_id:
                    # 전체 대시보드 데이터 다시 패치 (가장 중요)
                    await controller.fetch_dashboard_data(pet_id)
                    
                    # 1. 상단 '오늘의 기록' 컴포넌트 전체 교체
                    body_column.controls.clear()
                    body_column.controls.append(
                        domains.home_view.now_history(
                            page=page, 
                            popup=popup, 
                            stats_data=controller.get_today_record_stats(),
                            history_logs=controller.get_formatted_history(count=3),
                            on_click=on_timeline_click
                        )
                    )
                    body_column.update()
                        
                    # 2. 하단 '사료 잔여량' 및 메뉴 전체 교체
                    body_scroll_column.controls.clear()
                    body_scroll_column.controls.append(
                        dogdog.content_container(
                            content_list=domains.home_view.feeding_food_count(
                                page=page, 
                                content_page=content_page,
                                inventory_stats=controller.get_food_inventory_stats()
                            ),
                            on_click=lambda e: appbar_on_change(e, "/feeding"),
                        )
                    )
                    body_scroll_column.controls.append(
                        domains.grid_view.status_update_menu(page=page, popup=popup)
                    )
                    body_scroll_column.update()

        # [보정] 기존 구독된 함수가 있다면 제거하여 중복 실행 방지
        page.pubsub.unsubscribe_all()
        page.pubsub.subscribe(lambda msg: page.run_task(refresh_dashboard_task, msg))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/log":
        home_background , top_banner = dogdog.home_layout(page=page, text="Log")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        
        # LogController 생성 및 주입
        log_ctrl = LogController(page)
        body_scroll_column.controls = domains.log.log_view(page, controller=log_ctrl)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/shop":
        home_background , top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.shop.shop_feeding_guide(page=page))
        body_scroll_column.controls.append(
            dogdog.content_container(
                content_list=domains.home_view.feeding_food_count(
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
        home_background , top_banner = dogdog.home_layout(page=page, text="Contents")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        body_scroll_column.controls.append(domains.dummy_view(page=page))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/mypage":
        home_background , top_banner = dogdog.home_layout(page=page, text="My Page")
        main_container_content.append(top_banner)
        main_container_content.append(body_scroll_column)
        from domains.mypage.controller.mypage_controller import MypageController
        mypage_ctrl = MypageController(page)
        body_scroll_column.controls = domains.mypage_view.mypage_view(page, controller=mypage_ctrl)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/history":
        # [해결] 3단 동적 헤더 타이틀 설정
        storage = page.session.store
        if storage.get("select_log_week"):
            header_title = "일주일 상세 기록"
        elif storage.get("select_log_date"):
            header_title = "일일 기록"
        else:
            header_title = "오늘의 기록"
        
        home_background , top_banner = dogdog.home_layout(page=page, text=header_title)
        main_container_content.append(top_banner)
        
        history_container = ft.Column(expand=True, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        history_container.controls.append(ft.ProgressRing(color=ft.Colors.YELLOW_600)) # 로딩 표시
        main_container_content.append(history_container)
        
        async def load_history_data():
            from domains.logs.controller.history_controller import HistoryController
            history_ctrl = HistoryController(page)
            pet_id = page.session.store.get("current_pet_id")
            
            # [Step 3] 최신 데이터를 가져와서 UI를 재렌더링하는 콜백 함수 정의
            async def refresh_history_list():
                if pet_id:
                    # 1. API(get_timeline_logs)를 호출해 최신 데이터를 다시 가져옴
                    logs = await history_ctrl.get_timeline_logs(pet_id)
                    filtered_logs, date_str = history_ctrl.get_filtered_logs_and_date_str(logs)
                    
                    # 2. history_view를 다시 실행해 UI 컴포넌트를 새로 생성
                    history_ui = domains.history.history_view(page, filtered_logs, date_str, controller=history_ctrl)
                    
                    # 3. 부모 컨테이너(history_container)를 새 UI로 교체
                    # [Step 3 해결] 단순히 리스트를 교체하는 대신 clear()와 append()를 사용하여 확실하게 갱신
                    history_container.controls.clear()
                    history_container.controls.append(history_ui)
                    history_container.update()
                    # (선택사항) 전체 페이지 업데이트가 필요한 경우
                    # page.update() 

            # 컨트롤러에 콜백 주입
            history_ctrl.on_refresh_callback = refresh_history_list
            
            # 초기 데이터 로드 실행
            await refresh_history_list()
            
        page.run_task(load_history_data)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding":
        home_background , top_banner = dogdog.home_layout(page=page, text="급여 중인 상품")
        main_container_content.append(top_banner)
        
        # [수정] 데이터 갱신 시 전체 교체를 위해 래퍼 컨테이너 생성
        feeding_container = ft.Container(
            expand=True,
            content=domains.feeding_view.feeding_tabs_view(
                page=page,
                on_refresh_callback=on_refresh_callback,
                feeding_detail_data=await controller.get_feeding_detail_data()
            )
        )
        main_container_content.append(feeding_container)

        # [신규 추가] PubSub: 급여 목록 동기화 이벤트 구독 및 컴포넌트 부분 업데이트
        async def refresh_feeding_list_task(msg):
            if msg == "refresh_feeding_list" and content_page == "/feeding":
                feeding_container.content = domains.feeding_view.feeding_tabs_view(
                    page=page,
                    on_refresh_callback=on_refresh_callback,
                    feeding_detail_data=await controller.get_feeding_detail_data()
                )
                feeding_container.update()

        # [보정] 기존 구독된 함수가 있다면 제거하여 중복 실행 방지
        page.pubsub.unsubscribe_all()
        page.pubsub.subscribe(lambda msg: page.run_task(refresh_feeding_list_task, msg))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_edit":
        home_background , top_banner = dogdog.home_layout(page=page, text="급여 상품 정보 변경")
        main_container_content.append(top_banner)
        main_container_content.append(domains.feeding_add_edit.feeding_add_edit(page=page, view="edit"))
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/feeding_add":
        home_background , top_banner = dogdog.home_layout(page=page, text="급여 상품 신규 등록")
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

        from domains.mypage.controller.subs_notification_api import NotificationController
        from domains.shop.controller.shop_subscription_api import get_subscription_status

        settings = await NotificationController(page).get_settings()

        subscription_status = await get_subscription_status(page)
        is_subscribed = bool(
            subscription_status and subscription_status.get("is_subscribed")
        )

        body_scroll_column.controls.append(
            domains.notification.notification_setting(
                page=page,
                popup=popup,
                settings=settings,
                is_subscribed=is_subscribed,
            )
        )
    # ---------------------------------------------------------------------------------------------------
    elif "/shop/" in content_page:
        shop_content_page = content_page.replace("/shop","")
        # print(shop_content_page)
        home_background , top_banner = dogdog.home_layout(page=page, text="개밥개밥푸드")
        main_container_content.append(top_banner)
        # -----------------------------------------------------------------------------------------------
        if "product/" in shop_content_page:
            main_container_content.append(dogdog.shop_top(page=page, content_page=content_page))
            body_scroll_column.controls.append(domains.shop_product_detail.shop_product_detail(
                page=page, popup=popup, content_page=content_page))
        # -----------------------------------------------------------------------------------------------
        # elif shop_content_page == "/search":
        #     body_scroll_column.controls.append(ft.Container(
        #         padding=ft.Padding.only(left=20, right=20, top=20),
        #         bgcolor="#ffffff",
        #         content=ft.Column(
        #             controls=[dogdog.basic_text("상품 검색 더미 페이지")]
        #         )
        #     ))
        elif shop_content_page == "/search":
            body_scroll_column.controls.append(domains.search.search_products(page=page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/cart":
            main_container_content.append(
                dogdog.shop_top(page=page, text="장바구니", content_page=content_page))
            body_scroll_column.controls.append(domains.dummy_view(page=page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/wishlist":
            main_container_content.append(
                dogdog.shop_top(page=page, text="위시리스트", content_page=content_page))
            body_scroll_column.controls.append(domains.dummy_view(page=page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/product_order":
            main_container_content.append(
                dogdog.shop_top(page=page, text="주문 / 결제", content_page=content_page))
            body_scroll_column.controls.append(
                domains.shop_orders.order_view(page=page, popup=popup, page_name=content_page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/order_success":
            main_container_content.append(
                dogdog.shop_top(page=page, text="주문 / 결제", content_page=content_page))
            body_column.controls.append(
                domains.success_layout.order_success(page=page, page_name=content_page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/subs_start":
            main_container_content.append(
                dogdog.shop_top(page=page, text="똑똑 배송 시작하기", content_page=content_page))
            body_scroll_column.controls.append(domains.subs_start.subs_options(page=page, popup=popup))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/subs_product_order":
            main_container_content.append(
                dogdog.shop_top(page=page, text="똑똑 배송 / 자동결제 등록", content_page=content_page))
            body_scroll_column.controls.append(
                domains.shop_orders.order_view(page=page, popup=popup, page_name=content_page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/subs_order_success":
            main_container_content.append(
                dogdog.shop_top(page=page, text="똑똑 배송 / 자동결제 등록", content_page=content_page))
            body_column.controls.append(
                domains.success_layout.order_success(page=page, page_name=content_page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/address":
            main_container_content.append(
                dogdog.shop_top(page=page, text="주소 검색", content_page=content_page))
            body_scroll_column.controls.append(domains.address_view(page=page))
        # -----------------------------------------------------------------------------------------------
        elif shop_content_page == "/pay_list":
            import json

            main_container_content.append(
                dogdog.shop_top(page=page, text="주문 내역", content_page=content_page)
            )

            subscription_json_text = ft.Text(
                value="구독 내역을 불러오는 중입니다...",
                selectable=True,
                size=12,
                font_family="Consolas",
                color=ft.Colors.GREY_800,
            )

            body_scroll_column.controls.append(
                ft.Container(
                    padding=ft.Padding.only(left=20, right=20, top=20),
                    bgcolor="#ffffff",
                    content=ft.Column(
                        controls=[
                            dogdog.basic_text("구독 내역 조회 결과", size=16, weight="bold"),
                            ft.Container(
                                padding=10,
                                bgcolor=ft.Colors.GREY_100,
                                border_radius=8,
                                content=subscription_json_text,
                            ),
                        ]
                    ),
                )
            ) 

            async def load_subscription_json():
                from domains.shop.controller.shop_subscription_api import get_subscription_status

                result = await get_subscription_status(page)

                if result is None:
                    subscription_json_text.value = "구독 내역 조회 실패"
                else:
                    subscription_json_text.value = json.dumps(
                        result,
                        ensure_ascii=False,
                        indent=2,
                        default=str,
                    )

                page.update()

            page.run_task(load_subscription_json)

        # -----------------------------------------------------------------------------------------------
        main_container_content.append(ft.Divider(height=1))
        main_container_content.append(
            body_scroll_column if not "success" in shop_content_page else body_column)
        body_scroll_column.margin = None
    # ---------------------------------------------------------------------------------------------------
    return home_background , main_container_content