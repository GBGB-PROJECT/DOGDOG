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
        history_title = dogdog.basic_text(f"오늘의 기록 : {now}", size=18, weight="bold")
        now_log_bottom_sheet_contents.append(history_title)
        now_log_bottom_sheet_contents.append(ft.Divider())
        for pet_log_numeric_id , details in list(storage.get("history").items()): # type: ignore
            if details["log_date"].split()[0] == now:
                now_log_bottom_sheet_contents.append(
                    dogdog.log_container(page, pet_log_numeric_id, details=details))
        if len(now_log_bottom_sheet_contents) - 2 <= 0:
            now_log_bottom_sheet_contents.append(ft.Container(
                padding=ft.Padding.only(right=10, left=10),
                width=3000,
                ink=True,
                height=50,
                border_radius=10,
                border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                    dogdog.basic_text("오늘의 기록이 없어요 ㅠㅠ", size=14, color=ft.Colors.GREY_700),
            ])))
        history_page = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.TextButton(
                content=dogdog.basic_text(
                    "더보기", size=14,color=ft.Colors.GREY_500), on_click=lambda e:history_event(e))
        ])
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
    # Now History View (제작중)
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Row([dogdog.basic_text(value="오늘의 기록", size=18, weight="bold"),
                dogdog.basic_text(value=now, size=14, weight="bold", color=ft.Colors.GREY_700)]),
        ft.Row(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button("급여량: 100g", scale=0.8, disabled=True),
                dogdog.flat_button("음수량: 100ml", scale=0.8, disabled=True),
                dogdog.flat_button("산책: 60분")], scale=0.8, disabled=True),
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
    # ---------------------------------------------------------------------------------------------------
    return dogdog.content_container(
        content_list=content_column,
        on_click=lambda e: now_history_open(e))

def feeding_food_count(page: ft.Page, content_page):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    customer_detail = (storage.get("customer_detail"))
    first_customer_detail = customer_detail.get(next(iter(customer_detail.keys()))) if customer_detail else None
    feeding_food_count = first_customer_detail.get("left_food_count") if customer_detail else 0 # type: ignore
    now = datetime.datetime.now()
    days = datetime.timedelta(days=feeding_food_count) if customer_detail else 0
    last_feeding_food_count = (now+days).strftime("%Y.%m.%d") if days != 0 else "????.??.??"
    left_intake = first_customer_detail.get("left_intake") if customer_detail else 0 # type: ignore
    g_product_weight = first_customer_detail.get("total_weight") if customer_detail else 5 # type: ignore
    kg_product_weight = float(g_product_weight / 1000)
    view_product_weight = (
        f"{kg_product_weight}Kg" if len(str(kg_product_weight).replace(".0", "")) > 2 
            else f"{g_product_weight}g"
    ) if customer_detail else "???Kg"
    # ---------------------------------------------------------------------------------------------------
    # Feeding List First Product View
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="급여 중인 사료 잔여량", size=17, weight="bold"),
        ft.Row(
            controls=[
                dogdog.basic_text(spans=[
                    ft.TextSpan(f"{left_intake if left_intake != 0 else '???'}g", style=dogdog.TextStyle(size=16, height=-1)),
                    ft.TextSpan(f" / {view_product_weight}")
                ], color=ft.Colors.GREY_400, weight="bold", size=16),
                dogdog.flat_button(f"{feeding_food_count if feeding_food_count else '?'} 일치 남음", scale=0.7, disabled=True),
            ],
        ),
        ft.ProgressBar(
            height=10,
            value=left_intake / g_product_weight,
            bgcolor=ft.Colors.GREY_300,
            color=ft.Colors.YELLOW_600 if content_page != "/shop" else "#E6001A",
            border_radius=10,
        ),
        dogdog.basic_text(spans=[
            ft.TextSpan("예상 소진일 "),
            ft.TextSpan(last_feeding_food_count)
        ], size=12, color=ft.Colors.GREY_600),
    ]
    # ---------------------------------------------------------------------------------------------------
    return content_column