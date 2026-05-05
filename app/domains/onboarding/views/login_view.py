import flet as ft
import components as dogdog

def login_view(page: ft.Page, controller):
    """
    [View] login_view
    디자인 시안을 100% 재현한 이메일 로그인 화면입니다.
    """
    storage = page.session.store

    # 입력 변경 핸들러
    def on_email_change(e):
        storage.set("login_email", e.control.value)

    def on_password_change(e):
        storage.set("login_password", e.control.value)

    # 이메일 및 비밀번호 입력 필드 정의
    email_input = dogdog.input_textfield(
        hint_text="example@dogdog.com",
        input_type="email",
        on_change=on_email_change
    )
    email_input.value = "test042806@test.com"
    email_input.max_length = 50
    
    password_input = dogdog.input_textfield(
        hint_text="비밀번호",
        input_type="password",
        on_change=on_password_change
    )
    # [핵심 디테일] 비밀번호 가리기 및 눈 모양 아이콘 추가
    password_input.password = True
    password_input.can_reveal_password = True
    password_input.value = "A12345678!"

    # 중앙 콘텐츠 구성
    content = ft.Container(
        padding=ft.padding.only(top=page.height/10, bottom=page.height/10),
        alignment=ft.Alignment.CENTER,
        expand=True,
        content=ft.Column(
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
            controls=[
                ft.Row(height=150, margin=ft.margin.only(bottom=page.height/40),
                    alignment=ft.MainAxisAlignment.CENTER, 
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[ft.Image(src="dogdog_logo.png", width=300)]),
                ft.Container(height=10),
                dogdog.basic_text(value="이메일", weight="bold", color=ft.Colors.GREY_800),
                email_input,
                ft.Container(height=10),
                dogdog.basic_text(value="비밀번호", weight="bold", color=ft.Colors.GREY_800),
                password_input,
            ]
        )
    )

    # 하단 버튼 구성 (on_boarding_tile에서 bottom 변수로 사용될 부분)
    def on_login_click(e):
        # UI 필드의 현재 값을 실시간으로 직접 읽어옵니다.
        email = email_input.value
        password = password_input.value
        page.run_task(controller.process_email_login, email, password)

    bottom_bar = ft.Row(
        controls=[
            dogdog.arrow_back(on_click=lambda e: page.go("/login")),
            dogdog.continue_button(
                value="로그인",
                on_click=on_login_click
            )
        ]
    )

    return content, bottom_bar
