# # -------------------------------------------------------------------------------------------------------
# import flet as ft
# import domains as domains
# import components as dogdog
# import datetime
# from .home_controller import HomeController  # 같은 폴더의 컨트롤러를 가져옵니다.

# # -------------------------------------------------------------------------------------------------------
# async def home_tile(
#     page: ft.Page,
#     popup,
#     content_page: str,
#     change_page_callback=None,
#     on_refresh_callback=None,
# ):
#     """
#     [View] home_tile
#     역할: 홈 도메인의 화면 구성을 담당합니다.
#     - 직접 데이터를 가공하지 않고, HomeController에게 필요한 데이터를 요청(View 정제)합니다.
#     - 컨트롤러가 준 데이터를 기반으로 Flet 위젯들을 조립하여 화면을 그립니다.
#     """
    
#     # 1. 컨트롤러 초기화 (의존성 주입: 컨트롤러가 페이지 기능을 쓸 수 있게 연결)
#     controller = HomeController(page)
    
#     # 2. 데이터 가져오기 (Controller 호출)
#     # View는 "어떤 데이터가 필요해"라고 말하기만 하고, "어떻게 가져오고 가공할지"는 몰라도 됩니다.
#     pet_list = await controller.fetch_pets_data()

#     # ---------------------------------------------------------------------------------------------------
#     # 레이아웃 뼈대 설정
#     # ---------------------------------------------------------------------------------------------------
#     main_container_content = []
#     body_column = ft.Column(spacing=15, expand=True, margin=ft.margin.only(bottom=20))
#     body_scroll_column = ft.Column(
#         spacing=15, expand=True, scroll=ft.ScrollMode.HIDDEN, margin=ft.margin.only(bottom=20)
#     )
    
#     # 상단 공통 레이아웃 생성 시 가져온 pet_list를 전달합니다.
#     home_background, top_banner = dogdog.home_layout(page=page, view="feeding", pet_list=pet_list)

#     def appbar_on_change(e, on_change_page):
#         if change_page_callback:
#             change_page_callback(on_change_page)

#     popup = dogdog.Popup(page=page)

#     def history_event(e):
#         popup.show_popup_close(e)
#         appbar_on_change(e, "/history")

#     # [수정] 콜백 함수를 상위 스코프로 이동하여 모든 조건부 블록에서 접근 가능하게 함
#     async def local_refresh_callback():
#         print("🔥 [DEBUG] 새로고침 콜백 실행됨!")
#         pet_id = page.session.store.get("pet_id")
#         if not pet_id:
#             print("⚠️ [DEBUG] pet_id가 없어 새로고침을 중단합니다.")
#             return
        
#         # 1. 데이터 리패치 (Controller를 통해 세션 업데이트)
#         print(f"🔄 [DEBUG] 데이터 리패치 시도 (Pet ID: {pet_id})")
#         await controller.fetch_dashboard_data(pet_id)
        
#         # 2. 부모(main.py)의 콜백이 있다면 실행 (라우팅 포함)
#         if on_refresh_callback:
#             print("🚀 [DEBUG] 부모 refresh_home_data 호출")
#             await on_refresh_callback()
#         else:
#             # 부모 콜백이 없을 경우를 대비한 자체 강제 렌더링 (단, 홈 화면일 때만 유효함)
#             print("♻️ [DEBUG] 자체 UI 강제 재렌더링 시도")
#             if content_page == "/home":
#                 try:
#                     history_card.content.controls = domains.home.now_history(
#                         page=page, 
#                         popup=popup,
#                         stats_data=controller.get_today_record_stats(),
#                         history_logs=controller.get_formatted_history(count=3)
#                     )
#                     inventory_card.content.controls = domains.home.feeding_food_count(
#                         page=page, 
#                         content_page="/home",
#                         inventory_stats=controller.get_food_inventory_stats()
#                     )
#                     history_card.update()
#                     inventory_card.update()
#                 except Exception as e:
#                     print(f"⚠️ [DEBUG] UI 업데이트 중 에러 (무시됨): {e}")
        
#         print("✅ [DEBUG] 대시보드 새로고침 완료")

#     # ---------------------------------------------------------------------------------------------------
#     # 페이지별 컨텐츠 구성
#     # ---------------------------------------------------------------------------------------------------
#     if content_page == "/home":
#         # 홈 메인 화면 구성
#         home_background, top_banner = dogdog.home_layout(page=page, view="home", pet_list=pet_list)
#         main_container_content.append(top_banner)
#         # 홈 화면 전용 컬럼들은 아래에서 조건부로 채워진 뒤 append 됩니다.
        
#         # '오늘의 기록' 섹션 (데이터 가공은 컨트롤러가 수행)
#         now_history = popup.bottom_sheet_popup
#         now_history_content = now_history.content.content.controls # type: ignore
#         now_history_content.clear()
        
