# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def shop_product_detail(page: ft.Page, content_page):
    # ---------------------------------------------------------------------------------------------------
    from api.product_guide import Product
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    header_width = page.width / 3 # type: ignore
    product_id = int(content_page.strip("/shop/product/"))
    # print(f"product_id: {product_id}")
    content_column = []
    is_detail_page = False
    for p_id , p_d in Product.guide_product_list.items():
        if p_id == product_id:
            p_thumbnail = p_d["thumbnail"]
            p_brand = p_d["brand"]
            p_name = p_d["product_name"]
            p_price = int(p_d["sales_price"])
            is_detail_page = True
            break
    # ---------------------------------------------------------------------------------------------------
    # Product Detail Page Content
    # ---------------------------------------------------------------------------------------------------
    def order_event(e, key):
        print(f"{key}: {product_id}")
        if key == "cart": pass
        elif key == "order": page.go("/shop/order")
        elif key == "wishlist": pass
        elif key == "subs_order": page.go("/shop/order/subs")
    # ---------------------------------------------------------------------------------------------------
    # Product View
    # ---------------------------------------------------------------------------------------------------
    if is_detail_page:
        product_brand = dogdog.basic_text(p_brand, size=20, weight="bold", color=ft.Colors.GREY_900)
        product_name = dogdog.basic_text(p_name, size=16, weight="bold", color=ft.Colors.GREY_800)
        product_name.max_lines = 3
        product_name.overflow = ft.TextOverflow.ELLIPSIS
        product_name.text_align = ft.TextAlign.CENTER
        product_name.width = header_width * 1.4
        product_price = dogdog.basic_text(spans=[
            ft.TextSpan(f"{p_price:,}원\n"),
            ft.TextSpan(f"똑똑 배송 적용가: {int(p_price*0.9):,}원",
                style=dogdog.TextStyle(size=12, color="#E6001A")) # type: ignore
        ], weight="bold", color=ft.Colors.GREY_800)
        product_price.text_align = ft.TextAlign.CENTER
        # -----------------------------------------------------------------------------------------------
        page_header_brand = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[product_brand])
        page_header = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(width=header_width, height=header_width, image=ft.DecorationImage(src=p_thumbnail)),
                ft.Column(
                    height=header_width,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        product_name,
                        product_price
        ])])
        wish_list = dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
            text="♥", size=30, text_color=ft.Colors.WHITE,
            on_click=lambda e:order_event(e=e, key="wishlist"))
        wish_list.padding = ft.padding.only(left=10, right=10)
        page_header_order = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
                text="장바구니", size=16, text_color=ft.Colors.WHITE,
                on_click=lambda e:order_event(e=e, key="cart")),
            dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
                text="바로구매", size=16, text_color=ft.Colors.WHITE,
                on_click=lambda e:order_event(e=e, key="order")),
            wish_list
        ])
        subs_order = dogdog.flat_over_button(bgcolor="#E6001A", # type: ignore
            text="🔔 똑똑 배송으로 주문하기 🔔", expand=True, size=16, text_color=ft.Colors.WHITE,
            on_click=lambda e:order_event(e=e, key="subs_order"))
        subs_order.ink_color = "#80000F" # type: ignore
        page_header_subs_order = ft.Row(margin=ft.margin.only(top=5, bottom=10), controls=[subs_order])
        # -----------------------------------------------------------------------------------------------
        content_column.append(page_header_brand)
        content_column.append(page_header)
        content_column.append(page_header_order)
        content_column.append(page_header_subs_order)
        content_column.append(ft.Divider())
        # -----------------------------------------------------------------------------------------------
        # Product Detail Image Append
        # -----------------------------------------------------------------------------------------------
        for p_id , p_images in Product.product_detail_src.items():
            harim_url = "https://m.harimpetfood.com"
            if p_id == product_id:
                for image in p_images:
                    image_src_link = f"{harim_url}{image}"
                    content_column.append(ft.Image(src=image_src_link))
    else:
        content_column.append(
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                dogdog.basic_text("해당 상품은 존재하지 않습니다.")
            ])
        )
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column # type: ignore
        )
    )