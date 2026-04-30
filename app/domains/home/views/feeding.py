import flet as ft
import components as dogdog
import datetime
import domains
from domains.logs.controller.grid_controller import GridController


def content_container_detail(
    page: ft.Page, customer_food_id=None, feeding_data: dict = None
):  # type: ignore
    storage = page.session.store

    def feeding_edit_event(e):
        if storage.get("select_customer_food_id"):
            storage.remove("select_customer_food_id")
        if storage.get("select_feeding_data"):
            storage.remove("select_feeding_data")
        storage.set("select_customer_food_id", customer_food_id)
        storage.set("select_feeding_data", feeding_data)
        page.go("/feeding_edit")

    # 1. 데이터 추출 및 계산식 동기화 (Home Dashboard 로직 이식)
    if not feeding_data:
        feeding_data = {}

    left_intake = feeding_data.get("left_intake") or feeding_data.get("left_weight", 0)
    total_weight_g = feeding_data.get("total_weight", 0)
    total_weight_kg = round(float(total_weight_g) / 1000, 1) if total_weight_g else 0.0

    left_percent = feeding_data.get("left_percent", 0)
    progress_value = (
        float(left_percent) / 100 if float(left_percent) > 1 else float(left_percent)
    )

    left_days = feeding_data.get("left_food_count") or feeding_data.get(
        "expected_left_days", 0
    )
    expected_exdate = feeding_data.get("expected_exdate") or feeding_data.get(
        "expected_last_day", "????-??-??"
    )
    expected_exdate_formatted = str(expected_exdate).replace("-", ".")

    brand = feeding_data.get("product_brand") or feeding_data.get("brand") or ""
    product_name = feeding_data.get("product_name") or feeding_data.get("name") or ""
    thumbnail = (
        feeding_data.get("product_thumbnail")
        or feeding_data.get("thumbnail")
        or "dogbowl.png"
    )

    product_detail = ft.Row(
        height=100,
        expand=True,
        controls=[
            ft.Image(src=thumbnail, fit=ft.BoxFit.CONTAIN, expand=2),
            ft.Column(
                expand=3,
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    dogdog.basic_text(value=brand),
                    dogdog.basic_text(value=product_name, weight="bold"),
                ],
            ),
            ft.Column(
                controls=[
                    dogdog.flat_button(
                        text="변경", scale=0.8, on_click=feeding_edit_event
                    )
                ]
            ),
        ]
        if feeding_data
        else [
            dogdog.basic_text(
                spans=[ft.TextSpan(" 등록된 제품이 없습니다.")],
                color=ft.Colors.GREY_600,
                size=14,
            )
        ],
        alignment=ft.MainAxisAlignment.CENTER if not feeding_data else None,  # type: ignore
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
                                    text=f"{left_intake if left_intake != 0 else '???'}g",
                                    style=dogdog.TextStyle(size=16, height=-1),
                                ),
                                ft.TextSpan(text=f" / {total_weight_kg}Kg"),
                            ],
                            color=ft.Colors.GREY_400,
                            weight="bold",
                            size=16,
                        ),
                        dogdog.flat_button(
                            text=f"{round(float(left_days), 1) if left_days else '?'} 일치 남음",
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
                        ft.TextSpan(expected_exdate_formatted),
                    ],
                    size=12,
                    color=ft.Colors.GREY_600,
                ),
            ],
        ),
    ]

    return detail


def feeding_tabs_view(page: ft.Page, on_refresh_callback=None):
    storage = page.session.store

    def feeding_view_case(page, set=False):
        # [1] 세션 데이터 경로 정규화 (홈 화면 대시보드 소스 동기화)
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}

        # [2] 메인에서 미리 저장해 둔 사료 상세 정보 가져오기
        pet_food_detail = storage.get("pet_food_detail") or {}

        # [3] 데이터 병합 (재고 데이터 + 상세 정보)
        merged_data = {**inventory, **pet_food_detail}

        # [4] 데이터 존재 여부에 따른 UI 조립
        if set and (inventory or pet_food_detail):
            # 병합된 데이터를 UI 컴포넌트에 주입
            content_column_controls = [
                dogdog.content_container(
                    content_list=content_container_detail(
                        page=page,
                        customer_food_id=None,
                        feeding_data=merged_data,
                    )
                )
            ]
        else:
            # 데이터가 없거나 Fallback이 필요한 경우 (간식, 영양제 탭 등)
            content_column_controls = [
                dogdog.content_container(
                    content_list=content_container_detail(page=page),
                    on_click=lambda _: page.go("/feeding_add"),
                )
            ]

        return ft.Container(
            bgcolor="#ffffff",
            content=ft.Column(
                margin=ft.margin.only(bottom=10),
                controls=content_column_controls,  # type: ignore
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
        content_column(feeding_view_case(page=page)),  # 간식 탭
        content_column(feeding_view_case(page=page)),  # 영양제 탭
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
                        ),  # type: ignore
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
                ),  # type: ignore
            ],
        ),
    )

    return feeding_view
