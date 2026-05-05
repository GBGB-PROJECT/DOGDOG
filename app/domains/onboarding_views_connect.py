# -------------------------------------------------------------------------------------------------------
import re
import flet as ft
import domains
import components as dogdog
# -------------------------------------------------------------------------------------------------------
class Api_push_Data:
    data = {}
# -------------------------------------------------------------------------------------------------------
def on_boarding_tile(page: ft.Page, popup, content_page:str, change_page_callback):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    content = []
    bottom = ft.Container()  # [방어 코드] UnboundLocalError 방지를 위한 초기화

    def show_error(text: str):
        # [수정] SnackBar는 show_dialog가 아닌 page.snack_bar 또는 별도 스낵바 호출 방식을 사용해야 함
        snack_bar = ft.SnackBar(
            content=ft.Text(value=text),
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    top = ft.Row(controls=[dogdog.onboarding_top_bar()])
    focus_field = ft.TextField(
        border_color=ft.Colors.TRANSPARENT,
        height=0,
        opacity=0,
        focus_color=ft.Colors.TRANSPARENT,
        read_only=True,
    )

    # ---------------------------------------------------------------------------------------------------
    # Controller Initialization
    # ---------------------------------------------------------------------------------------------------
    from .onboarding.onboarding_controller import OnboardingController
    from .onboarding.pet_info_controller import PetInfoController
    from .onboarding.pet_food_controller import PetFoodController
    from .onboarding.login_controller import LoginController

    # 뷰와 로직을 연결하는 컨트롤러 인스턴스 생성
    controller = OnboardingController(
        page=page,
        show_error_callback=show_error,
        change_page_callback=change_page_callback,
        focus_field=focus_field,
        popup=popup,
    )
    
    pet_info_controller = PetInfoController(page=page, popup=popup)
    pet_food_controller = PetFoodController(page=page, popup=popup)
    login_controller = LoginController(page=page, change_page_callback=change_page_callback)

    # ---------------------------------------------------------------------------------------------------
    # On Boarding Tile Routeing
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/login":
        def login_next(e):
            key = e.control.data.get('key')
            if key == 'Email':
                change_page_callback("/login_email")
            elif key == 'sign_up':
                change_page_callback("/sign_up")
            else:
                show_error(text="기능 구현중입니다.")
                return
        top = ft.Row(height=150, margin=ft.margin.only(top=40, bottom=-100),
            alignment=ft.MainAxisAlignment.CENTER, 
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[ft.Image(src="dogdog_logo.png", width=300)])
        content_text_1 = dogdog.basic_text(
            value="똑똑🚪✊ 우리집 강아지가 마지막 한알을 먹기 전\n문앞에 사료가 도착합니다 🔔", weight="bold")
        content_text_1.text_align = ft.TextAlign.CENTER
        content_text_2 = dogdog.basic_text(color=ft.Colors.GREY_600,
            value="반려견 맞춤형 설정에 따라 똑똑AI가 계산한\n권장 급여량을 확인하고\n간편하게 식사량을 기록하세요!")
        content_text_2.text_align = ft.TextAlign.CENTER
        content_text_1 = dogdog.basic_text(
            value="똑똑🚪✊ 우리집 강아지가 마지막 한알을 먹기 전\n문앞에 사료가 도착합니다 🔔", weight="bold")
        content_text_1.text_align = ft.TextAlign.CENTER
        content_text_2 = dogdog.basic_text(color=ft.Colors.GREY_600,
            value="반려견 맞춤형 설정에 따라 똑똑AI가 계산한\n권장 급여량을 확인하고\n간편하게 식사량을 기록하세요!")
        content_text_2.text_align = ft.TextAlign.CENTER
        login_content = ft.Container(
            alignment=ft.Alignment.CENTER, expand=True,
            alignment=ft.Alignment.CENTER, expand=True,
            content=ft.Column(
                spacing=40,
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                controls=[
                    # dogdog.continue_button(
                    #     value="Continue with Google", icon="Google", expand=False, 
                    #     on_click=login_next, data={'key':'Google'}),
                    # dogdog.continue_button(
                    #     value="Continue with Naver", icon="Naver", expand=False,  
                    #     on_click=login_next, data={'key':'Naver'}),
                    # dogdog.continue_button(
                    #     value="Continue with Kakao", icon="Kakao", expand=False, 
                    #     on_click=login_next, data={'key':'Kakao'}),
                    # ft.Row(margin=10, height=20, controls=[
                    #     ft.Divider(expand=True), 
                    #     dogdog.basic_text('or', color=ft.Colors.GREY_500), 
                    #     ft.Divider(expand=True)
                    # ]),
                    content_text_1,
                    content_text_2,
                    dogdog.continue_button(
                        value="Continue with Email", expand=False, 
                        on_click=login_next, data={'key':'Email'}),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                        dogdog.basic_text("계정이 없으신가요?", color=ft.Colors.GREY_500),
                        ft.TextButton(dogdog.basic_text("회원가입", weight="bold"), 
                            on_click=login_next, data={'key':'sign_up'}),
                    ])
        ]))
        bottom = ft.Container(padding=0, margin=0)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/login_email":
        # [방어 코드] 로그인 화면에서는 온보딩 전용 헤더(onboarding_top_bar)를 노출하지 않도록 빈 컨테이너로 덮어씌움
        top = ft.Container() 
        
        # MVC 패턴 적용: 외부 View 함수 호출 (로고, 폼, 하단바를 각각 반환받음)
        top_logo, login_content, bottom_bar = domains.login_view(page=page, controller=login_controller)
        
        # 라우터 구조에 맞게 변수 할당
        top = top_logo
        content = login_content
        bottom = bottom_bar
    # ---------------------------------------------------------------------------------------------------
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/sign_up":
        top = ft.Row(controls=[dogdog.onboarding_top_bar(case=1)])
        content = domains.sign_up_view(
            page=page, controller=controller, check_email_callback=controller.check_email_duplicate
        )
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/login")),
                dogdog.continue_button(on_click=controller.process_user_sign_up)]
        )

    elif content_page == "/pet_info":
        content = domains.pet_info_view(page=page, popup=popup, controller=pet_info_controller)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/sign_up")),
                dogdog.continue_button(on_click=controller.process_pet_info),
            ]
        )

    elif content_page == "/pet_obesity":
        content = domains.pet_obesity_view(page=page, controller=controller)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_info")),
                dogdog.continue_button(on_click=controller.process_pet_obesity),
            ]
        )

    elif content_page == "/pet_activity":
        content = domains.pet_activity_view(page=page, controller=controller)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(
                    on_click=lambda e: change_page_callback("/pet_obesity")
                ),
                dogdog.continue_button(on_click=controller.process_pet_activity),
            ]
        )

    elif content_page == "/pet_health":
        content = domains.pet_health_view(page=page, controller=controller)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(
                    on_click=lambda e: change_page_callback("/pet_activity")
                ),
                dogdog.continue_button(on_click=controller.process_pet_health),
            ]
        )

    elif content_page == "/pet_food":
        content = domains.pet_food_view(page=page, popup=popup, controller=pet_food_controller)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(
                    on_click=lambda e: change_page_callback("/pet_health")
                ),
                dogdog.continue_button(on_click=controller.process_onboarding_finalize),
            ]
        )
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/sign_up_success":
        # 1.5초 후 자동으로 홈 화면으로 이동하는 비동기 태스크 정의
        async def auto_redirect_to_home():
            import asyncio

            await asyncio.sleep(1.5)
            # 이미 다른 페이지로 이동했거나 페이지가 닫힌 경우를 대비한 방어 코드
            if page.route == "/sign_up_success":
                page.go("/home")

        # 화면이 렌더링됨과 동시에 비동기 태스크 실행
        page.run_task(auto_redirect_to_home)

        basic_content = ft.Row(
            expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=domains.signup_success_view(page=page),
                )
            ],
        )
        focus_field = ft.Container()  # None 대신 빈 위젯 반환하여 "None" 글자 노출 방지
        return basic_content, focus_field
    # ---------------------------------------------------------------------------------------------------
    # On Boarding Content and Dummy Focus Field Change
    # ---------------------------------------------------------------------------------------------------
    basic_content = [
        top,
        ft.Container(
            expand=True,
            padding=ft.Padding.only(top=20),
            content=ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                expand=True,
                spacing=10,
                controls=content if isinstance(content, list) else [content] # type: ignore
            )
        ) if not "/login" in content_page else login_content,
        focus_field,
        bottom
    ]
    return basic_content, focus_field