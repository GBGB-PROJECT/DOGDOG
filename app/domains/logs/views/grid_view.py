import flet as ft
import components as dogdog
import datetime
from domains.logs.controller.status_controller import StatusController

# -------------------------------------------------------------------------------------------------------
async def bottom_sheet(e, page: ft.Page, popup, call, on_refresh_callback=None):
    """
    [View] bottom_sheet
    역할: 그리드 메뉴 클릭 시 열리는 하단 팝업 UI를 생성합니다.
    - StatusController를 인스턴스화하여 비즈니스 로직 및 상태 변경을 위임합니다.
    - 데이터 조회는 컨트롤러에서 수행하며, 이 뷰는 반환된 데이터로 시각적 요소만 렌더링합니다.
    """
    s_control = StatusController(page=page, popup=popup, on_refresh_callback=on_refresh_callback)
    s_control.set_default_datetime(call)
    
    bottom_sheet_contents = popup.bottom_sheet_controls
    bottom_sheet_contents.clear()
    
    # 공통 UI 컴포넌트: 피커
    date_picker = ft.DatePicker(
        first_date=datetime.datetime.now() - datetime.timedelta(days=7),
        last_date=datetime.datetime.now(),
    )
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)
        
    time_picker = ft.TimePicker(entry_mode=ft.TimePickerEntryMode.DIAL_ONLY)
    if time_picker not in page.overlay:
        page.overlay.append(time_picker)

    def open_picker(e, picker):
        picker.open = True
        page.update()

    data_button = dogdog.flat_icon_text_button(
        ft.Icons.CALENDAR_MONTH, datetime.datetime.now().strftime("%Y.%m.%d")
    )
    data_button.on_click = lambda e: open_picker(e, date_picker)

    time_button = dogdog.flat_icon_text_button(
        ft.Icons.ACCESS_TIME,
        datetime.datetime.now().strftime("%p %H:%M").replace("AM", "오전").replace("PM", "오후"),
    )
    time_button.on_click = lambda e: open_picker(e, time_picker)

    # 피커 on_change 이벤트 바인딩
    def on_date_change(e):
        formatted = s_control.change_date(call, date_picker.value)
        if formatted:
            data_button.content.controls[1].value = formatted
            popup.bottom_sheet_popup.update()

    def on_time_change(e):
        formatted = s_control.change_time(call, time_picker.value)
        if formatted:
            time_button.content.controls[1].value = formatted
            popup.bottom_sheet_popup.update()

    date_picker.on_change = on_date_change
    time_picker.on_change = on_time_change

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
        
        # 컨트롤러를 통해 데이터 준비
        data = await s_control.fetch_feeding_init_data()
        
        if data["has_food"]:
            feeding_guide = ft.Column(
                visible=True,
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0,
                controls=[
                    ft.Row(
                        margin=ft.margin.only(bottom=10),
                        controls=[dogdog.basic_text(f"오늘 {data['pet_name']}에게 딱 맞춘 1회 급여량은 ...", size=16, weight="bold", color=ft.Colors.GREY_600)],
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

            food_options = [dogdog.dropdown_menu_option(key=item["key"], text=item["text"]) for item in data["food_options_data"]]
            
            food_dropdown = dogdog.dropdown_menu(
                label="사료를 선택해주세요.",
                options=food_options,
                event=lambda e: s_control.change_customer_food_id(e.control.value),
            )
            food_dropdown.value = data["initial_value"]

            feeding_food_list = ft.Row(margin=ft.margin.only(bottom=18), controls=[food_dropdown])

            feeding_weight = dogdog.input_textfield(
                hint_text="급여량(g)을 입력하세요.", input_type="int", suffix="g",
                on_change=lambda e: s_control.change_weight(call, e.control.value)
            )
            feeding_weight.value = str(int(data["recommended_amount"]))
            s_control.change_weight(call, data["recommended_amount"])

            feeding_memo = dogdog.input_textfield(
                hint_text="메모 (선택)", text_filter=None, max_length=None,
                on_change=lambda e: s_control.change_memo(call, e.control.value)
            )

            bottom_sheet_contents.extend([feeding_guide, feeding_food_list, feeding_weight, feeding_memo])
        else:
            is_customer_detail = False
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
        watering = dogdog.input_textfield(
            hint_text="물 섭취량을 적어주세요.", input_type="int", suffix="ml",
            on_change=lambda e: s_control.change_weight(call, e.control.value)
        )
        watering_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value)
        )
        bottom_sheet_contents.extend([watering, watering_memo])

    elif call == "daily_walks":
        add_title("활동기록")
        daily_walks = dogdog.input_textfield(
            hint_text="산책시간을 적어주세요.", input_type="int", suffix="분",
            on_change=lambda e: s_control.change_weight(call, e.control.value)
        )
        daily_walks_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value)
        )
        bottom_sheet_contents.extend([daily_walks, daily_walks_memo])

    elif call == "hygiene_bowel":
        add_title("위생/배변", "bowel")
        hygiene_bowel_score = dogdog.dropdown_menu(
            label="배변 스코어를 선택해주세요.",
            options=[dogdog.dropdown_menu_option(text=f"{row}") for row in range(1, 8)],
            event=lambda e: s_control.change_weight(call, e.control.value),
        )
        hygiene_bowel_memo = dogdog.input_textfield(
            hint_text="메모 (선택)", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value)
        )
        bottom_sheet_contents.extend([hygiene_bowel_score, hygiene_bowel_memo])

    elif call == "health_log":
        add_title("건강기록", "bcs")
        health_log = dogdog.input_textfield(
            hint_text="몸무게를 적어주세요.", input_type="float", suffix="Kg",
            on_change=lambda e: s_control.change_weight(call, e.control.value, is_float=True)
        )
        health_bcs = dogdog.dropdown_menu(
            label="BCS를 선택해주세요.",
            options=[dogdog.dropdown_menu_option(text=f"{row}") for row in range(9, 0, -1)],
            event=lambda e: s_control.change_weight(call, e.control.value, is_bcs=True),
        )
        bottom_sheet_contents.extend([health_log, health_bcs])

    elif call == "status_log":
        add_title("상태기록")
        status_log = dogdog.input_textfield(
            hint_text="기타상태를 작성해주세요.", text_filter=None, max_length=None,
            on_change=lambda e: s_control.change_memo(call, e.control.value)
        )
        bottom_sheet_contents.extend([status_log])

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
        ("위생/배변", "poop.png", lambda e: page.run_task(bottom_sheet, e, page, popup, "hygiene_bowel", on_refresh_callback)),
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
