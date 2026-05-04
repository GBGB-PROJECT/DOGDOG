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
        top = ft.Row(height=200,
            alignment=ft.MainAxisAlignment.CENTER, 
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[ft.Image(src="dogdog_logo.png", width=300)])
        login_content = ft.Container(
            alignment=ft.Alignment.CENTER, expand=True, padding=ft.padding.only(top=10, bottom=20),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                controls=[
                    dogdog.continue_button(
                        value="Continue with Google", icon="Google", expand=False, 
                        on_click=login_next, data={'key':'Google'}),
                    dogdog.continue_button(
                        value="Continue with Naver", icon="Naver", expand=False,  
                        on_click=login_next, data={'key':'Naver'}),
                    dogdog.continue_button(
                        value="Continue with Kakao", icon="Kakao", expand=False, 
                        on_click=login_next, data={'key':'Kakao'}),
                    ft.Row(margin=10, height=20, controls=[
                        ft.Divider(expand=True), 
                        dogdog.basic_text('or', color=ft.Colors.GREY_500), 
                        ft.Divider(expand=True)
                    ]),
                    dogdog.continue_button(
                        value="Continue with Email", expand=False, 
                        on_click=login_next, data={'key':'Email'}),
                    ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                        ft.TextButton(dogdog.basic_text("회원가입", color=ft.Colors.GREY_500), 
                            on_click=login_next, data={'key':'sign_up'}),
                        ft.TextButton(dogdog.basic_text("아이디 / 비밀번호 찾기", color=ft.Colors.GREY_500), 
                            on_click=login_next, data={'key':'ID/PW_Search'})
                    ])
        ]))
        bottom = ft.Container(padding=0, margin=0)
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/login_email":
        def login_email_on_change(e):
            storage.set("login_email", e.control.value)
        def login_password_on_change(e):
            storage.set("login_password", e.control.value)
        def email_login_next(e):
            if storage.get('login_email') and storage.get('login_password'):
                change_page_callback("/home")
        email_input = dogdog.input_textfield(hint_text="example@gmail.com", input_type="email", on_change=login_email_on_change)
        password_input = dogdog.input_textfield(hint_text="비밀번호", input_type="password", on_change=login_password_on_change)
        top = ft.Row(height=200,
            alignment=ft.MainAxisAlignment.CENTER, 
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[ft.Image(src="dogdog_logo.png", width=300)])
        login_content = ft.Container(
            alignment=ft.Alignment.CENTER, expand=True,padding=ft.padding.only(top=10, bottom=20),
            content=ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                alignment=ft.MainAxisAlignment.CENTER, 
                expand=True,
                controls=[
                    ft.Container(height=10),
                    dogdog.basic_text(value="이메일", weight="bold", color=ft.Colors.GREY_800),
                    email_input,
                    dogdog.basic_text(value="비밀번호", weight="bold", color=ft.Colors.GREY_800),
                    password_input,
        ]))
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/login")),
            dogdog.continue_button(value="Continue with Email", on_click=email_login_next)
        ])
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