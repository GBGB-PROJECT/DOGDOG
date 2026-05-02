import flet as ft
import components as dogdog

def product(page, p_id, image_src, image_size, brand, title, price):
    print("이미지 URL:", image_src)
    image = ft.Container(
        width=image_size,
        height=image_size,
        alignment=ft.Alignment.CENTER,
        content=ft.Image(
            src=image_src,
            width=image_size,
            height=image_size,
            fit=ft.BoxFit.CONTAIN
        )
    )
    product_brand = dogdog.basic_text(value=brand, size=12, color=ft.Colors.GREY_800)
    product_name = dogdog.basic_text(value=title, size=12, color=ft.Colors.GREY_800)
    product_name.max_lines = 2
    product_name.overflow = ft.TextOverflow.ELLIPSIS
    product_name.width = image_size
    product_name.text_align = ft.TextAlign.CENTER
    product_price = dogdog.basic_text(value=price, size=12, color=ft.Colors.GREY_800)
    return ft.Container(
        padding=0,
        on_click=lambda _:page.go(f"/shop/product/{p_id}"),
        ink=True,
        content=ft.Column(spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
            controls=[image, product_brand, product_name, product_price]
    ))

def products(page, data_dict, image_size):
    items = list(data_dict.items())
    products = []
    for i in range(0, len(items), 3):
        chunk = items[i:i+3]
        row_controls = []
        for p_id, p_d in chunk:
            row_controls.append(
                product(page, 
                    p_id, 
                    p_d.get("thumbnail"), 
                    image_size, 
                    # f"{p_d['brand']} {p_d['product_name']}", 
                    p_d.get('brand'),
                    p_d.get('product_name'), 
                    f"{int(p_d.get('sales_price')):,}원"
                )
            )
        products.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                controls=row_controls
            )
        )
    return products

def shop_top(page: ft.Page, text=None, content_page=None):
    def handle_back(e=None):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
    # -----------------------------------------------------------------------------------------------
    content_text = text or ""

    content = dogdog.basic_text(
        content_text,
        size=20,
        weight="bold",
        color=ft.Colors.GREY_900,
    )

    if content_page and "product/" in content_page:
        async def load_product_title():
            try:
                from domains.shop.controller.shop_api import get_shop_product_detail

                product_id = int(content_page.split("/shop/product/")[-1])
                product = await get_shop_product_detail(page, product_id)

                if product:
                    content.value = product.get("brand") or product.get("product_name") or content_text
                    content.update()
            except Exception as e:
                print("shop_top product title load failed:", e)

        page.run_task(load_product_title)
    elif text:
        content.value = text

    content.expand = True
    content.text_align = ft.TextAlign.CENTER

    return ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        margin=ft.margin.only(bottom=-5),
        height=50,
        controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS, icon_size=20, 
                on_click=handle_back),
            content,
            ft.Container(width=24)
    ])

def order_row(content:list, spacing=10, visible:bool=True):
    return ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        visible=visible, spacing=spacing, controls=content)