#         now_date = datetime.datetime.now().strftime("%Y-%m-%d")
#         now_history_content.append(dogdog.basic_text(f"오늘의 기록 : {now_date}", size=18, weight="bold"))
#         now_history_content.append(ft.Divider())
        
#         # 컨트롤러에서 가공된 기록 데이터를 받아옵니다.
#         history_logs = controller.get_formatted_history(count=3)
        
#         for log in history_logs:
#             case = ft.Container(
#                 padding=ft.Padding.only(right=10, left=10),
#                 width=3000, height=50, border_radius=10,
#                 border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
#                 content=ft.Row(
#                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
#                     controls=[
#                         dogdog.basic_text(log["message"], size=14, color=ft.Colors.GREY_700),
#                         dogdog.basic_text(log["time"], size=14, color=ft.Colors.GREY_700)
#                     ]
#                 )
#             )
#             now_history_content.append(case)
            
#         now_history_content.append(ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
#             ft.TextButton(
#                 content=dogdog.basic_text("더보기", size=14, color=ft.Colors.GREY_500), 
#                 on_click=lambda e: history_event(e)
#             )
#         ]))
        
#         # 오늘의 기록 (칼로리 & 활동 요약) 카드
#         history_card = dogdog.content_container(
#             content_list=domains.home.now_history(
#                 page=page, 
#                 popup=popup,
#                 stats_data=controller.get_today_record_stats(),
#                 history_logs=history_logs
#             ),
#             on_click=lambda e: popup.show_popup_open(e, "bottom_sheet")
#         )
#         body_column.controls.append(history_card)
#         body_column.expand = False

#         # 사료 잔여량 게이지 카드
#         inventory_card = dogdog.content_container(
#             content_list=domains.home.feeding_food_count(
#                 page=page, 
#                 content_page="/home",
#                 inventory_stats=controller.get_food_inventory_stats()
#             ),
#             on_click=lambda e: appbar_on_change(e, "/feeding")
#         )
#         body_scroll_column.controls.append(inventory_card)

#         # 상태 업데이트 메뉴 (밥주기 버튼 등)
#         body_scroll_column.controls.append(
#             domains.grid.status_update_menu(
#                 page=page, 
#                 popup=popup, 
#                 on_refresh_callback=local_refresh_callback
#             )
#         )
#         # 메인 컨테이너에 추가 (홈 화면 전용)
#         main_container_content.append(body_column)
#         main_container_content.append(body_scroll_column)

#     # [참고] 다른 페이지들(log, shop 등)도 동일하게 home_layout을 사용하여 렌더링됩니다.
#     elif content_page in ["/log", "/shop", "/contents", "/mypage", "/history", "/notification"]:
#         title_map = {
#             "/log": "Log", "/shop": "Shop Test", "/contents": "Content",
#             "/mypage": "My Page", "/history": "오늘의 기록", "/notification": "알림"
#         }
#         home_background, top_banner = dogdog.home_layout(page=page, text=title_map.get(content_page))
#         main_container_content.append(top_banner)

#     elif content_page == "/feeding":
#         home_background, top_banner = dogdog.home_layout(
#             page=page, text="급여 중인 제품", back_event=lambda _: page.go("/home")
#         )
#         main_container_content.append(top_banner)
#         main_container_content.append(
#             domains.feeding.feeding_tabs_view(
#                 page=page, 
#                 on_refresh_callback=local_refresh_callback,
#                 feeding_detail_data=controller.get_feeding_detail_data()
#             )
#         )

#     elif content_page == "/feeding_edit":
#         # 상세 페이지는 홈의 body_scroll_column을 공유하지 않고 독립적으로 구성
#         home_background, top_banner = dogdog.home_layout(
#             page=page, text="제품 정보 변경", back_event=lambda _: page.go("/home")
#         )
#         main_container_content.append(top_banner)
#         main_container_content.append(domains.feeding_add_edit.feeding_add_edit(page=page, view="edit"))

#     elif content_page == "/feeding_add":
#         # 상세 페이지는 홈의 body_scroll_column을 공유하지 않고 독립적으로 구성
#         home_background, top_banner = dogdog.home_layout(
#             page=page, text="제품 등록", back_event=lambda _: page.go("/home")
#         )
#         main_container_content.append(top_banner)
#         main_container_content.append(domains.feeding_add_edit.feeding_add_edit(page=page, view="add"))

#     elif content_page in ["/what_bowel_score", "/what_bcs"]:
#         title = "배변 스코어란?" if content_page == "/what_bowel_score" else "BCS 란?"
#         home_background, top_banner = dogdog.home_layout(page=page, text=title)
#         main_container_content.append(top_banner)
#         main_container_content.append(body_scroll_column)
#         body_scroll_column.margin = ft.margin.only(top=20, bottom=20)
#         body_scroll_column.controls.append(domains.guide.what_guide(page=page, content=content_page))

#     print("on_refresh_callback : ", on_refresh_callback)
#     return home_background, main_container_content
