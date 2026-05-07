import flet as ft
import components as dogdog

def content_container(content_list, on_click=None):
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=10, bottom=10),
        on_click=on_click,
        ink=True,
        border_radius=ft.border_radius.all(10),
        border=ft.Border.all(width=2, color=ft.Colors.GREY_200),
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_100, offset=ft.Offset(x=0, y=3)),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_list
        )
    )

# select_log = {}
def log_container(page: ft.Page, pet_log_numeric_id, details):
    bgcolor = None
    
    def click_test(e):
        content.bgcolor = ft.Colors.GREY_300 if content.bgcolor == None else None
        content.update() # 클릭 시 색상 변경을 위해 꼭 필요합니다!

    # 1. 시간 및 날짜 변환 로직
    is_weekly = page.session.store.get("select_log_week") is not None
    display_time = details.get("display_time", "00:00")
    timestamp_raw = details.get("timestamp", "") # ISO Format (예: 2026-05-01T11:53:00)

    try:
        time_parts = display_time.split(":")
        hour = int(time_parts[0])
        minute = time_parts[1]
    except (ValueError, IndexError):
        hour = 0
        minute = "00"
    
    ampm = "오전" if hour < 12 else "오후"
    display_hour = hour if hour <= 12 else hour - 12
    if display_hour == 0: display_hour = 12
    
    # [해결] 시간 텍스트 생성
    log_time = f"{ampm} {display_hour}:{minute}"

    # [해결] 주간 모드일 경우 날짜(MM.DD) 추가
    if is_weekly and timestamp_raw:
        try:
            # ISO timestamp에서 월/일 추출 (예: 2026-05-01 -> 05.01)
            dt_part = timestamp_raw.split("T")[0]
            month_day = ".".join(dt_part.split("-")[1:3])
            log_time = f"{month_day} {log_time}"
        except:
            pass

    # 2. 메시지 변환 로직 (Domain 및 Category 분기 처리)
    domain = details.get("domain", "")
    category = details.get("category", "")  # numeric 도메인일 때 사용되는 세부 분류
    amount_raw = details.get("amount", 0)
    unit = details.get("unit", "")

    # [해결] 수치 데이터 포맷팅 (정수화 + 천 단위 콤마)
    try:
        amount_val = float(amount_raw)
        formatted_amount = f"{amount_val:,.0f}"
    except (ValueError, TypeError):
        formatted_amount = str(amount_raw)

    # 2-1. 사료(feeding)는 독자적인 도메인이므로 최우선 처리
    if domain == "feeding":
        product_name = details.get("product_name", "사료") 
        message = f"{product_name}를 {formatted_amount}{unit} 먹었습니다."

    # 2-2. numeric 도메인은 내부 category값에 따라 메시지 결정
    elif domain == "numeric":
        # 카테고리별 메시지 템플릿
        numeric_messages = {
            "water": f"물을 {formatted_amount}{unit} 마셨습니다.",
            "walk": f"산책을 {formatted_amount}분 했습니다.",
            "poop": f"배변 기록을 {formatted_amount}점 남겼습니다.",
            "bcs": f"BCS 기록을 {formatted_amount}점 남겼습니다.",
            "weight": f"체중 기록을 {amount_raw}kg 남겼습니다.", # 체중은 소수점 유지 (Kg 예외)
        }
        # 매핑된 메시지가 있으면 사용하고, 없으면 기본 방어 문구 출력
        message = numeric_messages.get(category, f"기록을 {formatted_amount}{unit} 남겼습니다.")

    # 2-3. 그 외 알 수 없는 도메인 방어 코드
    else:
        message = f"새로운 기록을 {formatted_amount}{unit} 남겼습니다."

    # 3. UI 조립
    content = ft.Container(
        padding=ft.Padding.only(right=10, left=10),
        width=3000,
        ink=False,
        on_click=click_test,
        bgcolor=bgcolor,
        height=50,
        border_radius=10,
        border=ft.Border.all(width=1, color=ft.Colors.GREY_300),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                dogdog.basic_text(message, size=14, color=ft.Colors.GREY_700),
                dogdog.basic_text(log_time, size=14, color=ft.Colors.GREY_700)
            ]
        )
    )
    
    return content