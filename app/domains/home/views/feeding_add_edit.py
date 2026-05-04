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

    # [QA 수정] 용량 선택 시 잔여량 자동 입력 통합 핸들러
    def handle_weight_change(e):
        # 1. 컨트롤러의 기존 로직 실행 (용량 ID 저장 등)
        food_select_ctrl.food_product_weight_set(e, food_select_ctrl.product_weight_list)
        
        # 2. 선택된 용량 값을 잔여량 텍스트 필드에 자동 입력
        selected_id = e.control.value
        # e.control은 이벤트를 발생시킨 실제 Dropdown 객체입니다.
        selected_option = next((opt for opt in e.control.options if opt.key == selected_id), None)
        if selected_option:
            try:
                # "1600g" -> "1600"
                weight_val = selected_option.text.replace("g", "")
                selected_food_weight.value = weight_val
                storage.set("food_weight", int(float(weight_val)))
                selected_food_weight.update()
            except Exception:
                pass

    # [핵심] 실제 Dropdown 컨트롤을 찾아 on_change 이벤트 연결 (래핑 대응)
    target_dropdown = food_select_ctrl.product_weight_list
    # dogdog.dropdown_menu가 Container(content=Dropdown) 구조일 경우를 대비
    if hasattr(target_dropdown, "content") and isinstance(target_dropdown.content, ft.Dropdown):
        target_dropdown = target_dropdown.content
    
    target_dropdown.on_change = handle_weight_change
    
    # 수정 모드 시 잔여량 자동 완성
    if view == "edit":
        # 1. 잔여량 텍스트 필드 채우기
        initial_left = str(int(float(feeding_data.get("left_intake", 0))))
        selected_food_weight.value = initial_left
        storage.set("food_weight", int(initial_left))
        
        # 2. 사료 용량 드롭다운 채우기 (중요: key 값과 value 타입 일치)
        # [QA 수정] 용량 데이터(total_weight 등)를 가져와서 드롭다운 value에 할당
        raw_total = feeding_data.get("total_weight") or feeding_data.get("product_weight")
        if raw_total:
            # str(int(float(...))) 처리를 통해 소수점 제거 및 타입 일치
            clean_weight_str = str(int(float(raw_total)))
            
            # [핵심] 옵션 리스트가 비어있으면 value를 설정해도 화면에 나오지 않으므로 임시 옵션 생성
            if not target_dropdown.options:
                target_dropdown.options = [
                    dogdog.dropdown_menu_option(key=clean_weight_str, text=f"{clean_weight_str}g")
                ]
            
            target_dropdown.value = clean_weight_str
            storage.set("product_id", int(clean_weight_str))
            target_dropdown.visible = True

    # 3. 급여 시작일 (수정 모드 전용)
    feeding_start_date = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=5,
        visible=(view == "edit"),
        # controls=[
        #     ft.Icon(icon=ft.Icons.CALENDAR_MONTH, color=ft.Colors.GREY_600, size=16),
        #     dogdog.basic_text(
        #         value=f"급여 시작일 : {feeding_data.get('feeding_start', '정보 없음')}", 
        #         color=ft.Colors.GREY_600
        #     ),
        # ]
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
            customer_food_id = storage.get("select_customer_food_id")
            success, msg = await controller.update_feeding_product(customer_food_id, f_weight)

        if success:
            show_toast(msg)
            # [QA 수정] 등록 성공 후 입력 임시 데이터 정리
            for key in ["food_text", "product_id", "food_weight"]:
                if storage.contains_key(key):
                    storage.remove(key)
            
            page.go("/feeding")
            # 홈 화면 대시보드 갱신 유도
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