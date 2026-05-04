# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import asyncio
from domains.shop.controller.shop_controller import ShopController
# -------------------------------------------------------------------------------------------------------
def shop_feeding_guide(page: ft.Page):
    storage = page.session.store
    pet_id = (
        storage.get("pet_id")
        or storage.get("customer_pet_id")
        or storage.get("current_pet_id")
    )
    
    # 초기 상태: 로딩 인디케이터 (ProgressRing)
    main_container = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[ft.ProgressRing(color=ft.Colors.AMBER_400)]
        ),
        padding=ft.padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        height=380 # UI 높이 확보
    )

    async def load_guide_data():
        if not pet_id:
            main_container.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[dogdog.basic_text("반려견 정보를 찾을 수 없습니다.", color=ft.Colors.GREY_400)]
            )
            main_container.update()
            return

        # ShopController를 통해 가공된 데이터 로드
        data = await ShopController.get_feeding_data(page, pet_id)
        
        if data:
            # UI 바인딩 및 교체
            main_container.content = ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                controls=[
                    # 상단: 반려견 맞춤 제목
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            dogdog.basic_text(
                                value=f"{data['pet_name']}에게 딱 맞춘 하루 권장량",
                                size=18, weight="bold"
                            )
                        ]
                    ),
                    # 제품 정보 (열량)
                    ft.Row(
                        margin=ft.margin.only(bottom=10, top=10), 
                        alignment=ft.MainAxisAlignment.END, 
                        controls=[
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.END, 
                                spacing=0, 
                                controls=[
                                    ft.Row([
                                        # ft.Container(
                                        #     scale=0.8,
                                        #     width=20, height=20, border_radius=20, 
                                        #     bgcolor=ft.Colors.GREY_300,
                                        #     content=ft.Icon(icon=ft.Icons.QUESTION_MARK, color=ft.Colors.WHITE, size=14)
                                        # ),
                                        dogdog.basic_text(f"제품의 열량 {data['kcal_per_kg']}kcal/kg", weight="bold", size=11, color=ft.Colors.GREY_600)
                                    ], spacing=5)
                                ]
                            )
                        ]
                    ),
                    # 중앙: 말풍선 이미지 + 권장량 텍스트
                    ft.Stack(
                        controls=[
                            ft.Image(src="speech_bubble.png", height=120, color="#FEF3B9"),
                            ft.Container(
                                content=dogdog.basic_text(f"{data['daily_food_g']}g", weight="bold", size=42),
                                padding=ft.padding.only(bottom=15),
                                alignment=ft.Alignment(0, 0)
                            )
                        ],
                        alignment=ft.Alignment(0, 0) 
                    ),
                    # 하단: 밥그릇 이미지 + 배차 정보
                    ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=5,
                        controls=[
                            ft.Image(src="dogbowl.png", height=100, margin=ft.margin.only(top=10)),
                            dogdog.basic_text(data["schedule"], weight="bold", size=15, color=ft.Colors.GREY_700),
                            # 통계: 하루 총 칼로리
                            ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    #ft.Icon(ft.Icons.BOLT, color=ft.Colors.AMBER, size=18),
                                    dogdog.basic_text(f"총 {data['total_kcal']}kcal", weight="bold", size=15, color=ft.Colors.GREY_600),
                                ]
                            )
                        ]
                    )
                ]
            )
        else:
            main_container.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[dogdog.basic_text("데이터 로드 실패", color=ft.Colors.GREY_400)]
            )
        
        main_container.update()

    # 데이터 로드 태스크 실행
    page.run_task(load_guide_data)
    
    return main_container

# -------------------------------------------------------------------------------------------------------
def product_guide(page: ft.Page):
    # 기존 백그라운드 태스크 정리
    for task in asyncio.all_tasks():
        if "shop_timesleep" in str(task.get_coro()): 
            task.cancel()
    dogdog.task_controls()

    guide_image_size = page.width / 4.4 # type: ignore
    product_image_size = page.width / 3.8 # type: ignore

    # Flet 0.81.0 준수 사항: Tabs 컨텐츠 구성
    product_guide_tabs = ft.Tabs(
        length=4,
        content=ft.Row(height=guide_image_size*1.8, margin=ft.margin.only(top=5), spacing=0, controls=[
            ft.Container(
                width=17,
                alignment=ft.Alignment(0, 0),
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS,
                    icon_size=10,
                    on_click=lambda e: ShopController.product_guide_page(product_guide_tabs, "back"),
                ),
            ),
            ft.TabBarView(
                expand=True,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[ft.ProgressRing()]
                    )
                ]
            ),
            ft.Container(
                width=17,
                alignment=ft.Alignment(0, 0),
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD_IOS,
                    icon_size=10,
                    on_click=lambda e: ShopController.product_guide_page(product_guide_tabs, "forward"),
                ),
            ),
    ]))

    product_list = ft.Container(
        padding=10,
        content=ft.Column(controls=[ft.Container(alignment=ft.Alignment(0, 0), content=ft.ProgressRing())])
    )

    def selected_filter(e):
        sort = None if e.data == "all" else e.data
        page.run_task(ShopController.load_products, page, product_list, product_image_size, sort)

    filter_list = [
        dogdog.dropdown_menu_option("전체", key="all"),
        dogdog.dropdown_menu_option("가격 높은순", key="price_desc"),
        dogdog.dropdown_menu_option("가격 낮은순", key="price_asc"),
        dogdog.dropdown_menu_option("무게 높은순", key="weight_desc"),
        dogdog.dropdown_menu_option("무게 낮은순", key="weight_asc"),
    ]
    product_filter = dogdog.dropdown_menu(label=None, event=selected_filter, options=filter_list)
    product_filter.value = "all"

    content_column = [
        #shop_feeding_guide(page), # 상단 권장 급여량 섹션 추가
        #ft.Divider(),
        dogdog.basic_text("추천사료", size=18, weight="bold"),
        product_guide_tabs,
        ft.Divider(),
        dogdog.basic_text("전체 상품", size=16, weight="bold"),
        product_filter,
        product_list
    ]

    # 태스크 시작
    asyncio.create_task(ShopController.shop_timesleep(product_guide_tabs))
    page.run_task(ShopController.load_products, page, product_list, product_image_size)
    page.run_task(ShopController.load_recommended_foods, page, product_guide_tabs, guide_image_size)
    
    return ft.Container(
        padding=ft.Padding.only(left=10, right=10),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column, scroll=ft.ScrollMode.AUTO) # type: ignore
    )