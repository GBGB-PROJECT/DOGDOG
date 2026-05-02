# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
class Default_data:
    def __init__(self, page: ft.Page, popup, content_page):
        # -----------------------------------------------------------------------------------------------
        # from api.product_guide import Product
        # -----------------------------------------------------------------------------------------------
        # Default Value
        # -----------------------------------------------------------------------------------------------
        # self.Product = Product
        self.popup = popup
        self.page = page
        self.storage = page.session.store
        self.header_width = page.width / 3 # type: ignore
        # self.product_id = int(content_page.strip("/shop/product/"))
        self.product_id = int(content_page.split("/shop/product/")[-1])
        # print(f"product_id: {self.product_id}")
        self.is_detail_page = False

        self.p_thumbnail = None
        self.p_brand = ""
        self.p_name =""
        self.p_price = 0
        self.pdi_images = []

        self.default_bottom_sheet = popup.bottom_sheet_popup
        self.default_bottom_sheet_content = popup.bottom_sheet_controls
        self.message = {
            "cart":"원 장바구니 담기",
            "order":"원 바로 구매",
            "subs_order":"원 똑똑 배송으로 주문하기 🔔"
        }

    async def load_product_detail(self):
        from domains.shop.controller.shop_api import get_shop_product_detail

        product = await get_shop_product_detail(self.page, self.product_id)

        if not product:
            self.is_detail_page = False
            self.page.update()
            return

        self.p_thumbnail = product.get("thumbnail")
        self.p_brand = product.get("brand") or ""
        self.p_name = product.get("product_name") or ""
        self.p_price = int(product.get("retail_price") or 0)
        self.pdi_images = product.get("pdi_images") or []

        self.is_detail_page = True
        self.page.update()
    # ---------------------------------------------------------------------------------------------------
    # Button Bottom Sheet
    # ---------------------------------------------------------------------------------------------------
    def bottom_sheet_open(self, e, key):
        self.bt_order_count_value = 1
        self.sale_order_price = self.p_price / 10
        self.final_price = (self.p_price - self.sale_order_price) if key == "subs_order" else self.p_price
        bt_product_price = dogdog.basic_text(spans=[
            ft.TextSpan(f"{self.p_price:,}원\n"),
            ft.TextSpan(f"똑똑 배송 적용가: {int(self.p_price*0.9):,}원",
                style=dogdog.TextStyle(size=12, color="#E6001A")) # type: ignore
            ], weight="bold", color=ft.Colors.GREY_700)
        self.default_bottom_sheet_content.clear()
        # print(f"{key}: {self.product_id}")
        bt_product_name = dogdog.basic_text(
            f"[{self.p_brand}] {self.p_name}", weight="bold", color=ft.Colors.GREY_700)
        bt_product_name.expand = True
        bt_product_name.overflow = ft.TextOverflow.ELLIPSIS
        bt_product_explanation = dogdog.basic_text(
            "상품 설명", size=12, color=ft.Colors.GREY_600)
        bt_product_explanation.max_lines = 2
        bt_product_explanation.expand = True
        bt_product_explanation.overflow = ft.TextOverflow.ELLIPSIS
        bt_product_header = ft.Row(vertical_alignment=ft.CrossAxisAlignment.START, controls=[
            ft.Container(width=60, height=60, image=ft.DecorationImage(src=self.p_thumbnail)),
            ft.Column(spacing=0, expand=True, controls=[bt_product_name, bt_product_explanation])
        ])
        self.bt_order_count_input = dogdog.basic_text(str(self.bt_order_count_value))
        self.bt_order_count = ft.Container(
            content=ft.Row(vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                ft.IconButton(
                icon=ft.Icons.ARROW_BACK_IOS, icon_size=10, 
                on_click=lambda e:self.order_count_event(e, "back", key)),
                self.bt_order_count_input,
                ft.IconButton(
                icon=ft.Icons.ARROW_FORWARD_IOS, icon_size=10, 
                on_click=lambda e:self.order_count_event(e, "forward", key)),
        ]))
        bt_product_main = ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
            bt_product_price,
            self.bt_order_count
        ])
        self.bt_product_bottom = dogdog.flat_over_button(bgcolor="#FBDD30", # type: ignore
            text=None, size=16, text_color=ft.Colors.WHITE, expand=True,
            on_click=lambda e:self.routing_page_event(e, key)
        )
        # -----------------------------------------------------------------------------------------------
        self.bt_button = self.bt_product_bottom.content
        self.bt_button.value = f"{self.final_price:,}{self.message.get(key)}" # type: ignore
        if key == "subs_order": # page.go("/shop/order/subs")
            self.bt_product_bottom.bgcolor = "#E6001A" # type: ignore
            self.bt_button.color = ft.Colors.WHITE # type: ignore
            self.bt_button.value = f"🔔 {int(self.final_price):,}{self.message.get(key)}" # type: ignore
        # -----------------------------------------------------------------------------------------------
        self.default_bottom_sheet_content.append(bt_product_header)
        self.default_bottom_sheet_content.append(ft.Divider())
        self.default_bottom_sheet_content.append(bt_product_main)
        self.default_bottom_sheet_content.append(self.bt_product_bottom)
        # -----------------------------------------------------------------------------------------------        
        if self.default_bottom_sheet not in self.page.overlay:
            self.page.overlay.append(self.default_bottom_sheet)
        else:
            self.page.overlay.clear()
            self.page.overlay.append(self.default_bottom_sheet)
        self.default_bottom_sheet.open = True
        self.page.update()
    # ---------------------------------------------------------------------------------------------------
    # Order Count Event
    # ---------------------------------------------------------------------------------------------------
    def order_count_event(self, e, value, key):
        count = self.bt_order_count_value
        if value == "back":
            if count > 1: self.bt_order_count_value = count - 1
        elif value == "forward":
            if count < 99: self.bt_order_count_value = count + 1
        self.bt_button.value = ( # type: ignore
            f"{int(self.final_price * self.bt_order_count_value):,}{self.message.get(key)}")
        if key == "subs_order": # page.go("/shop/order/subs")
            self.bt_button.value = "🔔 " + self.bt_button.value # type: ignore
        self.bt_order_count_input.value = str(self.bt_order_count_value)
        self.bt_order_count.update()
        self.bt_product_bottom.update()
    # ---------------------------------------------------------------------------------------------------
    # Route Change Event
    # ---------------------------------------------------------------------------------------------------
    def routing_page_event(self, e, key):
        def cart_rauting(e, key):
            cart_event.open = False
            self.page.go(f"/shop/{key}")
        self.default_bottom_sheet.open = False
        # self.page.update()
        # print(key)
        if key == "wishlist":
            self.show_event(text=f"{self.p_name} 상품이 위시리스트에 추가되었습니다!")
        elif key == "cart": 
            cart_event = self.popup.event_popup
            cart_event.title = dogdog.basic_text("장바구니", size=16, weight="bold")
            cart_event.content.value = "장바구니에 상품이 추가되었습니다\n확인하시겠어요?"
            cart_event.actions[0].content = "네"
            cart_event.actions[0].on_click = lambda e:cart_rauting(e,key)
            cart_event.actions[1].content = "괜찮아요"
            if cart_event not in self.page.overlay:
                self.page.overlay.append(cart_event)
            else:
                self.page.overlay.clear()
                self.page.overlay.append(cart_event)
            cart_event.open = True
            self.page.update()
        else:
            # print(self.product_id, self.bt_order_count_value)
            self.storage.set("select_product_id",self.product_id)
            self.storage.set("select_product_quantity", self.bt_order_count_value)
            self.page.go(f"/shop/{key}")
    def show_event(self, text:str):
        self.page.show_dialog(
            ft.SnackBar(content=ft.Text(value=text), open=True, behavior=ft.SnackBarBehavior.FLOATING))
