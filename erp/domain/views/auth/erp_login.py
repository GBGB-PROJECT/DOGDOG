import sys
import os

# 1. 내 위치(auth)를 기준으로, 프로젝트 최상위 폴더(dogdog-project)의 절대 경로를 찾습니다.
#    auth -> views -> domain -> erp -> dogdog-project (총 4칸 위로!)
current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_dir))))

# 2. 파이썬에게 "저 경로를 네 머릿속에 기억해 둬!" 라고 강제로 주입합니다.
if project_root not in sys.path:
    sys.path.insert(0, project_root)
### ========================================테스트 목적의 인위적 연결설정

import json
import flet as ft
from erp.components import common as cm

# 1. ERP 로그인 페이지 클래스 생성
"""
  - self에서 시작하는 이유
    - self를 통해 기억을 해두어야 함수 外(__init__)에서도 사용 가능함
"""
class ErpLoginView(ft.Container):
  ## 1-1. 초기 설정(flet 최초 설정과 동일하다.)
  def __init__(self, page:ft.Page, on_login_success):
    super().__init__()
    # 클래스에 대한 설정
    self.main_page= page
    self.expand = True # 화면에 꽉 차게 배치(화면에 ErpLoginView를 꽉 차게 배치)
    self.alignment=ft.Alignment.CENTER # 화면 중앙에 배치
    self.on_login_success = on_login_success

    ## 입력창을 선언함
    self.id_input = cm.custom_textfield('사번', "GB0001") # label값, placeholder값
    self.email_input = cm.custom_textfield('이메일', "test@naver.com")
    self.password_input = cm.custom_textfield("비밀번호", "********", is_password=True)

    self.content = self.build_login_erp()

  ## 1-2. 로그인 버튼 클릭 시 로직 -> 입력받은 값을 json 형태로 변경
  def handle_login(self, e):
    login_data = json.dumps({
    "id": self.id_input.controls[1].value,
    "email": self.email_input.controls[1].value,
    "password": self.password_input.controls[1].value
    })
    print(login_data)
    self.on_login_success() # 테스트용 일단 조건엾이 화면 전환
  
  ## 1-3. 컴포넌트 조립 ===================
  def build_login_erp(self):
    return ft.Container(
      width=320,# 너비
      padding=20, # 내부 간격
      content=ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # 좌우간격 중간
        alignment=ft.MainAxisAlignment.CENTER, # 상하간격 중간
        spacing=20,
        controls=[
          ft.Text("개밥개밥푸드", size=30, weight='bold', color=cm.MAIN_COLOR),
          #### input 창을 조립
          self.id_input,
          self.email_input,
          self.password_input,
          ### 아이디/비밀번호 찾기 칸
          ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.TextButton("아이디 찾기", style=ft.ButtonStyle(color=cm.MAIN_COLOR)),
                ft.Text("|", color=cm.MAIN_COLOR),
                ft.TextButton("비밀번호 찾기", style=ft.ButtonStyle(color=cm.MAIN_COLOR)),
            ]
          ),   
        # 로그인 버튼
        cm.primary_button("로그인", on_click=self.handle_login)
        ]
      )
    )

def main(page: ft.Page):
    page.title = "ERP 로그인 테스트"
    # 클래스를 생성하고 페이지에 추가합니다.
    login_view = ErpLoginView(page)
    page.add(login_view)


# ## 테스트용 실행(이후에는 연결고리를 만들 것)
# if __name__ == "__main__": 
#   ft.app(target=main, assets_dir="assets")
