# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime
# -------------------------------------------------------------------------------------------------------
def now_history(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    # 데이터 추출 및 초기화
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = storage.get("customer_detail") or {}
    dash_data = customer_detail.get("dashboard_sync", {})

    # [1] 오늘의 기록 상단 데이터
    query_date = dash_data.get("query_date", datetime.datetime.now().strftime("%Y-%m-%d"))
    query_date_formatted = str(query_date).replace("-", ".")

    feeding_stats = dash_data.get("feeding_stats", {})
    activity_stats = dash_data.get("activity_stats", {})

    current_amount = feeding_stats.get("current_amount", 0)
    water_total = activity_stats.get("water_total", 0)
    walk_total = activity_stats.get("walk_total", 0)

    # [2] 목표 칼로리 데이터
    current_kcal = feeding_stats.get("current_kcal", 0)
    target_kcal = feeding_stats.get("target_kcal", 0)
    # progress_rate가 100분율(예: 78)로 올 경우 대비하여 100으로 나눔
    progress_rate = feeding_stats.get("progress_rate", 0)
    kcal_progress_value = float(progress_rate) / 100 if progress_rate > 1 else float(progress_rate)

    content_column = [
        ft.Row([
            dogdog.basic_text(value="오늘의 기록", size=18, weight="bold"),
            dogdog.basic_text(value=query_date_formatted, size=14, weight="bold", color=ft.Colors.GREY_700),
        ]),
        ft.Row(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(f"급여량: {current_amount}g"),
                dogdog.flat_button(f"음수량: {water_total}ml"),
                dogdog.flat_button(f"산책: {walk_total}분"),
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
                            value=kcal_progress_value,
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.YELLOW_600,
                            border_radius=10,
                        ),
                        dogdog.basic_text(
                            value=f"{current_kcal} / {target_kcal}kcal",
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
    # 데이터 추출 및 초기화
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = storage.get("customer_detail") or {}
    dash_data = customer_detail.get("dashboard_sync", {})
    
    inventory = dash_data.get("food_inventory", {})
    
    # [1] 사료 잔여량 데이터
    left_intake = inventory.get("left_intake", 0)
    total_weight_g = inventory.get("total_weight", 0)
    # 1600g -> 1.6Kg 변환
    total_weight_kg = round(float(total_weight_g) / 1000, 1)
    
    left_percent = inventory.get("left_percent", 0)
    progress_value = float(left_percent) / 100 if left_percent > 1 else float(left_percent)
    
    # [2] 남은 일수 및 소진일
    left_days = inventory.get("left_food_count", 0)
    expected_exdate = inventory.get("expected_exdate", "????-??-??")
    expected_exdate_formatted = str(expected_exdate).replace("-", ".")
    
    # ---------------------------------------------------------------------------------------------------
    # UI 조립
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="급여 중인 사료 잔여량", size=17, weight="bold"),
        ft.Row(
            controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan(f"{left_intake}g", style=dogdog.TextStyle(size=16)),
                    ft.TextSpan(f" / {total_weight_kg}Kg")
                ], color=ft.Colors.GREY_400, weight="bold", size=16),
                dogdog.flat_button(f"{round(left_days, 1)} 일치 남음", scale=0.7),
            ],
        ),
        ft.ProgressBar(
            height=10,
            value=progress_value,
            bgcolor=ft.Colors.GREY_300,
            color=ft.Colors.YELLOW_600,
            border_radius=10,
        ),
        dogdog.basic_text(spans=[
            ft.TextSpan("예상 소진일 "),
            ft.TextSpan(expected_exdate_formatted)
        ], size=12, color=ft.Colors.GREY_600),
    ]

    return content_column