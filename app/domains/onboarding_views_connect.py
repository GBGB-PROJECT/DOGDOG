import re
import flet as ft
from .onboarding.views.sign_up_view import sign_up_view
from .onboarding.views.pet_info_view import pet_info_view
from .onboarding.views.pet_obesity_view import pet_obesity_view
from .onboarding.views.pet_activity_view import pet_activity_view
from .onboarding.views.pet_health_view import pet_health_view
from .onboarding.views.pet_food_view import pet_food_view
from .onboarding.views.sign_up_success_view import signup_success_view
import components as dogdog


# -------------------------------------------------------------------------------------------------------
class Api_push_Data:
    data = {}


# -------------------------------------------------------------------------------------------------------
def on_boarding_tile(page: ft.Page, content_page: str, change_page_callback):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    popop = dogdog.Popup(page=page)
    storage = page.session.store
    content = []
    bottom = ft.Container() # [방어 코드] UnboundLocalError 방지를 위한 초기화

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
    regex_email = re.compile(
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._]+[@][a-zA-Z][A-Za-z.]+[.]\w{2,}"
    )

    # ---------------------------------------------------------------------------------------------------
    # Controller Initialization
    # ---------------------------------------------------------------------------------------------------
    from .onboarding.onboarding_controller import OnboardingController
    
    # 뷰와 로직을 연결하는 컨트롤러 인스턴스 생성
    controller = OnboardingController(
        page=page, 
        show_error_callback=show_error, 
        change_page_callback=change_page_callback,
        focus_field=focus_field,
        popop=popop
    )

    # ---------------------------------------------------------------------------------------------------
    # On Boarding Tile Routeing (View)
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/sign_up":
        top = ft.Row(controls=[dogdog.onboarding_top_bar(case=1)])
        content = sign_up_view(
            page=page, 
            check_email_callback=controller.check_email_duplicate
        )
        bottom = ft.Row(controls=[dogdog.continue_button(on_click=controller.process_user_sign_up)])

    elif content_page == "/pet_info":
        content = pet_info_view(page=page)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/sign_up")),
                dogdog.continue_button(on_click=controller.process_pet_info),
            ]
        )

    elif content_page == "/pet_obesity":
        content = pet_obesity_view(page=page)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_info")),
                dogdog.continue_button(on_click=controller.process_pet_obesity),
            ]
        )

    elif content_page == "/pet_activity":
        content = pet_activity_view(page=page)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_obesity")),
                dogdog.continue_button(on_click=controller.process_pet_activity),
            ]
        )

    elif content_page == "/pet_health":
        content = pet_health_view(page=page)
        bottom = ft.Row(
            controls=[
                dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_activity")),
                dogdog.continue_button(on_click=controller.process_pet_health),
            ]
        )

    elif content_page == "/pet_food":
        content = pet_food_view(page=page)
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
        basic_content = ft.Row(
            expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=signup_success_view(page=page),
                )
            ],
        )
        focus_field = None
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
                controls=content if isinstance(content, list) else [content],  # type: ignore
            ),
        ),
        focus_field,
        bottom,
    ]
    return basic_content, focus_field
