import flet as ft
import components as dogdog
import datetime

def content_container_detail(page: ft.Page, customer_food_id=None, feeding_data:dict=None): # type: ignore
    storage = page.session.store
    def feeding_edit_event(e):
        if storage.get("select_customer_food_id"): storage.remove("select_customer_food_id")
        if storage.get("select_feeding_data"): storage.remove("select_feeding_data")
        storage.set("select_customer_food_id", customer_food_id)
        storage.set("select_feeding_data", feeding_data)
        page.go("/feeding_edit")

    now = datetime.datetime.now()
    days = datetime.timedelta(days=feeding_data["left_food_count"]) if feeding_data else 0
    last_feeding_food_count = (now+days).strftime("%Y.%m.%d") if days != 0 else "????.??.??"

    feeding_food_weight = feeding_data["left_intake"] if feeding_data else 0
    g_product_weight = feeding_data["total_weight"] if feeding_data else 5
    kg_product_weight = float(g_product_weight / 1000)
    view_product_weight = (
        f"{kg_product_weight}Kg" if len(str(kg_product_weight).replace(".0", "")) > 2 
            else f"{g_product_weight}g"
    ) if feeding_data else "???Kg"

    product_detail = ft.Row(height=100, expand=True, controls=[
        ft.Image(src=feeding_data["thumbnail"], fit=ft.BoxFit.CONTAIN, expand=2),
        ft.Column(expand=3, spacing=0, alignment=ft.MainAxisAlignment.CENTER, controls=[
            dogdog.basic_text(value=feeding_data["brand"]),
            dogdog.basic_text(value=feeding_data["product_name"], weight="bold")
        ]),
        ft.Column(
            controls=[dogdog.flat_button(text="변경", on_click=feeding_edit_event ,disabled=False)]
    )] if feeding_data else [dogdog.basic_text(spans=[
        ft.TextSpan(" 등록된 제품이 없습니다."),
        # ft.TextSpan("\n제품을 등록하시겠습니까?")
    ], color=ft.Colors.GREY_600, size=14)],
    alignment=ft.MainAxisAlignment.CENTER if not feeding_data else None # type: ignore
    )

    detail = [
        product_detail,
        ft.Divider(height=1),
        ft.Column(expand=True, spacing=5, controls=[
            ft.Row(controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan(
                        text=f"{feeding_food_weight if feeding_food_weight != 0 else '???'}g",
                        style=dogdog.TextStyle(size=16)),
                    ft.TextSpan(text=f" / {view_product_weight}")
                ], color=ft.Colors.GREY_400, weight="bold", size=16),
                dogdog.flat_button(text=f"{feeding_data['left_food_count'] if feeding_data else '?'} 일치 남음", scale=0.7),
            ]),
            ft.ProgressBar(
                height=10,
                value=feeding_food_weight / g_product_weight,
                bgcolor=ft.Colors.GREY_300,
                color=ft.Colors.YELLOW_600,
                border_radius=10,
            ),
            dogdog.basic_text(spans=[
                ft.TextSpan("예상 소진일 "),
                ft.TextSpan(last_feeding_food_count)
            ], size=12, color=ft.Colors.GREY_600),
    ])]

    return detail

def feeding_tabs_view(page: ft.Page):
    storage = page.session.store
    def feeding_view_case(page, set=False):
        customer_food_detail = storage.get("customer_detail")
        content_column = [
            dogdog.content_container(
                content_list=content_container_detail(
                    page=page, customer_food_id=customer_food_id, feeding_data=detail
            )) for customer_food_id , detail in customer_food_detail.items()
        ] if customer_food_detail and set else [
            dogdog.content_container(
                content_list=content_container_detail(page=page), 
                on_click=lambda _: page.go("/feeding_add"))
        ]

        return ft.Container(
            bgcolor="#ffffff",
            content=ft.Column(
                margin=ft.margin.only(bottom=10),
                controls=content_column # type: ignore
            )
        )

    feeding_tabs = [
        ft.Tab(label="전체"),
        ft.Tab(label="사료"),
        ft.Tab(label="간식"),
        ft.Tab(label="영양제")
    ]

    def content_column(content):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN, expand=True, controls=[content], margin=ft.margin.only(bottom=10)
        )

    feeding_content = [
        content_column(feeding_view_case(page=page, set=True)), # 전체 탭
        content_column(feeding_view_case(page=page, set=True)), # 사료 탭
        content_column(feeding_view_case(page=page)), # 간식 탭
        content_column(feeding_view_case(page=page)), # 영양제 탭
    ]
    
    feeding_view = ft.Tabs(
        selected_index=0,
        length=len(feeding_tabs),
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN, controls=[
                    ft.TabBar(
                        indicator_size=ft.TabBarIndicatorSize.TAB, divider_height=0,
                        tabs=feeding_tabs, label_text_style=dogdog.TextStyle(size=14), expand=True),  # type: ignore
                    dogdog.flat_button(
                        text="사료 등록", icon=ft.Icons.EDIT, on_click=lambda _: page.go("/feeding_add"), disabled=False)
                ]),
                ft.Divider(height=1),
                ft.TabBarView(expand=True, margin=ft.margin.only(top=10), controls=feeding_content), # type: ignore
    ]))

    return feeding_view