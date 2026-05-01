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
    s_control = StatusController(page=page, popup=popup, on_refresh_callback=on_refresh_callback, edit_mode=edit_mode, log_data=log_data)
    s_control.set_default_datetime(call)
    
    bottom_sheet_contents = popup.bottom_sheet_controls
    bottom_sheet_contents.clear()
    
    # 날짜/시간 초기화 로직 (수정 모드 대응)
    initial_date = datetime.datetime.now()
    initial_time = datetime.datetime.now()
    
    if edit_mode and log_data:
        raw_date = log_data.get("log_date") or log_data.get("date")
        if raw_date:
            try:
                # "2024-05-12 13:23" 또는 ISO 형식 지원
                initial_dt = datetime.datetime.fromisoformat(raw_date.replace(" ", "T"))
                initial_date = initial_dt
                initial_time = initial_dt
            except: pass

    # 공통 UI 컴포넌트: 피커
    date_picker = ft.DatePicker(
        first_date=datetime.datetime.now() - datetime.timedelta(days=365), # 수정 시 과거 기록도 가능하도록 범위 확대
        last_date=datetime.datetime.now() + datetime.timedelta(days=1),
        value=initial_date
    )
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)
        
    time_picker = ft.TimePicker(
        entry_mode=ft.TimePickerEntryMode.DIAL_ONLY,
        value=initial_time.time()
    )
    if time_picker not in page.overlay:
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

    # 공통 하단 컨트롤
    def add_bottom_controls(is_customer_detail):
        if is_customer_detail:
            bottom_sheet_contents.append(
                ft.Row(spacing=30, alignment=ft.MainAxisAlignment.CENTER, controls=[data_button, time_button])
            )
            bottom_sheet_contents.append(
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
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

    # ---------------------------------------------------------------------------------------------------
    # 상태별 화면 구성 (분기)
    # ---------------------------------------------------------------------------------------------------
    if call == "feeding":
        add_title("밥주기")
        data = await s_control.fetch_feeding_init_data()
        
        if data["has_food"]:
            feeding_guide = dogdog.basic_text("급여할 사료와 양을 확인해주세요.", size=14, color=ft.Colors.GREY_600)
            food_options = [dogdog.dropdown_menu_option(key=item["key"], text=item["text"]) for item in data["food_options_data"]]
            food_dropdown = dogdog.dropdown_menu(
                label="사료를 선택해주세요.",
                options=food_options,
                event=lambda e: s_control.change_customer_food_id(e.control.value),
            )
            
            # 수정 모드 프리필
            if edit_mode and log_data:
                food_id = log_data.get("pet_food_id")
                food_dropdown.value = str(food_id) if food_id else data["initial_value"]
                
                # [문제 4 해결] amount가 0이거나 None일 때의 처리 개선
                amount_val = log_data.get("amount")
                initial_weight = str(int(amount_val)) if amount_val is not None else ""
                initial_memo = log_data.get("memo", "")
            else:
                food_dropdown.value = data["initial_value"]
                initial_weight = str(int(data["recommended_amount"]))
                initial_memo = ""

            feeding_weight = dogdog.input_textfield(
                hint_text="급여량(g)을 입력하세요.", input_type="int", suffix="g",
                on_change=lambda e: s_control.change_weight(call, e.control.value),
            )
            feeding_weight.value = initial_weight

            feeding_memo = dogdog.input_textfield(
                hint_text="메모 (선택)", text_filter=None, max_length=None,
                on_change=lambda e: s_control.change_memo(call, e.control.value),
            )
            feeding_memo.value = initial_memo
            
            # [문제 1 해결] 모든 컴포넌트가 정의된 후 if 블록 안에서 extend 실행
            bottom_sheet_contents.extend([feeding_guide, ft.Row(controls=[food_dropdown]), feeding_weight, feeding_memo])
        else:
            # 기존 "등록된 제품이 없습니다" 로직 유지
            not_customer_detail = ft.Row(
                height=100, alignment=ft.MainAxisAlignment.CENTER,
                controls=[dogdog.basic_text("등록된 제품이 없습니다.", size=16, weight="bold", color=ft.Colors.GREY_600)],
            )
            def go_to_add(e):
                popup.bottom_sheet_popup.open = False
                page.update()
                page.go("/feeding_add")

            setting = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Column(
                        spacing=20, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            dogdog.flat_button("등록하러가기", bgcolor="#FEF3B9", on_click=go_to_add),
                            dogdog.flat_button("나중에 등록할께요", on_click=lambda _: setattr(popup.bottom_sheet_popup, 'open', False)),
                        ]
                    )
                ],
            )
            bottom_sheet_contents.extend([not_customer_detail, setting])

    elif call == "watering":
        add_title("물주기")
        # [Step 1 해결] edit_mode와 log_data가 있을 때만 값 추출
        if edit_mode and log_data:
            status_val = log_data.get("log_status")
            initial_val = str(int(status_val)) if status_val is not None else ""
            initial_memo = log_data.get("memo", "")
        else:
            initial_val = ""
            initial_memo = ""
        
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
        # [Step 1 해결] edit_mode와 log_data가 있을 때만 값 추출
        if edit_mode and log_data:
            status_val = log_data.get("log_status")
            initial_val = str(int(status_val)) if status_val is not None else ""
            initial_memo = log_data.get("memo", "")
        else:
            initial_val = ""
            initial_memo = ""

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
        # [Step 1 해결] edit_mode와 log_data가 있을 때만 값 추출
        if edit_mode and log_data:
            status_val = log_data.get("log_status")
            initial_val = str(int(status_val)) if status_val is not None else None
            initial_memo = log_data.get("memo", "")
        else:
            initial_val = None
            initial_memo = ""

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
        add_title("건강기록", "bcs")
        # [Step 1 해결] edit_mode와 log_data가 있을 때만 값 추출
        if edit_mode and log_data:
            initial_weight = str(log_data.get("weight", ""))
            initial_bcs = str(log_data.get("bcs", ""))
        else:
            initial_weight = ""
            initial_bcs = None

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

    # 하단 버튼 조립
    add_bottom_controls(is_customer_detail)

    # 오버레이 제어 및 팝업 열기
    if popup.bottom_sheet_popup not in page.overlay:
        page.overlay.append(popup.bottom_sheet_popup)
    else:
        page.overlay.clear()
        page.overlay.append(popup.bottom_sheet_popup)
        
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
