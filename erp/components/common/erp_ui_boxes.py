from ..common import color as c
import flet as ft

# ============================================================
# ✅ ERP 3줄 정보 카드
# - title (작은 설명)
# - main (핵심 값)
# - sub (보조 정보)
# ============================================================
def erp_info_box(title, main, sub):
    return ft.Container(
        width=220,  # 🔥 추가 (핵심)
        height=100,
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

def custom_textfield(label:str, hint:str, is_password=False):
  """둥근 테두리의 규격화된 입력창"""
  return ft.Column(
    spacing = 5, # 버튼 좌우 크기
    controls=[
      ft.Text(label,size=12, color=c.MAIN_COLOR, weight='bold'),
      ft.TextField(
        hint_text=hint,
        password=is_password,
        border_radius=20,
        border_color=c.MAIN_COLOR,
        height=45,
        content_padding=15,
        text_size=14,
        bgcolor=ft.Colors.WHITE,
      )
    ],
  )

def primary_button(text: str, on_click):
    """브랜드 색상이 적용된 둥근 버튼"""
    return ft.ElevatedButton(
        content=ft.Text(text, size=16, weight="bold", color=ft.Colors.WHITE),
        bgcolor=c.MAIN_COLOR,
        height=50,
        width=float("inf"), # 부모 너비에 맞춤
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=on_click
    )