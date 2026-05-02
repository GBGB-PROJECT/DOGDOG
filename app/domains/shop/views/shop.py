# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
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
    # from api.product_guide import Product
    from domains.shop.controller.shop_api import get_shop_product_list, get_recommended_foods
    import asyncio
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    guide_image_size = page.width / 3.8 # type: ignore
    product_image_size = page.width / 3.8 # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Guide Page Arrow Event
    # ---------------------------------------------------------------------------------------------------
    def product_guide_page(key, e=None):
        view_page_index = product_guide.selected_index
        if key == "forward":
            if product_guide.selected_index == product_guide.length - 1:
                product_guide.selected_index = 0
            else: product_guide.selected_index = view_page_index + 1
        elif key == "back":
            if product_guide.selected_index == 0: 
                product_guide.selected_index = product_guide.length - 1
            else: product_guide.selected_index = view_page_index - 1
        # print(product_guide.selected_index)
        product_guide.update()
    # ---------------------------------------------------------------------------------------------------
    # Guide Page View
    # ---------------------------------------------------------------------------------------------------    
    product_guide = ft.Tabs(
        length=4,
        content=ft.Row(height=guide_image_size*1.5, margin=ft.margin.only(top=5), spacing=0, controls=[
            ft.Container(
                width=25,
                alignment=ft.Alignment.CENTER,
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS,
                    icon_size=10,
                    style=ft.ButtonStyle(
                        padding=0,
                    ),
                    on_click=lambda e: product_guide_page(e=e, key="back"),
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
                width=25,
                alignment=ft.Alignment.CENTER,
                content=ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD_IOS,
                    icon_size=10,
                    style=ft.ButtonStyle(
                        padding=0,
                    ),
                    on_click=lambda e: product_guide_page(e=e, key="forward"),
                ),
            ),
    ]))
    async def load_recommended_foods():
        storage = page.session.store
        pet_id = pet_id = (
                storage.get("pet_id")
                or storage.get("customer_pet_id")
                or storage.get("current_pet_id")
            )

        if not pet_id:
            product_guide.content.controls[1].controls = [
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text(
                            "반려견 정보를 찾을 수 없습니다.",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ]
                )
            ]
            product_guide.length = 1
            product_guide.update()
            return

        foods = await get_recommended_foods(page, int(pet_id))

        if not foods:
            product_guide.content.controls[1].controls = [
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text(
                            "추천사료가 없습니다.",
                            size=12,
                            color=ft.Colors.GREY_500
                        )
                    ]
                )
            ]
            product_guide.length = 1
            product_guide.update()
            return

        recommended_views = dogdog.products(
            page,
            foods,
            guide_image_size
        )

        product_guide.content.controls[1].controls = recommended_views
        product_guide.length = len(recommended_views)
        product_guide.selected_index = 0
        product_guide.update()
    # ---------------------------------------------------------------------------------------------------
    # Product Filter Event
    # ---------------------------------------------------------------------------------------------------
    #default_view = dogdog.products(page, Product.guide_product_list_t, product_image_size)
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


    async def load_products(sort=None):
        products = await get_shop_product_list(page, sort=sort)

        if not products:
            product_list.content = ft.Column(
                controls=[
                    dogdog.basic_text(
                        "상품이 없습니다.",
                        size=14,
                        color=ft.Colors.GREY_500
                    )
                ]
            )
        else:
            print("상품 리스트 출력")
            product_list.content = ft.Column(
                controls=dogdog.products(
                    page,
                    products,
                    product_image_size
                )
            )

        product_list.update()


    def selected_filter(e):
        sort = None if e.data == "all" else e.data
        page.run_task(load_products, sort)
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
    # product_list = ft.Container(
    #     padding=10,
    #     content=ft.Column(default_view))
    # ---------------------------------------------------------------------------------------------------
    # Shop Page Content
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Divider(),
        dogdog.basic_text("추천사료", size=18, weight="bold"),
        product_guide,
        ft.Divider(),
        dogdog.basic_text("전체 상품", size=16, weight="bold"),
        product_filter,
        product_list
    ]
    # ---------------------------------------------------------------------------------------------------
    # Background Guide Page Event
    # ---------------------------------------------------------------------------------------------------
    async def timesleep():
        try:
            for i in range(999):
                await asyncio.sleep(5)
                product_guide_page("forward")
        except: pass
    page.run_task(timesleep)
    # ---------------------------------------------------------------------------------------------------
    page.run_task(load_products)
    page.run_task(load_recommended_foods)
    return ft.Container(
        padding=ft.Padding.only(left=10, right=10),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column) # type: ignore
    )