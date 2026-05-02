import flet as ft
import components as dogdog
from urllib.parse import quote
from api_client import BASE_URL

def proxy_image_url(url):
    if not url:
        return "test_product_4.jpg"

    image_url = str(url).strip()
    if image_url.startswith("http://") or image_url.startswith("https://"):
        return f"{BASE_URL}/images/proxy?url={quote(image_url, safe='')}"
    return image_url

def content_container_detail(page: ft.Page, customer_food_id=None, feeding_data: dict = None):
    """
    급여 상세 컨테이너 뷰 컴포넌트 (순수 View)
    - 컨트롤러가 제공한 가공된 feeding_data를 사용하여 렌더링합니다.
    """
    storage = page.session.store

    def feeding_edit_event(e):
        if storage.get("select_customer_food_id"):
            storage.remove("select_customer_food_id")
        if storage.get("select_feeding_data"):
            storage.remove("select_feeding_data")
        storage.set("select_customer_food_id", customer_food_id)
        # raw_data는 컨트롤러에서 원본 데이터를 넘겨준 것이라고 가정
        storage.set("select_feeding_data", feeding_data.get("raw_data") if feeding_data else {})
        page.go("/feeding_edit")

    if not feeding_data:
        # 데이터가 없을 때의 UI
        product_detail = ft.Row(
            height=100,
            expand=True,
            controls=[
                dogdog.basic_text(
                    spans=[ft.TextSpan(" 등록된 제품이 없습니다.")],
                    color=ft.Colors.GREY_600,
                    size=14,
                )
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        return [product_detail]

    # 데이터가 있을 때의 UI (컨트롤러에서 가공한 데이터 사용)
    progress_value = feeding_data.get("progress_value", 0.0)

    product_detail = ft.Row(
        height=100,
        expand=True,
        controls=[
            ft.Image(src=proxy_image_url(feeding_data.get("thumbnail")), fit=ft.BoxFit.CONTAIN, expand=2),
            ft.Column(
                expand=3,
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    dogdog.basic_text(value=feeding_data.get("brand")),
                    dogdog.basic_text(value=feeding_data.get("product_name"), weight="bold"),
                ],
            ),
            ft.Column(
                controls=[
                    dogdog.flat_button(text="변경", scale=0.8, on_click=feeding_edit_event)
                ]
            ),
        ]
    )

    detail = [
        product_detail,
        ft.Divider(height=1),
        ft.Column(
            expand=True,
            spacing=5,
            controls=[
                ft.Row(
                    controls=[
                        dogdog.basic_text(
                            spans=[
                                ft.TextSpan(
                                    text=f"{feeding_data.get('left_intake', '???')}g",
                                    style=dogdog.TextStyle(size=16, height=-1),
                                ),
                                ft.TextSpan(text=f" / {feeding_data.get('total_weight_kg', 0.0)}Kg"),
                            ],
                            color=ft.Colors.GREY_400,
                            weight="bold",
                            size=16,
                        ),
                        dogdog.flat_button(
                            text=f"{feeding_data.get('left_days', '?')} 일치 남음",
                            scale=0.7,
                            disabled=True,
                        ),
                    ]
                ),
                ft.ProgressBar(
                    height=10,
                    value=progress_value,
                    bgcolor=ft.Colors.GREY_300,
                    color="#E6001A" if progress_value < 0.2 else ft.Colors.YELLOW_600,
                    border_radius=10,
                ),
                dogdog.basic_text(
                    spans=[
                        ft.TextSpan("예상 소진일 "),
                        ft.TextSpan(feeding_data.get("expected_exdate_formatted", "????.??.??")),
                    ],
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
        ),
    ]

    return detail

def feeding_tabs_view(page: ft.Page, on_refresh_callback=None, feeding_detail_data=None):
    """
    급여 탭 뷰 컴포넌트 (순수 View)
    - 컨트롤러가 제공한 feeding_detail_data를 넘겨받아 탭 화면을 구성합니다.
    """
    def feeding_view_case(page, set=False):
        if set and feeding_detail_data:
            # 병합/가공된 데이터를 UI 컴포넌트에 주입
            content_column_controls = [
                dogdog.content_container(
                    content_list=content_container_detail(
                        page=page,
                        customer_food_id=None,
                        feeding_data=feeding_detail_data,
                    )
                )
            ]
        else:
            # 데이터가 없거나 Fallback이 필요한 경우 (간식, 영양제 탭 등)
            content_column_controls = [
                dogdog.content_container(
                    content_list=content_container_detail(page=page, feeding_data=None),
                    on_click=lambda _: page.go("/feeding_add"),
                )
            ]

        return ft.Container(
            bgcolor="#ffffff",
            content=ft.Column(
                margin=ft.margin.only(bottom=10),
                controls=content_column_controls,
            ),
        )

    feeding_tabs = [
        ft.Tab(label="전체"),
        ft.Tab(label="사료"),
        ft.Tab(label="간식"),
        ft.Tab(label="영양제"),
    ]

    def content_column(content):
        return ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            controls=[content],
            margin=ft.margin.only(bottom=10),
        )

    feeding_content = [
        content_column(feeding_view_case(page=page, set=True)),  # 전체 탭
        content_column(feeding_view_case(page=page, set=True)),  # 사료 탭
        content_column(feeding_view_case(page=page)),            # 간식 탭
        content_column(feeding_view_case(page=page)),            # 영양제 탭
    ]

    feeding_view = ft.Tabs(
        selected_index=0,
        length=len(feeding_tabs),
        expand=True,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.TabBar(
                            indicator_size=ft.TabBarIndicatorSize.TAB,
                            divider_height=0,
                            tabs=feeding_tabs,
                            label_text_style=dogdog.TextStyle(size=14),
                            expand=True,
                            height=-1,
                        ),
                        dogdog.flat_button(
                            text="사료 등록",
                            scale=0.8,
                            icon=ft.Icons.EDIT,
                            on_click=lambda _: page.go("/feeding_add"),
                        ),
                    ],
                ),
                ft.Divider(height=1),
                ft.TabBarView(
                    expand=True, margin=ft.margin.only(top=10), controls=feeding_content
                ),
            ],
        ),
    )

    return feeding_view
