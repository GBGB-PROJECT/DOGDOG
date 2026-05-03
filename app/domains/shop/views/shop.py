# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import asyncio
from domains.shop.controller.shop_controller import ShopController
# -------------------------------------------------------------------------------------------------------
def shop_feeding_guide(page: ft.Page):
    storage = page.session.store
    feeding_guide = ft.Column(
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=0,
        controls=[
            ft.Row(controls=[
                dogdog.basic_text(
                    value=f"{storage.get('customer_pet_name')}에게 딱 맞춘 하루 권장량",
                    size=18, weight="bold")]),
            ft.Row(margin=ft.margin.only(bottom=10), alignment=ft.MainAxisAlignment.END, controls=[ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0, controls=[
                ft.Container(scale=0.8,
                    width=25, height=25, ink=True, on_click=None, border_radius=25, bgcolor=ft.Colors.GREY_300,
                    content=ft.Icon(icon=ft.Icons.QUESTION_MARK, color=ft.Colors.WHITE, size=20)),
                    dogdog.basic_text("제품의 열량 4005kcal/kg", weight="bold", size=12, color=ft.Colors.GREY_600)
            ])]),
            ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.Image(src="speech_bubble.png", height=100, color="#FEF3B9"),
                dogdog.basic_text("40g", weight="bold", size=40),
            ], spacing=-90),
            ft.Image(src="dogbowl.png", height=100, margin=ft.margin.only(top=20)),
            dogdog.basic_text("아침 39g, 저녁 39g", weight="bold", color=ft.Colors.GREY_600),
            dogdog.basic_text("총 310kcal", weight="bold", color=ft.Colors.GREY_600)
    ])
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        content=feeding_guide # type: ignore
    )
# -------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------
def product_guide(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    for task in asyncio.all_tasks():
        if "shop_timesleep" in str(task.get_coro()): 
            print("\n" * 10 + f"{'===='*30}\n 🪄 Cancel Task Controls\n{'===='*30}")
            print(' ✅ domains.shop.controller.shop_controller.ShopController.shop_timesleep()')
            task.cancel()
    dogdog.task_controls()
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    guide_image_size = page.width / 4.4 # type: ignore
    product_image_size = page.width / 3.8 # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Guide Page View
    # ---------------------------------------------------------------------------------------------------    
    product_guide_tabs = ft.Tabs(
        length=4,
        content=ft.Row(height=guide_image_size*1.8, margin=ft.margin.only(top=5), spacing=0, controls=[
            ft.Container(
                width=17,
                alignment=ft.Alignment.CENTER,
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS,
                    icon_size=10,
                    style=ft.ButtonStyle(
                        padding=0,
                    ),
                    on_click=lambda e: ShopController.product_guide_page(product_guide_tabs, "back"),
                ),
            ),
            #
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
                alignment=ft.Alignment.CENTER,
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD_IOS,
                    icon_size=10,
                    style=ft.ButtonStyle(
                        padding=0,
                    ),
                    on_click=lambda e: ShopController.product_guide_page(product_guide_tabs, "forward"),
                ),
            ),
    ]))
    # ---------------------------------------------------------------------------------------------------
    # Product Filter Event
    # ---------------------------------------------------------------------------------------------------
    product_list = ft.Container(
        padding=10,
        content=ft.Column(
            controls=[
                ft.Container(
                    alignment=ft.Alignment.CENTER,
                    content=ft.ProgressRing()
                )
            ]
        )
    )

    def selected_filter(e):
        sort = None if e.data == "all" else e.data
        page.run_task(ShopController.load_products, page, product_list, product_image_size, sort)
    # ---------------------------------------------------------------------------------------------------
    # Product View
    # ---------------------------------------------------------------------------------------------------
    filter_list = [
        dogdog.dropdown_menu_option("전체", key="all"),
        dogdog.dropdown_menu_option("가격 높은순", key="price_desc"),
        dogdog.dropdown_menu_option("가격 낮은순", key="price_asc"),
        dogdog.dropdown_menu_option("무게 높은순", key="weight_desc"),
        dogdog.dropdown_menu_option("무게 낮은순", key="weight_asc"),
    ]
    product_filter = dogdog.dropdown_menu(label=None, event=selected_filter, options=filter_list)
    product_filter.value = "all"
    # ---------------------------------------------------------------------------------------------------
    # Shop Page Content
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Divider(),
        dogdog.basic_text("추천사료", size=18, weight="bold"),
        product_guide_tabs,
        ft.Divider(),
        dogdog.basic_text("전체 상품", size=16, weight="bold"),
        product_filter,
        product_list
    ]
    # ---------------------------------------------------------------------------------------------------
    # Background Guide Product Task
    # ---------------------------------------------------------------------------------------------------
    asyncio.create_task(ShopController.shop_timesleep(product_guide_tabs))
    # ---------------------------------------------------------------------------------------------------
    page.run_task(ShopController.load_products, page, product_list, product_image_size)
    page.run_task(ShopController.load_recommended_foods, page, product_guide_tabs, guide_image_size)
    
    return ft.Container(
        padding=ft.Padding.only(left=10, right=10),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column) # type: ignore
    )