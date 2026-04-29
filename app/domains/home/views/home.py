# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime


# -------------------------------------------------------------------------------------------------------
def now_history(page: ft.Page, popup):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    # ---------------------------------------------------------------------------------------------------
    # Popup Bottom Sheet
    # ---------------------------------------------------------------------------------------------------
    now_log_bottom_sheet = popup.bottom_sheet_popup
    now_log_bottom_sheet_contents = popup.bottom_sheet_controls

    # ---------------------------------------------------------------------------------------------------
    # Route Change Event
    # ---------------------------------------------------------------------------------------------------
    def history_event(e):
        now_log_bottom_sheet.open = False
        if storage.get("select_log_date"):
            storage.remove("select_log_date")
        page.go("/history")

    # ---------------------------------------------------------------------------------------------------
    # History Bottom Sheet Open
    # ---------------------------------------------------------------------------------------------------
    def now_history_open(e):
        now_log_bottom_sheet_contents.clear()
        history_title = dogdog.basic_text(
            f"오늘의 기록 : {now}", size=18, weight="bold"
        )
        now_log_bottom_sheet_contents.append(history_title)
        now_log_bottom_sheet_contents.append(ft.Divider())
        for pet_log_numeric_id, details in list(storage.get("history").items()):  # type: ignore
            if details["log_date"].split()[0] == now:
                now_log_bottom_sheet_contents.append(
                    dogdog.log_container(page, pet_log_numeric_id, details=details)
                )
        if len(now_log_bottom_sheet_contents) - 2 <= 0:
            now_log_bottom_sheet_contents.append(
                ft.Container(
                    padding=ft.Padding.only(right=10, left=10),
                    width=3000,
                    ink=True,
                    height=50,
                    border_radius=10,
                    border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            dogdog.basic_text(
                                "오늘의 기록이 없어요 ㅠㅠ",
                                size=14,
                                color=ft.Colors.GREY_700,
                            ),
                        ],
                    ),
                )
            )
        history_page = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.TextButton(
                    content=dogdog.basic_text(
                        "더보기", size=14, color=ft.Colors.GREY_500
                    ),
                    on_click=lambda e: history_event(e),
                )
            ],
        )
        now_log_bottom_sheet_contents.append(history_page)
        # ---------------------------------------------------------------------------------------------------
        if now_log_bottom_sheet not in page.overlay:
            page.overlay.append(now_log_bottom_sheet)
        else:
            page.overlay.clear()
            page.overlay.append(now_log_bottom_sheet)
        now_log_bottom_sheet.open = True
        page.update()

    # ---------------------------------------------------------------------------------------------------
    # 데이터 추출 및 초기화 (Cold Start 방어)
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = storage.get("customer_detail") or {}
    dash_data = customer_detail.get("dashboard_sync") or {}  # None 방지

    # [1] 오늘의 기록 상단 데이터 (Key 매핑: feeding_stats, activity_stats)
    query_date = dash_data.get(
        "query_date", datetime.datetime.now().strftime("%Y-%m-%d")
    )

    feeding_stats = dash_data.get("feeding_stats") or {}
    activity_stats = dash_data.get("activity_stats") or {}

    current_amount = feeding_stats.get("current_amount", 0)
    water_total = activity_stats.get("water_total", 0)
    walk_total = activity_stats.get("walk_total", 0)

    # [2] 목표 칼로리 및 진행률 계산
    current_kcal = feeding_stats.get("current_kcal", 0)
    target_kcal = feeding_stats.get("target_kcal", 0)
    progress_rate = feeding_stats.get("progress_rate", 0)

    # 0 나누기 방지 및 100분율 대응
    try:
        progress_val = float(progress_rate)
        kcal_progress_value = (
            progress_val / 100.0 if progress_val > 1.0 else progress_val
        )
    except (ValueError, TypeError, ZeroDivisionError):
        kcal_progress_value = 0.0

    content_column = [
        ft.Row(
            [
                dogdog.basic_text(value="오늘의 기록", size=18, weight="bold"),
                dogdog.basic_text(
                    value=now, size=14, weight="bold", color=ft.Colors.GREY_700
                ),
            ]
        ),
        ft.Row(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(f"급여량: {current_amount}g"),
                dogdog.flat_button(f"음수량: {water_total}ml"),
                dogdog.flat_button(f"산책: {walk_total}분"),
            ],
        ),
        ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                dogdog.basic_text(
                    value="목표 칼로리",
                    size=14,
                    color=ft.Colors.GREY_700,
                    weight="bold",
                ),
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
            ],
        ),
    ]
    # ---------------------------------------------------------------------------------------------------
    return dogdog.content_container(
        content_list=content_column, on_click=lambda e: now_history_open(e)
    )


def feeding_food_count(page: ft.Page, content_page):
    # ---------------------------------------------------------------------------------------------------
    # 데이터 추출 및 초기화 (Cold Start 방어)
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = storage.get("customer_detail") or {}
    dash_data = customer_detail.get("dashboard_sync") or {}

    inventory = dash_data.get("food_inventory") or {}

    # [1] 사료 잔여량 데이터 (Key 매핑: food_inventory)
    left_intake = inventory.get("left_intake", 0)
    total_weight_g = inventory.get("total_weight", 0)
    # 1600g -> 1.6Kg 변환
    total_weight_kg = round(float(total_weight_g) / 1000, 1)

    left_percent = inventory.get("left_percent", 0)
    progress_value = (
        float(left_percent) / 100 if left_percent > 1 else float(left_percent)
    )

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
                dogdog.basic_text(
                    spans=[
                        ft.TextSpan(
                            f"{left_intake if left_intake != 0 else '???'}g",
                            style=dogdog.TextStyle(size=16, height=-1),
                        ),
                        ft.TextSpan(f" / {total_weight_kg}Kg"),
                    ],
                    color=ft.Colors.GREY_400,
                    weight="bold",
                    size=16,
                ),
                dogdog.flat_button(
                    f"{round(left_days, 1) if round(left_days, 1) else '?'} 일치 남음",
                    scale=0.7,
                    disabled=True,
                ),
            ],
        ),
        ft.ProgressBar(
            height=10,
            value=progress_value,
            bgcolor=ft.Colors.GREY_300,
            color=ft.Colors.YELLOW_600 if content_page != "/shop" else "#E6001A",
            border_radius=10,
        ),
        dogdog.basic_text(
            spans=[ft.TextSpan("예상 소진일 "), ft.TextSpan(expected_exdate_formatted)],
            size=12,
            color=ft.Colors.GREY_600,
        ),
    ]
    # ---------------------------------------------------------------------------------------------------
    return content_column
