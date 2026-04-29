# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
class Default_data:
    def __init__(self, page, content_page):
        # -----------------------------------------------------------------------------------------------
        from api.product_guide import Product
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        self.Product = Product
        self.header_width = page.width / 3 # type: ignore
        self.product_id = int(content_page.strip("/shop/product/"))
        # print(f"product_id: {self.product_id}")
        self.is_detail_page = False
        for p_id , p_d in self.Product.guide_product_list.items():
            if p_id == self.product_id:
                self.p_thumbnail = p_d["thumbnail"]
                self.p_brand = p_d["brand"]
                self.p_name = p_d["product_name"]
                self.p_price = int(p_d["sales_price"])
                self.is_detail_page = True
                break
        self.bt_order_count_value = 1

def shop_product_detail(page: ft.Page, popup, content_page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    dd = Default_data(page, content_page)
    content_column = []
    # ---------------------------------------------------------------------------------------------------
    # Button Bottom Sheet
    # ---------------------------------------------------------------------------------------------------
    default_bottom_sheet = popup.bottom_sheet_popup
    default_bottom_sheet_content = popup.bottom_sheet_controls
    def button_event(e, key):
        default_bottom_sheet_content.clear()
        print(f"{key}: {dd.product_id}")
        if key == "cart": return
        elif key == "order": pass # page.go("/shop/order")
        elif key == "wishlist": return
        elif key == "subs_order": # page.go("/shop/order/subs")
            bt_product_name = dogdog.basic_text(
                f"[{dd.p_brand}] {dd.p_name}", weight="bold", color=ft.Colors.GREY_700)
            bt_product_name.expand = True
            bt_product_name.overflow = ft.TextOverflow.ELLIPSIS
            bt_product_explanation = dogdog.basic_text(
                "상품 설명", size=12, color=ft.Colors.GREY_600)
            bt_product_explanation.max_lines = 2
            bt_product_explanation.expand = True
            bt_product_explanation.overflow = ft.TextOverflow.ELLIPSIS
            bt_product_header = ft.Row(vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Container(width=60, height=60, image=ft.DecorationImage(src=dd.p_thumbnail)),
                ft.Column(spacing=0, expand=True, controls=[bt_product_name, bt_product_explanation])
            ])
            bt_product_price = dogdog.basic_text(spans=[
                ft.TextSpan(f"{dd.p_price:,}원\n"),
                ft.TextSpan(f"똑똑 배송 적용가: {int(dd.p_price*0.9):,}원",
                    style=dogdog.TextStyle(size=12, color="#E6001A")) # type: ignore
            ], weight="bold", color=ft.Colors.GREY_700)
            bt_order_count_input = dogdog.basic_text(str(dd.bt_order_count_value))
            def order_count_event(e, key, long_press=False):
                value = dd.bt_order_count_value
                if key == "back":
                    if value > 1: dd.bt_order_count_value = value - 1
                elif key == "back" and long_press:
                    if value > 1: dd.bt_order_count_value = value - 1
                elif key == "forward":
                    if value < 99: dd.bt_order_count_value = value + 1
                else: pass
                bt_order_count_input.value = str(dd.bt_order_count_value)
                bt_order_count.update()
            bt_order_count = ft.Container(
                content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                    ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS, icon_size=10, 
                    on_click=lambda e:order_count_event(e, "back"),
                    on_long_press=lambda e:order_count_event(e, "back", True)),
                    bt_order_count_input,
                    ft.IconButton(
                    icon=ft.Icons.ARROW_FORWARD_IOS, icon_size=10, 
                    on_click=lambda e:order_count_event(e, "forward"),
                    on_long_press=lambda e:order_count_event(e, "forward", True)),
            ]))
            bt_product_main = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                bt_product_price,
                bt_order_count
            ])
            default_bottom_sheet_content.append(bt_product_header)
            default_bottom_sheet_content.append(ft.Divider())
            default_bottom_sheet_content.append(bt_product_main)
        else: return
        if default_bottom_sheet not in page.overlay:
            page.overlay.append(default_bottom_sheet)
        else:
            page.overlay.clear()
            page.overlay.append(default_bottom_sheet)
        default_bottom_sheet.open = True
        page.update()
    # ---------------------------------------------------------------------------------------------------
    # Product View
    # ---------------------------------------------------------------------------------------------------
    if dd.is_detail_page:
        product_brand = dogdog.basic_text(dd.p_brand, size=20, weight="bold", color=ft.Colors.GREY_900)
        product_brand.expand = True
        product_brand.text_align = ft.TextAlign.CENTER
        product_name = dogdog.basic_text(dd.p_name, weight="bold", color=ft.Colors.GREY_700)
        product_name.max_lines = 3
        product_name.overflow = ft.TextOverflow.ELLIPSIS
        product_name.text_align = ft.TextAlign.CENTER
        product_name.width = dd.header_width * 1.4
        product_price = dogdog.basic_text(spans=[
            ft.TextSpan(f"{dd.p_price:,}원\n"),
            ft.TextSpan(f"똑똑 배송 적용가: {int(dd.p_price*0.9):,}원",
                style=dogdog.TextStyle(size=12, color="#E6001A")) # type: ignore
        ], weight="bold", color=ft.Colors.GREY_700)
        product_price.text_align = ft.TextAlign.CENTER
        # -----------------------------------------------------------------------------------------------
        page_header_brand = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS, icon_size=10, 
                on_click=lambda _:page.go("/shop")),
            product_brand,
            ft.Container(width=24)
        ])
        page_header = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(width=dd.header_width, height=dd.header_width, image=ft.DecorationImage(src=dd.p_thumbnail)),
                ft.Column(
                    height=dd.header_width,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        product_name,
                        product_price
        ])])
        wish_list = dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
            text="♥", size=30, text_color=ft.Colors.WHITE,
            on_click=lambda e:button_event(e=e, key="wishlist"))
        wish_list.padding = ft.padding.only(left=10, right=10)
        page_header_order = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
                text="장바구니", size=16, text_color=ft.Colors.WHITE, expand=True,
                on_click=lambda e:button_event(e=e, key="cart")),
            dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
                text="바로구매", size=16, text_color=ft.Colors.WHITE, expand=True,
                on_click=lambda e:button_event(e=e, key="order")),
            wish_list
        ])
        subs_order = dogdog.flat_over_button(bgcolor="#E6001A", # type: ignore
            text="🔔 똑똑 배송으로 주문하기 🔔", expand=True, size=16, text_color=ft.Colors.WHITE,
            on_click=lambda e:button_event(e=e, key="subs_order"))
        subs_order.ink_color = "#80000F" # type: ignore
        page_header_subs_order = ft.Row(margin=ft.margin.only(top=5, bottom=5), controls=[subs_order])
        # -----------------------------------------------------------------------------------------------
        content_column.append(page_header_brand)
        content_column.append(page_header)
        content_column.append(page_header_order)
        content_column.append(page_header_subs_order)
        content_column.append(ft.Divider())
        # -----------------------------------------------------------------------------------------------
        # Product Detail Image Append
        # -----------------------------------------------------------------------------------------------
        def error_message(image_count):
            message = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                dogdog.basic_text(f"{image_count}번 이미지가 로딩되지 않았어요.\nCORS 설정을 확인해주세요.")
            ])
            message.controls[0].text_align = ft.TextAlign.CENTER # type: ignore
            return message

        for p_id , p_images in dd.Product.product_detail_src.items():
            harim_url = "https://m.harimpetfood.com"
            if p_id == dd.product_id:
                i = 0
                for image in p_images:
                    i = i + 1
                    image_src_link = f"{harim_url}{image}"
                    content_column.append(ft.Image(
                        src=image_src_link, error_content=error_message(i)))
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