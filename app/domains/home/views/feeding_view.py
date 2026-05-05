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
        if storage.contains_key("select_customer_food_id"):
            storage.remove("select_customer_food_id")
        if storage.contains_key("select_feeding_data"):
            storage.remove("select_feeding_data")
        storage.set("select_customer_food_id", customer_food_id)
        storage.set("select_feeding_data", feeding_data.get("raw_data") if feeding_data else {})
        page.go("/feeding_edit")

    def go_product_detail(e):
        product_id = None

        if feeding_data:
            product_id = (
                feeding_data.get("product_id")
                or feeding_data.get("raw_data", {}).get("product_id")
            )
        if not product_id:
            page.show_dialog(
                ft.SnackBar(
                    content=ft.Text("상품 정보를 찾을 수 없습니다."),
                    open=True,
                    behavior=ft.SnackBarBehavior.FLOATING,
                )
            )
            return
        page.go(f"/shop/product/{product_id}")


    # [해결] 데이터가 비어있거나 필수 정보(상품명)가 없는 경우 안내 UI 출력
    if not feeding_data or not feeding_data.get("product_name") or feeding_data.get("product_name") == "등록된 사료 없음":
        return [
            ft.Row(
                height=150,
                expand=True,
                controls=[
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                        controls=[
                            ft.Icon(icon=ft.Icons.ERROR_OUTLINE_ROUNDED, color=ft.Colors.GREY_400, size=30),
                            dogdog.basic_text(
                                value="등록된 상품이 없습니다.",
                                color=ft.Colors.GREY_600,
                                size=14,
                            ),
                        ]
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]

    # 수치 파싱 안전 함수 (View 내부용)
    def safe_display_int(val, suffix=""):
        try:
            return f"{int(float(val)):,}{suffix}"
        except (ValueError, TypeError):
            return f"0{suffix}" if suffix else "0"

    # 데이터가 있을 때의 UI
    progress_value = feeding_data.get("progress_value", 0.0)

    product_info = ft.Container(
        expand=True,
        ink=True,
        border_radius=8,
        on_click=go_product_detail,
        content=ft.Row(
            height=100,
            expand=True,
            controls=[
                ft.Image(
                    src=proxy_image_url(feeding_data.get("thumbnail")),
                    fit=ft.BoxFit.CONTAIN,
                    expand=2,
                ),
                ft.Column(
                    expand=3,
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        dogdog.basic_text(value=feeding_data.get("brand")),
                        dogdog.basic_text(value=feeding_data.get("product_name"), weight="bold"),
                    ],
                ),
            ],
        ),
    )

    product_detail = ft.Row(
        height=100,
        expand=True,
        controls=[
            product_info,
            ft.Column(
                controls=[
                    dogdog.flat_button(text="수정", scale=0.8, on_click=feeding_edit_event)
                ]
            ),
        ],
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
                                     text=f"{safe_display_int(feeding_data.get('left_intake'))}g",
                                     style=dogdog.TextStyle(size=16, height=-1),
                                 ),
                                 ft.TextSpan(text=f" / {feeding_data.get('total_weight_kg', 0.0)}Kg"),
                            ],
                            color=ft.Colors.GREY_400,
                            weight="bold",
                            size=16,
                        ),
                        dogdog.flat_button(
                            text=f"{safe_display_int(feeding_data.get('left_days'))} 일치 남음" if feeding_data.get('left_days') not in [None, "?", "None"] else "0 일치 남음",
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
                            text="상품 등록",
                            scale=0.8,
                            #icon=ft.Icons.EDIT,
                            on_click=lambda _: page.run_task(handle_add_product),
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

    async def handle_add_product():
        print("👉 [로그] 뷰: [상품 등록] 버튼 클릭 이벤트 발생")
        # [QA 수정] 현재 급여 중인 상품이 있는지 확인 (데이터가 존재하면 경고창)
        if feeding_detail_data and feeding_detail_data.get("product_name"):
            print("👉 [로그] 뷰: 기존 급여 상품 존재 확인 - 중복 등록 에러 다이얼로그 호출")
            from domains.home.controller.feeding_add_edit_controller import FeedingAddEditController
            temp_ctrl = FeedingAddEditController(page)
            temp_ctrl.show_duplicate_error_dialog()
        else:
            # 데이터가 없을 때만 등록 화면으로 이동
            page.go("/feeding_add")

    return feeding_view
