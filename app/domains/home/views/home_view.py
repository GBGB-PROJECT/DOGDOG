# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime

# -------------------------------------------------------------------------------------------------------
def open_now_history_popup(page: ft.Page, popup, history_logs: list):
    """
    오늘의 기록 팝업(타임라인)을 열고, 주입받은 API 로그 데이터를 렌더링합니다.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    now_log_bottom_sheet = popup.bottom_sheet_popup
    now_log_bottom_sheet_contents = popup.bottom_sheet_controls

    def history_event(e):
        now_log_bottom_sheet.open = False
        if page.session.store.get("select_log_date"):
            page.session.store.remove("select_log_date")
        
        # [Step 3] 이동 직전 오버레이 강제 청소 (잔상 방지)
        page.overlay.clear()
        page.update()
        
        page.go("/history")

    now_log_bottom_sheet_contents.clear()
    history_title = dogdog.basic_text(
        f"오늘의 기록 : {now}", size=18, weight="bold"
    )
    now_log_bottom_sheet_contents.append(history_title)
    now_log_bottom_sheet_contents.append(ft.Divider())
    
    # 컨트롤러가 주입한 history_logs 사용 (API 배열 데이터 반복)
    for log in history_logs[:4]:
        now_log_bottom_sheet_contents.append(
            dogdog.log_container(page, log.get('id'), details=log)
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
                        dogdog.basic_text("오늘의 기록이 없어요 ㅠㅠ", size=14, color=ft.Colors.GREY_700),
                    ],
                ),
            )
        )
        
    history_page = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.TextButton(
                content=dogdog.basic_text("더보기", size=14, color=ft.Colors.GREY_500),
                on_click=lambda e: history_event(e),
            )
        ],
    )
    now_log_bottom_sheet_contents.append(history_page)
    
    if now_log_bottom_sheet not in page.overlay:
        page.overlay.append(now_log_bottom_sheet)
    else:
        page.overlay.clear()
        page.overlay.append(now_log_bottom_sheet)
    now_log_bottom_sheet.open = True
    page.update()

def now_history(page: ft.Page, popup, stats_data: dict, history_logs: list, on_click=None):
    """
    오늘의 기록 뷰 컴포넌트 (순수 View)
    - 컨트롤러가 제공한 stats_data와 history_logs만 사용하여 렌더링합니다.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d")

    # ---------------------------------------------------------------------------------------------------
    # UI 조립 (데이터는 컨트롤러에서 주입)
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        ft.Row(
            [
                dogdog.basic_text(value="오늘의 기록", size=18, weight="bold"),
                dogdog.basic_text(value=now, size=14, weight="bold", color=ft.Colors.GREY_700),
            ]
        ),
        ft.Row(
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                dogdog.flat_button(f"급여량: {int(stats_data.get('current_amount', 0))}g", disabled=True, scale=0.8),
                dogdog.flat_button(f"음수량: {int(stats_data.get('water_total', 0))}ml", disabled=True, scale=0.8),
                dogdog.flat_button(f"산책: {int(stats_data.get('walk_total', 0))}분", disabled=True, scale=0.8),
            ],
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
                            value=stats_data.get('kcal_progress_value', 0.0),
                            bgcolor=ft.Colors.GREY_300,
                            color=ft.Colors.YELLOW_600,
                            border_radius=10,
                        ),
                        dogdog.basic_text(
                            value=f"{int(stats_data.get('current_kcal', 0)):,} / {int(stats_data.get('target_kcal', 0)):,}kcal",
                            size=12,
                            color=ft.Colors.GREY_500,
                            weight="bold",
                        ),
                    ],
                ),
            ],
        ),
    ]
    return dogdog.content_container(content_list=content_column, on_click=on_click)


def feeding_food_count(page: ft.Page, content_page: str, inventory_stats: dict):
    """
    사료 잔여량 뷰 컴포넌트 (순수 View)
    - 컨트롤러가 제공한 inventory_stats를 사용하여 렌더링합니다.
    """
    progress_value = inventory_stats.get('progress_value', 0.0)
    
    content_column = [
        dogdog.basic_text(value="급여 중인 사료 잔여량", size=17, weight="bold"),
        ft.Row(
            controls=[
                dogdog.basic_text(
                    spans=[
                        ft.TextSpan(
                            f"{int(inventory_stats.get('left_intake', 0)):,}g",
                            style=dogdog.TextStyle(size=16, height=-1),
                        ),
                        ft.TextSpan(f" / {inventory_stats.get('total_weight_kg', 0.0)}Kg"),
                    ],
                    color=ft.Colors.GREY_400,
                    weight="bold",
                    size=16,
                ),
                dogdog.flat_button(
                    (
                        f"{int(float(inventory_stats.get('left_days', 0))):,} 일치 남음"
                        if str(inventory_stats.get('left_days')).replace('.', '').isdigit()
                        else f"{inventory_stats.get('left_days', '0')} 일치 남음"
                    ),
                    scale=0.7,
                    disabled=True,
                ),
            ],
        ),
        ft.ProgressBar(
            height=10,
            value=progress_value,
            bgcolor=ft.Colors.GREY_300,
            color="#E6001A" if progress_value < 0.2 else ft.Colors.YELLOW_600,
            border_radius=10,
        ),
        dogdog.basic_text(
            spans=[ft.TextSpan("예상 소진일 "), ft.TextSpan(inventory_stats.get('expected_exdate_formatted', '????.??.??'))],
            size=12,
            color=ft.Colors.GREY_600,
        ),
    ]
    return content_column
