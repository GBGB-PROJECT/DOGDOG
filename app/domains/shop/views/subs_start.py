# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def subs_options(page: ft.Page, popup):
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    if not storage.get("select_product_id") and not storage.get("select_product_quantity"):
        return ft.Container(
            padding=ft.padding.only(left=10, right=10, top=10, bottom=20),
            bgcolor="#ffffff",
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    dogdog.basic_text("정상적이지 않은 접근입니다.")
        ]))
    if storage.get("select_subs"): storage.remove("select_subs")
    # ---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------
    def subs_options_check(e):
        page.go("/shop/subs_product_order")
    # ---------------------------------------------------------------------------------------------------
    def delivery_option_change(e, container):
        is_auto_delivery = e.data == "yes"

        storage.set("select_is_auto_delivery", is_auto_delivery)
        storage.set("select_delivery_cycle", None if is_auto_delivery else 2)

        container_option = container.content.controls[2].content
        container_option.controls = ai_delivery_option if 'yes' == e.data else not_ai_delivery_option
        container.update()
    # ---------------------------------------------------------------------------------------------------
    def options_check(e, container):
        container.bgcolor = "#FBDD30"
        container_icon = container.content.controls[0].controls[0]
        container_icon.icon = ft.Icons.CHECK_CIRCLE
        container_icon.color = ft.Colors.BLACK
        container_text = container.content.controls[0].controls[1]
        container_text.color = ft.Colors.BLACK
        if container == new_subs:
            storage.set("select_subs", "new_subs") #***
            storage.set("select_is_auto_delivery", True) #***
            storage.set("select_delivery_cycle", None) #***
            new_subs_option.visible = True
            add_subs.bgcolor = ft.Colors.WHITE
            add_subs_container_icon = add_subs.content.controls[0].controls[0] # type: ignore
            add_subs_container_icon.icon = ft.Icons.CHECK_CIRCLE_OUTLINE
            add_subs_container_icon.color = ft.Colors.GREY_600
            add_subs_container_text = add_subs.content.controls[0].controls[1] # type: ignore
            add_subs_container_text.color = ft.Colors.GREY_600
        else: 
            storage.set("select_subs", "add_subs") #***
            new_subs_option.visible = False
            new_subs.bgcolor = ft.Colors.WHITE
            new_subs_container_icon = new_subs.content.controls[0].controls[0] # type: ignore
            new_subs_container_icon.icon = ft.Icons.CHECK_CIRCLE_OUTLINE
            new_subs_container_icon.color = ft.Colors.GREY_600
            new_subs_container_text = new_subs.content.controls[0].controls[1] # type: ignore
            new_subs_container_text.color = ft.Colors.GREY_600
        next_page.visible = True
    # ---------------------------------------------------------------------------------------------------
    ai_delivery_option = [
        dogdog.basic_text(spans=[
            ft.TextSpan("똑똑 배송으로 주문하신 제품의 "),
            ft.TextSpan("급여 시작일 등록시 똑똑 AI가 급여량과 잔여량을 계산하여 " \
                "실제 사료 소진일에 맞춰 똑똑 배송 설정한 제품을 자동 결제 및 배송"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan("합니다.")
        ], color=ft.Colors.GREY_600),
        dogdog.basic_text(spans=[
            ft.TextSpan("구독 중인 똑똑 배송 제품은 자동 결제, 배송되기 "),
            ft.TextSpan("7,3일 전"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan(" 알려드립니다.")
        ], color=ft.Colors.GREY_600),
        dogdog.basic_text(spans=[
            ft.TextSpan("🚨 마이페이지 내 "),
            ft.TextSpan("똑똑 배송 미루기 와 똑똑 배송 일정 당기기"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan("를 할 수 있습니다.")
        ], color=ft.Colors.GREY_600),
    ]
    not_ai_delivery_option = [
        dogdog.basic_text("구매 배송주기 선택", weight="bold", color=ft.Colors.GREY_800),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            dogdog.radio_group(
                value="2", 
                on_change=lambda e: storage.set("select_delivery_cycle", int(e.data)), 
                contents=[
                    ft.Radio(value="2", label="2주", fill_color=ft.Colors.GREY_800, 
                        label_style=dogdog.TextStyle(color=ft.Colors.GREY_800)),
                    ft.Radio(value="4", label="4주", fill_color=ft.Colors.GREY_800, 
                        label_style=dogdog.TextStyle(color=ft.Colors.GREY_800))
        ])]),
        dogdog.basic_text(spans=[
            ft.TextSpan("선택하신 첫구매 배송주기에 맞춰 자동 결제 및 배송"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan("됩니다.")
        ], color=ft.Colors.GREY_600),
        dogdog.basic_text(spans=[
            ft.TextSpan("구독 중인 똑똑 배송 제품은 자동 결제, 배송되기 "),
            ft.TextSpan("7,3일 전"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan(" 알려드립니다.")
        ], color=ft.Colors.GREY_600),
        dogdog.basic_text(spans=[
            ft.TextSpan("🚨 마이페이지 내 "),
            ft.TextSpan("똑똑 배송 미루기 와 똑똑 배송 일정 당기기"
                , style=dogdog.TextStyle(weight="bold", color=ft.Colors.GREY_600)),
            ft.TextSpan("를 할 수 있습니다.")
        ], color=ft.Colors.GREY_600),
    ]
    # ---------------------------------------------------------------------------------------------------
    # 구독자 여부 파악
    new_subs = dogdog.content_container(
        on_click=None,
        content_list=[
            ft.Row(height=60, controls=[
                ft.Icon(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREY_600, size=20),
                dogdog.basic_text(
                    "새로운 똑똑 배송 시작하기", weight="bold", color=ft.Colors.GREY_600, size=16)
    ])])
    new_subs_option = dogdog.content_container(content_list=[
        dogdog.basic_text("AI 자동배송 선택", weight="bold", color=ft.Colors.GREY_800),
        ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            dogdog.radio_group(
                value="yes", 
                on_change=lambda e:delivery_option_change(e, new_subs_option), 
                contents=[
                    ft.Radio(value="yes", label="예", fill_color=ft.Colors.GREY_800, 
                        label_style=dogdog.TextStyle(color=ft.Colors.GREY_800)),
                    ft.Radio(value="no", label="아니오", fill_color=ft.Colors.GREY_800, 
                        label_style=dogdog.TextStyle(color=ft.Colors.GREY_800))
        ])]),
        ft.Container(
            padding=0,
            margin=0,
            expand=True,
            content=ft.Column(controls=ai_delivery_option)) # type: ignore
    ])
        
    new_subs_option.visible = False
    add_subs = dogdog.content_container(
        on_click=None,
            content_list=[
                ft.Row(height=60, controls=[
                    ft.Icon(icon=ft.Icons.CHECK_CIRCLE_OUTLINE, color=ft.Colors.GREY_600, size=20),
                    dogdog.basic_text("나의 똑똑 배송에 추가하기", weight="bold", color=ft.Colors.GREY_600, size=16)
        ])])
    
    dummy_container = ft.Container(expand=True)
    next_page = dogdog.continue_button(
        value="똑똑배송 시작하기", bgcolor="#E6001A", text_color=ft.Colors.WHITE, 
        on_click=lambda e: subs_options_check(e))
    next_page.visible = False

    # ----------------------------------------------------------------------
    new_subs.on_click = None
    add_subs.on_click = None
    new_subs.opacity = 0.4
    add_subs.opacity = 0.4

    async def load_subscription_state():
        from domains.shop.controller.shop_subscription_api import get_subscription_status

        result = await get_subscription_status(page)

        if not result:
            # 조회 실패 시 둘 다 막아두기
            page.update()
            return

        is_subscribed = result.get("is_subscribed")
        subscription = result.get("subscription")

        storage.set("select_subscription", subscription)

        # 기존 구독자
        if is_subscribed:
            new_subs.on_click = None
            new_subs.opacity = 0.4

            add_subs.on_click = lambda e: options_check(e, add_subs)
            add_subs.opacity = 1
        # 신규 구독자
        else:
            new_subs.on_click = lambda e: options_check(e, new_subs)
            new_subs.opacity = 1

            add_subs.on_click = None
            add_subs.opacity = 0.4

        page.update()

    page.run_task(load_subscription_state)
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        new_subs,
        add_subs,
        new_subs_option,
        dummy_container,
        next_page
    ]
    # ---------------------------------------------------------------------------------------------------
    return ft.Container(
        padding=ft.padding.only(left=10, right=10, top=10, bottom=20),
        bgcolor="#ffffff",
        content=ft.Column(spacing=20, controls=content_column) # type: ignore
    )
