# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime
# -------------------------------------------------------------------------------------------------------
def now_history(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    # Now History View (제작중)
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Row([
                dogdog.basic_text(value="오늘의 기록", size=18, weight="bold"),
                dogdog.basic_text(value=datetime.datetime.now().strftime("%Y.%m.%d"), size=14, weight="bold", color=ft.Colors.GREY_700),
        ]),
        ft.Row(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button("급여량: 100g"),
                dogdog.flat_button("음수량: 100ml"),
                dogdog.flat_button("산책: 60분"),
        ]),
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                dogdog.basic_text(value="목표 활동량", size=14, color=ft.Colors.GREY_700, weight="bold"),
                ft.Column(
                    spacing=0,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressBar(
                            height=20,
                            value=45 / 90 if 90 else 0,
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.YELLOW_600,
                            border_radius=10,
                        ),
                        dogdog.basic_text(
                            value=f"{45}/{90}{'분'}",
                            size=12,
                            color=ft.Colors.GREY_500,
                            weight="bold",
                        ),
                    ],
                ),
            ]
        ),
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                dogdog.basic_text(value="목표 칼로리", size=14, color=ft.Colors.GREY_700, weight="bold"),
                ft.Column(
                    spacing=0,
                    expand=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.ProgressBar(
                            height=20,
                            value=150 / 310 if 310 else 0,
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.YELLOW_600,
                            border_radius=10,
                        ),
                        dogdog.basic_text(
                            value=f"{150}/{310}{'kcal'}",
                            size=12,
                            color=ft.Colors.GREY_500,
                            weight="bold",
                        ),
                    ],
                ),
            ]
        )
    ]
    return content_column

def feeding_food_count(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = storage.get("customer_detail") or {}
    
    # dashboard_sync 경로 또는 기존 구조 양쪽 호환
    dash_data = customer_detail.get("dashboard_sync", {})
    if dash_data:
        first_customer_detail = dash_data
    elif customer_detail:
        first_key = next(iter(customer_detail.keys()), None)
        first_customer_detail = customer_detail.get(first_key, {}) if first_key else {}
    else:
        first_customer_detail = {}
    
    # 안전한 데이터 추출 (None 방어 + int 형변환)
    raw_food_count = first_customer_detail.get("left_food_count")
    try:
        feeding_food_count = int(raw_food_count) if raw_food_count is not None else 0
    except (ValueError, TypeError):
        feeding_food_count = 0
    
    now = datetime.datetime.now()
    if feeding_food_count > 0:
        days = datetime.timedelta(days=feeding_food_count)
        last_feeding_food_count = (now + days).strftime("%Y.%m.%d")
    else:
        last_feeding_food_count = "????.??.??"
    
    raw_left_intake = first_customer_detail.get("left_intake")
    try:
        left_intake = int(raw_left_intake) if raw_left_intake is not None else 0
    except (ValueError, TypeError):
        left_intake = 0
    
    raw_total_weight = first_customer_detail.get("total_weight")
    try:
        g_product_weight = int(raw_total_weight) if raw_total_weight is not None else 5
    except (ValueError, TypeError):
        g_product_weight = 5
    if g_product_weight == 0:
        g_product_weight = 5  # 0으로 나누기 방지
    
    kg_product_weight = float(g_product_weight / 1000)
    view_product_weight = (
        f"{kg_product_weight}Kg" if len(str(kg_product_weight).replace(".0", "")) > 2 
            else f"{g_product_weight}g"
    ) if g_product_weight > 5 else "???Kg"
    # ---------------------------------------------------------------------------------------------------
    # Feeding List First Product View
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="급여 중인 사료 잔여량", size=17, weight="bold"),
        ft.Row(
            controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan(f"{left_intake if left_intake != 0 else '???'}g", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan(f" / {view_product_weight}")
                ], color=ft.Colors.GREY_400, weight="bold", size=16),
                dogdog.flat_button(f"{feeding_food_count if feeding_food_count else '?'} 일치 남음", scale=0.7),
            ],
        ),
        ft.ProgressBar(
            height=10,
            value=left_intake / g_product_weight,
            bgcolor=ft.Colors.GREY_300,
            color=ft.Colors.YELLOW_600,
            border_radius=10,
        ),
        dogdog.basic_text(spans=[
            ft.TextSpan("예상 소진일 "),
            ft.TextSpan(last_feeding_food_count)
        ], size=12, color=ft.Colors.GREY_600),
    ]

    return content_column