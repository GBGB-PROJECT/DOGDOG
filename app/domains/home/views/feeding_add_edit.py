# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
from domains.onboarding.pet_food_controller import PetFoodController
from domains.home.controller.feeding_add_edit_controller import FeedingAddEditController


# -------------------------------------------------------------------------------------------------------
def feeding_add_edit(page: ft.Page, view: str):
    """
    [View] feeding_add_edit
    역할: 사료의 신규 등록 및 수정을 한 화면에서 처리합니다.
    - view == "add": 신규 등록 모드
    - view == "edit": 수정 모드
    """
    # ---------------------------------------------------------------------------------------------------
    # Controller 및 초기값 설정
    # ---------------------------------------------------------------------------------------------------
    popup = dogdog.Popup(page=page)
    storage = page.session.store
    controller = FeedingAddEditController(page, popup)
    
    # 수정 모드 데이터 로드
    feeding_data = controller.get_initial_data(view)
    
    # ---------------------------------------------------------------------------------------------------
    # 공통 에러 알림 로직
    # ---------------------------------------------------------------------------------------------------
    def show_toast(text: str):
        page.show_dialog(
            ft.SnackBar(content=ft.Text(value=text), open=True, behavior=ft.SnackBarBehavior.FLOATING)
        )

    # ---------------------------------------------------------------------------------------------------
    # 입력 필드 및 컨트롤러 위임
    # ---------------------------------------------------------------------------------------------------
    # 사료 선택 및 용량 드롭다운 (PetFoodController 재사용)
    food_select_ctrl = PetFoodController(page=page, popup=popup)
    
    # ---------------------------------------------------------------------------------------------------
    # UI 컴포넌트 정의 및 자동 완성 (Auto-fill)
    # ---------------------------------------------------------------------------------------------------
    # 1. 상단 타이틀 및 타이틀별 초기화
    if view == "edit":
        column_text = "급여 중인 사료"
        # 수정 모드 시 기존 데이터 바인딩
        product_name = f"{feeding_data.get('brand', '')} {feeding_data.get('product_name', '')}".strip()
        food_select_ctrl.food_picker_field.content.controls[0].value = product_name
        food_select_ctrl.food_picker_field.content.controls[0].color = ft.Colors.BLACK
        
        storage.set("product_id", feeding_data.get("product_id"))
        storage.set("food_text", product_name)
    else:
        column_text = "신규 사료 등록"
        # 신규 모드 시 초기화 (방어적 프로그래밍 적용)
        if storage.contains_key("food_text"):
            storage.remove("food_text")
        if storage.contains_key("product_id"):
            storage.remove("product_id")
        if storage.contains_key("food_weight"):
            storage.remove("food_weight")

    # 2. 사료 잔여량 입력 필드
    def on_weight_change(e):
        try:
            val = e.control.value
            storage.set("food_weight", int(val) if val else None)
        except ValueError:
            pass

    selected_food_weight = dogdog.input_textfield(
        hint_text="사료의 잔여량을 적어주세요", 
        input_type="int", 
        suffix="g", 
        on_change=on_weight_change
    )

    # [QA 수정] 용량 선택 시 잔여량 자동 입력 (메서드 가로채기 방식)
    # 기존 컨트롤러의 이벤트를 감싸서 UI 업데이트 로직을 100% 실행하도록 보장
    original_weight_set = food_select_ctrl.food_product_weight_set

    def intercepted_weight_set(e, weight_list_control):
        # 1. 컨트롤러 원본 로직 먼저 실행 (용량 ID 저장 등)
        original_weight_set(e, weight_list_control)
        
        # 2. UI 자동완성 로직 실행 (가로채기)
        try:
            import re
            val_str = str(e.control.value)
            # 옵션 리스트에서 현재 선택된 객체 찾기
            selected_option = next((opt for opt in e.control.options if str(opt.key) == val_str), None)
            
            # [Fallback] 옵션 텍스트가 있으면 텍스트에서, 없으면 value 자체에서 숫자만 추출
            raw_source = selected_option.text if selected_option else val_str
            weight_val = re.sub(r'[^0-9]', '', raw_source)
            
            if weight_val:
                selected_food_weight.value = weight_val
                storage.set("food_weight", int(weight_val))
                
                # [가장 중요] 개별 컴포넌트와 화면 전체를 강제 렌더링하여 즉각 반영
                selected_food_weight.update()
                page.update() 
                print(f"👉 [성공] 잔여량 자동 입력 가로채기 완료: {weight_val}g")
        except Exception as ex:
            print(f"👉 [에러] 자동 입력 처리 실패: {ex}")

    # 컨트롤러 메서드 덮어쓰기 (Monkey Patching)
    food_select_ctrl.food_product_weight_set = intercepted_weight_set

    # 수정 모드 시 잔여량 자동 완성
    if view == "edit":
        # 1. 잔여량 텍스트 필드 채우기
        initial_left = str(int(float(feeding_data.get("left_intake", 0))))
        selected_food_weight.value = initial_left
        storage.set("food_weight", int(initial_left))
        
        # 2. 사료 용량 드롭다운 채우기
        raw_total = feeding_data.get("total_weight") or feeding_data.get("product_weight")
        if raw_total:
            clean_weight_str = str(int(float(raw_total)))
            if not target_dropdown.options:
                target_dropdown.options = [
                    dogdog.dropdown_menu_option(key=clean_weight_str, text=f"{clean_weight_str}g")
                ]
            target_dropdown.value = clean_weight_str
            target_dropdown.visible = True
        
        # [Step 2] 급여 시작일 세션 저장 및 Fallback 처리
        f_start = feeding_data.get("feeding_start")
        if not f_start or f_start == "정보 없음":
            from datetime import datetime
            f_start = datetime.now().strftime("%Y-%m-%d")
        
        storage.set("feeding_start", f_start)

    # 3. 급여 시작일 (수정 모드 전용) - Date Picker 연동
    from datetime import datetime
    
    # 3-1. 날짜 텍스트 객체 선언
    date_display_text = dogdog.basic_text(
        value=storage.get("feeding_start"),
        color=ft.Colors.GREY_600,
        size=14
    )

    # 3-2. 피커 핸들러
    def handle_date_change(e):
        if date_picker.value:
            from datetime import timedelta
            # [버그 해결] UTC -> KST (9시간 더해서 강제 보정)
            corrected_datetime = date_picker.value + timedelta(hours=9)
            selected_date = corrected_datetime.strftime("%Y-%m-%d")
            
            storage.set("feeding_start", selected_date)
            date_display_text.value = selected_date
            date_display_text.update()

    # 3-3. DatePicker 정의 및 오버레이 등록
    now = datetime.now()
    initial_date_val = now
    try:
        if storage.get("feeding_start"):
            initial_date_val = datetime.strptime(storage.get("feeding_start"), "%Y-%m-%d")
    except Exception:
        pass

    date_picker = ft.DatePicker(
        value=initial_date_val,
        on_change=handle_date_change,
        first_date=datetime(2020, 1, 1),
        last_date=now,
    )
    
    if date_picker not in page.overlay:
        page.overlay.append(date_picker)

    # 3-4. UI 컴포넌트 구성
    feeding_start_date = ft.Container(
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            controls=[
                dogdog.basic_text(value="급여 시작일:", color=ft.Colors.GREY_600, size=14),
                ft.Icon(icon=ft.Icons.CALENDAR_MONTH, color=ft.Colors.GREY_600, size=16),
                date_display_text
            ]
        ),
        visible=(view == "edit"),
        on_click=lambda _: setattr(date_picker, "open", True) or page.update(),
        padding=ft.padding.symmetric(vertical=10),
    )

    # ---------------------------------------------------------------------------------------------------
    # 버튼 이벤트 로직
    # ---------------------------------------------------------------------------------------------------
    async def handle_save(e):
        p_id = storage.get("product_id")
        f_weight = storage.get("food_weight")

        if not p_id:
            show_toast("사료를 선택해주세요.")
            return
        if not f_weight:
            show_toast("사료의 잔여량을 입력해주세요.")
            return

        if view == "add":
            success, msg = await controller.save_feeding_product(p_id, f_weight)
        else:
            f_date = storage.get("feeding_start")
            success, msg = await controller.update_feeding_product(f_weight, f_date)

        if success:
            show_toast(msg)
            # [Issue 1 해결] 성공 시 낡은 세션 완벽 청소 (임시 데이터 및 상세 데이터)
            keys_to_clear = ["food_text", "product_id", "food_weight", "select_feeding_data"]
            for key in keys_to_clear:
                if storage.contains_key(key):
                    storage.remove(key)
            
            # [Issue 1 해결] 라우팅 최적화
            if view == "edit":
                page.go("/feeding") # 수정은 목록으로
            else:
                page.go("/home")    # 등록은 홈으로 (대시보드 갱신 유도)

            # 전역 갱신 신호 발송
            page.pubsub.send_all("update_dashboard")
        else:
            show_toast(msg)

    # [QA 수정] 삭제 확인 모달 호출 로직 (컨트롤러 위임)
    async def handle_delete(e):
        print("👉 [로그] 뷰: [삭제] 버튼 클릭 이벤트 발생")
        async def perform_delete():
            success, msg = await controller.delete_feeding_product()
            if success:
                show_toast(msg)
                # [Issue 1 해결] 삭제 성공 시 세션 비우기
                if storage.contains_key("select_feeding_data"):
                    storage.remove("select_feeding_data")
                    
                page.go("/feeding")
                page.pubsub.send_all("update_dashboard")
            else:
                show_toast(msg)
        
        # 컨트롤러의 최신 Dialog API 사용
        controller.show_delete_confirm_dialog(perform_delete)

    # ---------------------------------------------------------------------------------------------------
    # 하단 버튼 구성 (모드별 분기)
    # ---------------------------------------------------------------------------------------------------
    if view == "edit":
        # 수정 모드: [삭제](회색) & [수정](노란색)
        feeding_setting_content = [
            dogdog.flat_button(
                text="삭제", 
                bgcolor=ft.Colors.GREY_300, 
                text_color=ft.Colors.BLACK54,
                on_click=handle_delete
            ),
            dogdog.flat_button(
                text="수정", 
                bgcolor="#FEF3B9", 
                on_click=handle_save
            ),
        ]
    else:
        # 신규 모드: [저장](노란색)
        feeding_setting_content = [
            dogdog.flat_button(
                text="저장", 
                bgcolor="#FEF3B9", 
                on_click=handle_save
            )
        ]

    feeding_setting = ft.Row(
        margin=ft.margin.only(top=10),
        spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=feeding_setting_content
    )

    # ---------------------------------------------------------------------------------------------------
    # 최종 레이아웃 구성
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value=column_text, weight="bold"),
        food_select_ctrl.food_picker_field,
        food_select_ctrl.product_weight_list,
        ft.Container(height=10),
        dogdog.basic_text(value="사료 잔여량", weight="bold"),
        selected_food_weight,
        feeding_start_date,
        ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
        feeding_setting,
    ]

    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_column,
            horizontal_alignment=ft.CrossAxisAlignment.START
        )
    )