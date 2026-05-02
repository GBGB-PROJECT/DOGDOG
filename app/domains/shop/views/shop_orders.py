# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import asyncio
# -------------------------------------------------------------------------------------------------------
def order_view(page: ft.Page, popup, page_name):
    # ---------------------------------------------------------------------------------------------------
    from api.product_guide import Product
    def payment_check(e):
        page.go("/shop/subs_order_success") if "/subs_product_order" in page_name else page.go("/shop/order_success") 
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    if (not storage.get("select_product_id") and 
        not storage.get("select_product_quantity") and
        not ("/subs_order" in page_name and storage.get("select_subs"))):
        return ft.Container(
            padding=ft.padding.only(left=10, right=10, top=10, bottom=20),
            bgcolor="#ffffff",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    dogdog.basic_text("정상적이지 않은 접근입니다.")
        ]))
    product_id = int(storage.get("select_product_id")) # type: ignore
    product_quantity = int(storage.get("select_product_quantity")) # type: ignore
    # for p_id , p_d in Product.guide_product_list.items():
    #     if p_id == product_id:
    #         p_brand = str(p_d.get('brand'))
    #         p_name = str(p_d.get('product_name'))
    #         p_price = int(p_d.get('sales_price')) # type: ignore
    #         break
    from domains.shop.controller.shop_api import get_shop_product_detail

    # product = get_shop_product_detail(page, product_id)

    # p_brand = product.get("brand") or ""
    # p_name = product.get("product_name") or ""
    # p_price = int(product.get("retail_price") or 0)
    p_brand = ""
    p_name = ""
    p_price = 0

    product_name_text = ft.Text(
        "상품 정보를 불러오는 중...",
        font_family="Pretendard",
        expand=4,
        overflow=ft.TextOverflow.ELLIPSIS,
        text_align=ft.TextAlign.RIGHT
    )

    product_price_text = dogdog.basic_text("0원")
    subs_sale_price_text = dogdog.basic_text("0원", color="#E6001A")
    total_price_text = dogdog.basic_text("0원")

    # ---------------------------------------------------------------------------------------------------
    order_price = p_price * product_quantity
    sale_order_price = order_price*0.1 if "/subs_order" in page_name else 0
    final_price = order_price - sale_order_price
    view_sale_order_price = int(final_price) - int(order_price)
    # ---------------------------------------------------------------------------------------------------
    order_customer_name = dogdog.input_textfield(
        hint_text="최대 10자로 작성해주세요", cancel_event=True)
    order_customer_phone = dogdog.input_textfield(
        hint_text="010-0000-0000", input_type="phone", cancel_event=True)
    # ---------------------------------------------------------------------------------------------------
    # Delivery Address Select Run Task (Limit: 1 Hour)
    # ---------------------------------------------------------------------------------------------------
    async def order_timesleep():
        try:
            for i in range(3600):
                # print('order task call')
                await asyncio.sleep(1)
                if storage.get('order_address'):
                    delivery_picker.content.controls[0].value = storage.get('order_address') # type: ignore
                    delivery_picker.content.controls[0].color = ft.Colors.BLACK # type: ignore
                    delivery_picker.update()
                    break
        except: pass
    # ---------------------------------------------------------------------------------------------------
    # Delivery Address Select Event
    # ---------------------------------------------------------------------------------------------------
    def delivery_picker_route(e):
        if storage.get('order_address'): storage.remove('order_address')
        for task in asyncio.all_tasks():
            if "order_timesleep" in str(task.get_coro()):
                print("\n" * 10 + f"{'===='*30}\n 🪄 Cancel Task Controls\n{'===='*30}")
                print(' ✅ domains.shop.views.shop_orders.order_timesleep()')
                task.cancel()
        dogdog.task_controls()
        asyncio.create_task(order_timesleep()) # type: ignore
        page.go("/shop/address")
    # ---------------------------------------------------------------------------------------------------
    delivery_customer_name = dogdog.input_textfield(
        hint_text="최대 10자로 작성해주세요", cancel_event=True)
    delivery_customer_phone = dogdog.input_textfield(
        hint_text="010-0000-0000", input_type="phone", cancel_event=True)
    delivery_picker = dogdog.picker_field(
        text="배송지를 입력해주세요.", on_click=lambda e:delivery_picker_route(e), icon=ft.Icons.HOME)
    delivery_picker.content.controls[0].max_lines = 3 # type: ignore
    delivery_message = [
        "문 앞에 배송해주세요.",
        "경비실에 맡겨주세요.",
        "배송 전에 연락주세요.",
        "택배함에 넣어주세요."
    ]
    delivery_options = [dogdog.dropdown_menu_option(text) for text in delivery_message]
    delivery_message_menu = dogdog.dropdown_menu(
        label="요청사항을 선택해주세요.",
        event=None,
        options=delivery_options)
    # ---------------------------------------------------------------------------------------------------
    # Order Page View
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text("주문자 정보", size=16, weight="bold"),
        dogdog.basic_text("이름"),
        order_customer_name,
        dogdog.basic_text("전화번호"),
        order_customer_phone,
        ft.Divider(),
        dogdog.basic_text("배송 정보", size=16, weight="bold"),
        dogdog.basic_text("이름"),
        delivery_customer_name,
        dogdog.basic_text("전화번호"),
        delivery_customer_phone,
        dogdog.basic_text("배송주소"),
        delivery_picker,
        dogdog.basic_text("배송메모(선택)"),
        delivery_message_menu,
        ft.Divider(),
        dogdog.basic_text("주문 상품", size=16, weight="bold"),
        dogdog.order_row(content=[
            ft.Text("상품명", font_family="Pretendard", expand=1),
            product_name_text,
        ]),
        dogdog.order_row(content=[
            dogdog.basic_text("상품 수량"),
            dogdog.basic_text(f"{product_quantity:,}개")
        ]),
        ft.Divider(),
        dogdog.basic_text("최종 결제 금액", size=16, weight="bold"),
        dogdog.order_row(content=[
            dogdog.basic_text("상품 가격"),
            product_price_text,
        ]),
        dogdog.order_row(
            visible=True if "/subs_product_order" in page_name else False,
            content=[
                dogdog.basic_text("똑똑 배송 할인", weight="bold", color="#E6001A"), # type: ignore
                subs_sale_price_text,
        ]),
        dogdog.order_row(content=[
            dogdog.basic_text("배송비"),
            dogdog.basic_text("0원"),
        ]),
        dogdog.order_row(content=[
            dogdog.basic_text("총 결제 금액", weight="bold"),
            total_price_text,
        ]),
        ft.Divider(),
        dogdog.basic_text(
            "자동 결제 등록" if "/subs_order" in page_name else "결제 방법", size=16, weight="bold"),
        dogdog.order_row(spacing=8, content=[
            dogdog.flat_button("카드", expand=True),
            dogdog.flat_button("간편결제", expand=True),
        ]),
        dogdog.order_row(
            spacing=8,
            visible=False if "/subs_product_order" in page_name else True,
            content=[
                dogdog.flat_button("가상계좌", expand=True),
                dogdog.flat_button("무통장입금", expand=True),
        ]),
        ft.Divider(height=1),
        ft.Row(
            spacing=3,
            controls=[
                ft.Checkbox(scale=0.9),
                ft.Text(
                    "주문하실 상품 및 결제, 주문정보를 확인했으며 이에 동의합니다. (필수)",
                    size=12, color=ft.Colors.GREY_600, max_lines=3,
                    font_family="Pretendard", expand=True, overflow=ft.TextOverflow.ELLIPSIS),
        ]),
        dogdog.continue_button(
            value="결제하기", bgcolor="#E6001A", text_color=ft.Colors.WHITE, 
            on_click=lambda e: payment_check(e))
    ]
    async def load_order_product():
        product = await get_shop_product_detail(page, product_id)

        if not product:
            product_name_text.value = "상품 정보를 불러올 수 없습니다."
            page.update()
            return

        p_brand = product.get("brand") or ""
        p_name = product.get("product_name") or ""
        p_price = int(product.get("retail_price") or 0)

        order_price = p_price * product_quantity
        sale_order_price = int(order_price*0.1) if "/subs_order" in page_name else 0
        final_price = order_price - sale_order_price
        view_sale_order_price = int(final_price) - int(order_price)

        product_name_text.value = f"[{p_brand}] {p_name}"
        product_price_text.value = f"{order_price:,}원"  # 상품 가격
        subs_sale_price_text.value = f"{sale_order_price:,}원"
        total_price_text.value = f"{int(final_price):,}원"  # 총 결제 금액

        page.update()

    page.run_task(load_order_product)
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.padding.only(left=10, right=10, top=10, bottom=20),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column) # type: ignore
    )