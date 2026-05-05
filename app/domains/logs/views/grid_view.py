import flet as ft
import components as dogdog
import datetime
from domains.logs.controller.status_controller import StatusController

# -------------------------------------------------------------------------------------------------------
async def bottom_sheet(e, page: ft.Page, popup, call, on_refresh_callback=None, edit_mode=False, log_data=None):
    """
    [View] bottom_sheet
    역할: 그리드 메뉴 클릭 시 열리는 하단 팝업 UI를 생성합니다.
    - StatusController를 인스턴스화하여 비즈니스 로직 및 상태 변경을 위임합니다.
    - 데이터 조회는 컨트롤러에서 수행하며, 이 뷰는 반환된 데이터로 시각적 요소만 렌더링합니다.
    """
    # [Step 2] 기존 피커 찌꺼기 완벽 제거 (렉 방지)
    pickers_to_remove = [c for c in page.overlay if isinstance(c, (ft.DatePicker, ft.TimePicker))]
    for p in pickers_to_remove:
        page.overlay.remove(p)
    page.update()

    s_control = StatusController(page=page, popup=popup, on_refresh_callback=on_refresh_callback, edit_mode=edit_mode, log_data=log_data)
    s_control.set_default_datetime(call)
    
    bottom_sheet_contents = popup.bottom_sheet_controls
    bottom_sheet_contents.clear()
    
    # [버그 1 수정] 정규식(Regex) 기반 절대 에러 안 나는 파서 + Storage 동기화
    # 핵심 원인:
    #   1. fromisoformat이 "2026-05-02 11:08:00.000000" 같은 포맷 수신 시 에러 투스
    #   2. 파싱 성공해도 Storage에 동기화되지 않아 저장 시 시간이 날아건
    # 해결: re 모듈로 날짜/시간을 각각 독립적으로 추출 → 파싱 후 Storage에 즉시 반영
    import re
    initial_date, initial_time = datetime.datetime.now(), datetime.datetime.now()

    if edit_mode and log_data:
        log_str = str(log_data)

        # 1. 날짜 추출 (YYYY-MM-DD 또는 YYYY.MM.DD 패턴 중 첫 번째)
        date_match = re.search(r"(\d{4}[-.\s]\d{2}[-.\s]\d{2})", log_str)
        if date_match:
            try:
                d_str = date_match.group(1).replace(".", "-").replace(" ", "-")
                initial_date = datetime.datetime.strptime(d_str, "%Y-%m-%d")
                # initial_time의 날짜도 일치시켜 주기 (나중에 시간만 replace하면 사용)
                initial_time = initial_time.replace(
                    year=initial_date.year,
                    month=initial_date.month,
                    day=initial_date.day,
                )
            except Exception:
                pass

        # 2. 시간 추출 (HH:MM:SS 또는 HH:MM 패턴 중 첫 번째)
        time_matches = re.findall(r"([0-2]\d:[0-5]\d(?::[0-5]\d)?)", log_str)
        if time_matches:
            try:
                t_parts = time_matches[0].split(":")
                h = int(t_parts[0])
                m = int(t_parts[1])
                s = int(t_parts[2]) if len(t_parts) > 2 else 0
                initial_time = initial_time.replace(hour=h, minute=m, second=s, microsecond=0)
            except Exception:
                pass

    # [핵심] 파싱된 날짜/시간을 Storage에 강제 동기화
    # 유저가 피커를 건드리지 않아도 저장 시 올바른 시간이 전달됨
    s_control.storage.set(f"{call}_date", initial_date.strftime("%Y-%m-%d"))
    s_control.storage.set(f"{call}_time", initial_time.strftime("%H:%M"))


    # 안전한 피커 생성
    date_picker = ft.DatePicker(
        first_date=datetime.datetime.now() - datetime.timedelta(days=365),
        last_date=datetime.datetime.now(), # 오늘까지만 선택 (내일 선택 방지 유지)
        value=initial_date
    )
    
    time_picker = ft.TimePicker(
        entry_mode=ft.TimePickerEntryMode.DIAL_ONLY,
        value=initial_time.time()
    )

    # [수정] 중복 방지를 위해 기존 피커 찾아서 안전하게 제거 (page.overlay는 할당이 불가능함)
    pickers_to_remove = [c for c in page.overlay if isinstance(c, (ft.DatePicker, ft.TimePicker))]
    for p in pickers_to_remove:
        page.overlay.remove(p)
        
    # 새 피커 추가
    page.overlay.append(date_picker)
    page.overlay.append(time_picker)

    def open_picker(e, picker):
        picker.open = True
        page.update()

    data_button = dogdog.flat_icon_text_button(
        ft.Icons.CALENDAR_MONTH, initial_date.strftime("%Y.%m.%d")
    )
    data_button.on_click = lambda e: open_picker(e, date_picker)

    time_button = dogdog.flat_icon_text_button(
        ft.Icons.ACCESS_TIME,
        initial_time.strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후"),
    )
    time_button.on_click = lambda e: open_picker(e, time_picker)

    # 피커 on_change 이벤트 바인딩 (팝업 업데이트 강제)
    def on_date_change(e):
        formatted = s_control.change_date(call, date_picker.value)
        if formatted:
            data_button.content.controls[1].value = formatted
            # 버튼이 포함된 Row나 Container를 명시적으로 업데이트하거나 전체 팝업 업데이트
            popup.bottom_sheet_popup.update()

    def on_time_change(e):
        formatted = s_control.change_time(call, time_picker.value)
        if formatted:
            time_button.content.controls[1].value = formatted
            popup.bottom_sheet_popup.update()

    date_picker.on_change = on_date_change
    time_picker.on_change = on_time_change

    # ... (add_title, open_guide 함수 생략 - 기존 코드 유지됨)

    # 공통 헬퍼: 타이틀
    def add_title(text, guide_route=None):
        if guide_route:
            bottom_sheet_contents.append(
                ft.Row(
                    spacing=5,
                    controls=[
                        dogdog.basic_text(value=text, size=25, weight="bold"),
                        ft.Container(
                            scale=0.8, width=25, height=25, ink=True,
                            on_click=lambda e: open_guide(e, guide_route),
                            border_radius=25, bgcolor=ft.Colors.GREY_300,
                            content=ft.Icon(icon=ft.Icons.QUESTION_MARK, color=ft.Colors.WHITE, size=20),
                        ),
                    ],
                )
            )
        else:
            bottom_sheet_contents.append(dogdog.basic_text(value=text, size=25, weight="bold"))
        bottom_sheet_contents.append(ft.Divider())

    # 가이드 바텀 시트 (BCS, 배변 스코어)
    guide_bottom_sheet_content = []
    guide_page = dogdog.bottom_sheet(content=guide_bottom_sheet_content)
    
    def open_guide(e, route):
        if guide_page not in page.overlay:
            page.overlay.append(guide_page)
        guide_bottom_sheet_content.clear()
        title_text = "배변 스코어란?" if route == "bowel" else "BCS 란?"
        guide_bottom_sheet_content.append(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    dogdog.basic_text(title_text, size=25, weight="bold"),
                    dogdog.flat_button("닫기", on_click=lambda _: setattr(guide_page, 'open', False), scale=0.8),
                ],
            )
        )
        guide_bottom_sheet_content.append(ft.Divider())
        import domains # guide_view 등을 위해 필요
        guide_bottom_sheet_content.append(
            ft.Column(
                expand=True, scroll=ft.ScrollMode.HIDDEN,
                controls=[domains.guide.what_guide(page=page, content=route)],
            )
        )
        guide_page.open = True
        page.update()

    # [해결] 인라인 에러 메시지 필드 생성
    error_message_field = ft.Text(value="", color=ft.Colors.RED_400, size=12, visible=False)
    s_control.error_field = error_message_field # 컨트롤러와 연결

    # 공통 하단 컨트롤 (날짜/시간 및 취소/저장 버튼)
    def add_bottom_controls(is_customer_detail, visible=True):
        if is_customer_detail:
            # 1. 날짜/시간 표시줄
            bottom_sheet_contents.append(
                ft.Row(
                    spacing=30, alignment=ft.MainAxisAlignment.CENTER, 
                    controls=[data_button, time_button],
                    visible=visible
                )
            )
            # 2. 에러 필드
            bottom_sheet_contents.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER, 
                    controls=[error_message_field],
                    visible=visible
                )
            )
            # 3. 취소/저장 버튼
            bottom_sheet_contents.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    visible=visible,
                    controls=[
                        dogdog.flat_button(
                            "취소", scale=1,
                            on_click=lambda _: setattr(popup.bottom_sheet_popup, 'open', False)
                        ),
                        dogdog.flat_button(
                            "저장", scale=1, bgcolor="#FEF3B9",
                            on_click=lambda _: page.run_task(s_control.save_event, call)
                        ),
                    ],
                )
            )

    is_customer_detail = True
    has_food = True # 기본값 (feeding 외 카테고리는 항상 True)

    def get_real_val(*keys):
        if not edit_mode or not log_data: return ""
        for k in keys + ("amount", "log_status", "weight", "bcs", "score", "value"):
            v = log_data.get(k)
            if v is not None and str(v).strip() not in ["", "0", "0.0", "None"]:
                return v
        return ""
    
    if call == "feeding":
        add_title("밥주기")
        data = await s_control.fetch_feeding_init_data()
        has_food = data.get("has_food", False)
        
        # [UI] 사료가 있을 때 노출되는 영역
        feeding_guide = ft.Column(
            visible=has_food,
            alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
            controls=[
                ft.Row(
                    margin=ft.margin.only(bottom=10),
                    controls=[dogdog.basic_text(f"오늘 {data['pet_name']}에게 딱 알맞는 1회 급여량은 ...", size=16, weight="bold", color=ft.Colors.GREY_600)],
                ),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=-90,
                    controls=[
                        ft.Image(src="speech_bubble.png", height=100, color="#FEF3B9"),
                        dogdog.basic_text(f"{data['recommended_amount']}g", weight="bold", size=40),
                    ],
                ),
                ft.Image(src="dogbowl.png", height=100, margin=ft.margin.only(top=20)),
            ],
        )
        
        food_options = [dogdog.dropdown_menu_option(key=item["key"], text=item["text"]) for item in data.get("food_options_data", [])]
        food_dropdown = dogdog.dropdown_menu(
            label="사료를 선택해주세요.",
            options=food_options,
            event=lambda e: s_control.change_customer_food_id(e.control.value),
        )
        # [해결] 커스텀 컴포넌트 대신 Row/Container에 visible 속성 부여
        food_dropdown_wrap = ft.Row(controls=[food_dropdown], visible=has_food)
        
        # 수정 모드 프리필
        if edit_mode and log_data:
            food_id = log_data.get("pet_food_id")
            food_dropdown.value = str(food_id) if food_id else data.get("initial_value")
            amount_val = log_data.get("amount")
            initial_weight = str(int(amount_val)) if amount_val is not None else ""
            initial_memo = log_data.get("memo", "")
        else:
            food_dropdown.value = data.get("initial_value")
            initial_weight = str(int(data.get("recommended_amount", 0)))
            initial_memo = ""

        feeding_weight = dogdog.input_textfield(
            hint_text="급여량(g)을 입력하세요.", input_type="int", suffix="g",
            on_change=lambda e: s_control.change_weight(call, e.control.value),
        )
        feeding_weight.value = initial_weight
        # [해결] 래핑 컨테이너로 가시성 제어
        feeding_weight_wrap = ft.Container(content=feeding_weight, visible=has_food)

        feeding_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value),
        )
        feeding_memo.value = initial_memo
        # [해결] 래핑 컨테이너로 가시성 제어
        feeding_memo_wrap = ft.Container(content=feeding_memo, visible=has_food)
        
        if has_food:
            s_control.change_customer_food_id(food_dropdown.value)
            s_control.change_weight(call, initial_weight if initial_weight else "0")
            s_control.change_memo(call, initial_memo)

        # [UI] 사료가 없을 때 노출되는 Empty State 영역
        not_customer_detail = ft.Column(
            visible=not has_food,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(height=20),
                ft.Row(
                    height=80, alignment=ft.MainAxisAlignment.CENTER,
                    controls=[dogdog.basic_text("등록된 상품이 없습니다.", size=16, weight="bold", color=ft.Colors.GREY_600)],
                ),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    controls=[
                        dogdog.flat_button(
                            "나중에 등록할게요", 
                            on_click=lambda _: setattr(popup.bottom_sheet_popup, 'open', False)
                        ),
                        dogdog.flat_button(
                            "등록하러가기", 
                            bgcolor="#FEF3B9", 
                            on_click=lambda _: page.go("/feeding")
                        ),
                    ]
                ),
                ft.Container(height=20),
            ]
        )

        bottom_sheet_contents.extend([
            feeding_guide, 
            food_dropdown_wrap, 
            feeding_weight_wrap, 
            feeding_memo_wrap,
            not_customer_detail
        ])

    elif call == "watering":
        add_title("물주기")
        val_raw = get_real_val("amount", "log_status")
        initial_val = str(int(float(val_raw))) if val_raw else ""
        initial_memo = log_data.get("memo", "") if edit_mode and log_data else ""
        
        watering = dogdog.input_textfield(
            hint_text="물 섭취량을 적어주세요.", input_type="int", suffix="ml",
            on_change=lambda e: s_control.change_weight(call, e.control.value),
        )
        watering.value = initial_val
        watering_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value),
        )
        watering_memo.value = initial_memo
        bottom_sheet_contents.extend([watering, watering_memo])

    elif call == "daily_walks":
        add_title("활동기록")
        val_raw = get_real_val("amount", "log_status")
        initial_val = str(int(float(val_raw))) if val_raw else ""
        initial_memo = log_data.get("memo", "") if edit_mode and log_data else ""

        daily_walks = dogdog.input_textfield(
            hint_text="산책시간을 적어주세요.", input_type="int", suffix="분",
            on_change=lambda e: s_control.change_weight(call, e.control.value),
        )
        daily_walks.value = initial_val
        daily_walks_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value),
        )
        daily_walks_memo.value = initial_memo
        bottom_sheet_contents.extend([daily_walks, daily_walks_memo])

    elif call == "hygiene_bowel":
        add_title("배변", "bowel")
        val_raw = get_real_val("log_status", "score")
        initial_val = str(int(float(val_raw))) if val_raw else None
        initial_memo = log_data.get("memo", "") if edit_mode and log_data else ""

        hygiene_bowel_score = dogdog.dropdown_menu(
            label="배변 스코어를 선택해주세요.",
            options=[dogdog.dropdown_menu_option(text=f"{row}") for row in range(1, 8)],
            event=lambda e: s_control.change_weight(call, e.control.value),
        )
        hygiene_bowel_score.value = initial_val
        
        hygiene_bowel_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value),
        )
        hygiene_bowel_memo.value = initial_memo
        bottom_sheet_contents.extend([hygiene_bowel_score, hygiene_bowel_memo])

    elif call == "health_log":
        initial_weight = ""
        initial_bcs = None
        category = ""
        
        if edit_mode and log_data:
            category = log_data.get("category", "")
            # [해결 1] get_real_val을 사용하여 안전하게 추출 및 예외 처리 (크래시 방지)
            status_val = get_real_val("log_status", "weight", "bcs", "value")
            
            try:
                if category == "weight" and status_val:
                    initial_weight = str(float(status_val))
                elif category == "bcs" and status_val:
                    initial_bcs = str(int(float(status_val)))
            except (ValueError, TypeError):
                pass

        health_weight_field = dogdog.input_textfield(
            hint_text="몸무게를 적어주세요.", input_type="float", suffix="Kg",
            on_change=lambda e: s_control.change_weight(call, e.control.value, is_float=True),
        )
        health_weight_field.value = initial_weight
        
        health_bcs_dropdown = dogdog.dropdown_menu(
            label="BCS를 선택해주세요.",
            options=[dogdog.dropdown_menu_option(text=f"{row}") for row in range(9, 0, -1)],
            event=lambda e: s_control.change_weight(call, e.control.value, is_bcs=True),
        )
        health_bcs_dropdown.value = initial_bcs
        
        # [해결] 수정 모드 시 분리된 필드들의 초기값을 Storage에 즉시 강제 세팅 (데이터 단절 복구)
        if edit_mode and log_data:
            if category == "weight":
                s_control.change_weight(call, initial_weight, is_float=True)
            elif category == "bcs":
                s_control.change_weight(call, initial_bcs, is_bcs=True)

        # [핵심] edit_mode일 때 카테고리에 따라 UI 분리
        if edit_mode and category == "weight":
            add_title("건강기록 (체중)")
            bottom_sheet_contents.extend([health_weight_field])
        elif edit_mode and category == "bcs":
            add_title("건강기록 (BCS)", "bcs")
            bottom_sheet_contents.extend([health_bcs_dropdown])
        else:
            add_title("건강기록", "bcs")
            bottom_sheet_contents.extend([health_weight_field, health_bcs_dropdown])

    elif call == "status_log":
        add_title("상태기록")
        # [Step 1 해결] edit_mode와 log_data가 있을 때만 값 추출
        if edit_mode and log_data:
            initial_memo = log_data.get("memo", "")
        else:
            initial_memo = ""

        status_log_field = dogdog.input_textfield(
            hint_text="기타상태를 작성해주세요.", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value),
        )
        status_log_field.value = initial_memo
        bottom_sheet_contents.extend([status_log_field])

    # 하단 버튼 조립 (has_food 상태에 따라 노출 제어)
    add_bottom_controls(is_customer_detail, visible=has_food)

    # 오버레이 제어 및 팝업 열기
    if popup.bottom_sheet_popup not in page.overlay:
        page.overlay.append(popup.bottom_sheet_popup)
    else:
        # [수정] page.overlay.clear()는 피커(DatePicker 등)까지 지워버리므로 사용 금지.
        # 대신 팝업이 이미 있다면 덮어쓰지 않고 바로 엽니다.
        pass
        
    popup.bottom_sheet_popup.open = True
    page.update()

# -------------------------------------------------------------------------------------------------------
def status_update_menu(page: ft.Page, popup, on_refresh_callback=None):
    """
    [View] status_update_menu
    역할: 6개의 그리드 버튼 메뉴 UI를 생성합니다.
    """
    content_list_top = [
        ("밥주기", "dogbowl.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "feeding", on_refresh_callback)),
        ("물주기", "waterdrop.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "watering", on_refresh_callback)),
        ("활동기록", "dogwalking.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "daily_walks", on_refresh_callback)),
    ]
    content_list_bottom = [
        ("배변", "poop.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "hygiene_bowel", on_refresh_callback)),
        ("건강기록", "injection.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "health_log", on_refresh_callback)),
        ("상태기록", "note.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "status_log", on_refresh_callback)),
    ]
    
    content_column = [
        ft.Row(controls=[dogdog.icon_flat_button(text=t, icon=i, on_click=o) for t, i, o in content_list_top]),
        ft.Row(controls=[dogdog.icon_flat_button(text=t, icon=i, on_click=o) for t, i, o in content_list_bottom]),
    ]
    
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20),
        bgcolor="#ffffff",
        content=ft.Column(controls=content_column),
    )