# -------------------------------------------------------------------------------------------------------

# -------------------------------------------------------------------------------------------------------
def shop_product_detail(page: ft.Page, popup, content_page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    dd = Default_data(page, popup, content_page)
    content_column = ft.Column(
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.ProgressRing()
                ]
            )
        ]
    )
    # ---------------------------------------------------------------------------------------------------
    # Product View
    # ---------------------------------------------------------------------------------------------------
    def error_message(image_count):
        message = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.basic_text(
                    f"{image_count}번 이미지가 로딩되지 않았어요.\nCORS 설정을 확인해주세요."
                )
            ]
        )
        message.controls[0].text_align = ft.TextAlign.CENTER # type: ignore
        return message

    def render_detail():
        content_column.controls.clear()

        if not dd.is_detail_page:
            content_column.controls.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text("해당 상품은 존재하지 않습니다.")
                    ]
                )
            )
            page.update()
            return

        product_brand = dogdog.basic_text(
            dd.p_brand,
            size=20,
            weight="bold",
            color=ft.Colors.GREY_900
        )
        product_brand.expand = True
        product_brand.text_align = ft.TextAlign.CENTER

        product_name = dogdog.basic_text(
            dd.p_name,
            weight="bold",
            color=ft.Colors.GREY_700
        )
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
        page_header = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=dd.header_width,
                    height=dd.header_width,
                    content=ft.Image(
                        src=dd.p_thumbnail, # type: ignore
                        width=dd.header_width,
                        height=dd.header_width,
                        fit="contain" # type: ignore
                    )
                ),
                ft.Column(
                    height=dd.header_width,
                    alignment=ft.MainAxisAlignment.SPACE_AROUND,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        product_name,
                        product_price
                    ]
                )
            ]
        )

        wish_list = dogdog.flat_over_button(
            bgcolor="#FBDD30", # type: ignore
            text="♥",
            size=30,
            text_color=ft.Colors.WHITE,
            on_click=lambda e:dd.routing_page_event(e, "wishlist")
        )
        wish_list.padding = ft.padding.only(left=10, right=10)

        page_header_order = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_over_button(
                    bgcolor="#FBDD30", # type: ignore
                    text="장바구니",
                    size=16,
                    text_color=ft.Colors.WHITE,
                    expand=True,
                    on_click=lambda e: dd.bottom_sheet_open(e=e, key="cart")
                ),
                dogdog.flat_over_button(
                    bgcolor="#FBDD30", # type: ignore
                    text="바로구매",
                    size=16,
                    text_color=ft.Colors.WHITE,
                    expand=True,
                    on_click=lambda e: dd.bottom_sheet_open(e=e, key="order")
                ),
                wish_list
            ]
        )

        subs_order = dogdog.flat_over_button(
            bgcolor="#E6001A", # type: ignore
            text="🔔 똑똑 배송으로 주문하기 🔔",
            expand=True,
            size=16,
            text_color=ft.Colors.WHITE,
            on_click=lambda e: dd.bottom_sheet_open(e=e, key="subs_order")
        )
        subs_order.ink_color = "#80000F"

        page_header_subs_order = ft.Row(
            margin=ft.margin.only(top=5, bottom=5),
            controls=[subs_order]
        )

        content_column.controls.append(page_header)
        content_column.controls.append(page_header_order)
        content_column.controls.append(page_header_subs_order)
        content_column.controls.append(ft.Divider())

        # if dd.pdi:
        #     content_column.controls.append(
        #         ft.Image(
        #             src=dd.pdi,
        #             error_content=error_message(1)
        #         )
        #     )
        
        if dd.pdi_images:
            image_width = (page.width or 390) - 40

            for i, image_url in enumerate(dd.pdi_images, start=1):
                content_column.controls.append(
                    ft.Image(
                        src=image_url,
                        width=image_width,
                        fit=ft.BoxFit.CONTAIN,
                        error_content=error_message(i),
                    )
                )

        page.update()

    async def load_and_render():
        await dd.load_product_detail()
        render_detail()

    page.run_task(load_and_render)

    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        content=content_column
    )