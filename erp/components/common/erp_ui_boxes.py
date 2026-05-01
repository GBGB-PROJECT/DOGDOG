from ..common import color as c
import re
import flet as ft

from components.common.erp_busy_cursor import busy_cursor_control, with_busy_cursor

# ============================================================
# ✅ ERP 3줄 정보 카드
# - title (작은 설명)
# - main (핵심 값)
# - sub (보조 정보)
# ============================================================
def erp_info_box(title, main, sub):
    return ft.Container(
        expand=True,
        bgcolor=c.BOX_BG,
        border_radius=16,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),

        content=ft.Column(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                # 🔹 1줄 (작은 제목)
                ft.Text(
                    value=title,
                    size=12,
                    color=c.TEXT_MUTED,
                    weight=ft.FontWeight.W_500,
                ),

                # 🔹 2줄 (핵심 값)
                ft.Text(
                    value=main,
                    size=20,
                    color=c.TEXT_PRIMARY,
                    weight=ft.FontWeight.W_700,
                ),

                # 🔹 3줄 (보조 설명)
                ft.Text(
                    value=sub,
                    size=12,
                    color=c.TEXT_SECONDARY,
                    weight=ft.FontWeight.W_500,
                ),
            ],
        ),
    )

## 규격화된 textfield

def custom_textfield(label:str, hint:str, value: str="", is_password=False, on_submit=None):
    """
    둥근 테두리의 규격화된 입력창
     value: 기본입력값
     on_submit: enter 누를 때 실행되는 함수
    """
    def on_text_change(e):
        current_value = e.control.value # 현재 입력된 값

        if not current_value:
            return
        cleaned = re.sub(r'[가-힣ㄱ-ㅎㅏ-ㅣ]', '', current_value)
        if e.control.value != cleaned:
            e.control.value = cleaned
            e.control.update()
    return ft.Column(
        spacing=5,
        controls=[
            ft.Text(label, size=12, color=c.MAIN_COLOR, weight='bold'),
            ft.TextField(
                value=value,
                hint_text=hint,
                password=is_password,
                border_radius=20,
                border_color=c.MAIN_COLOR,
                height=45,
                content_padding=15,
                text_size=14,
                bgcolor=ft.Colors.WHITE,
                keyboard_type=ft.KeyboardType.EMAIL if not is_password else ft.KeyboardType.VISIBLE_PASSWORD,
                input_filter=ft.InputFilter(
                    allow=True,
                    regex_string=r"[a-zA-Z0-9!@#$%^&*().,]*",
                    replacement_string=""
                ),
                on_change=on_text_change, # 4. 정의한 함수 이름과 동일하게 맞춤
                on_submit=on_submit
            )
        ],
    )


def primary_button(text: str, on_click):
    """브랜드 색상이 적용된 둥근 버튼"""
    # 🔥 로그인 버튼도 실행 중 progress cursor 적용
    return busy_cursor_control(
        ft.ElevatedButton(
            content=ft.Text(text, size=16, weight="bold", color=ft.Colors.WHITE),
            bgcolor=c.MAIN_COLOR,
            height=50,
            width=float("inf"), # 부모 너비에 맞춤
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
            on_click=with_busy_cursor(on_click)
        )
    )
