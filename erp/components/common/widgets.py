import flet as ft
# 버튼 크기 규격화 목적의 컴포넌트
MAIN_COLOR = "#004080"
ACTIVE_COLOR = "#22C7E8"
PAGE_BG = "#F2F2F2"


## 규격화된 textfield

def custom_textfield(label:str, hint:str, is_password=False):
  """둥근 테두리의 규격화된 입력창"""
  return ft.Column(
    spacing = 5, # 버튼 좌우 크기
    controls=[
      ft.Text(label,size=12, color=MAIN_COLOR, weight='bold'),
      ft.TextField(
        hint_text=hint,
        password=is_password,
        border_radius=20,
        border_color=MAIN_COLOR,
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
        bgcolor=MAIN_COLOR,
        height=50,
        width=float("inf"), # 부모 너비에 맞춤
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=on_click
    )

'''로그인 창 input'''
def custom_textfield(label:str, hint:str, is_password=False):
  """둥근 테두리의 규격화된 입력창"""
  return ft.Column(
    spacing = 5, # 버튼 좌우 크기
    controls=[
      ft.Text(label,size=12, color=MAIN_COLOR, weight='bold'),
      ft.TextField(
        hint_text=hint,
        password=is_password,
        border_radius=20,
        border_color=MAIN_COLOR,
        height=45,
        content_padding=15,
        text_size=14,
        bgcolor=ft.Colors.WHITE,
      )
    ],
  )

'''로그인 버튼'''
def primary_button(text: str, on_click):
    """브랜드 색상이 적용된 둥근 버튼"""
    return ft.ElevatedButton(
        content=ft.Text(text, size=16, weight="bold", color=ft.Colors.WHITE),
        bgcolor=MAIN_COLOR,
        height=50,
        width=float("inf"), # 부모 너비에 맞춤
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=25)),
        on_click=on_click
    )