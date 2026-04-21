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
from components import common as cm
from domain.controller.auth.erp_login_controller import AuthController

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
    self.email_input = cm.custom_textfield('이메일', "dogdog@gaebap.com")
    self.password_input = cm.custom_textfield("비밀번호", "********", is_password=True)

    self.content = self.build_login_erp()

  ## 1-2. 로그인 버튼 클릭 시 로직
  def handle_login(self, e):
    try:
      # 1. 입력창에서 값만 가져오기
      uid = self.id_input.controls[1].value
      u_email = self.email_input.controls[1].value
      u_pw = self.password_input.controls[1].value

      # 2. 모든 입력창의 에러 메시지 전광판을 초기화합니다.
      self.id_input.controls[1].error_text = None
      self.email_input.controls[1].error_text = None
      self.password_input.controls[1].error_text = None

      # 3. 데이터를 전달, 바구니에 넣는 작업
      is_valid, error_msg, error_type = AuthController.validate_login(uid, u_email, u_pw)

      # 4. 결과에 따른 후속 조치
      if not is_valid:
        target = None
        if error_type == "id":
          target = self.id_input.controls[1]
          print("아이디 유효성 오류")
        elif error_type == "email":
          target = self.email_input.controls[1]
          print('이메일 유효성 오류')
        elif error_type == "pw":
          target = self.password_input.controls[1]
          print("패스워드 유효성 오류")
        
        if target:
          target.error_text = error_msg
          target.update()

        # 2. 💡 가져오신 공식 예시를 적용한 SnackBar 호출법
        error_snackbar = ft.SnackBar(
            content=ft.Text(error_msg, color=cm.PAGE_BG),
            bgcolor=cm.INCORRECT_POPUPCOLOR,
            duration=3000
        )
        
        # 게시판에 붙이는 대신, show_dialog를 사용해 화면에 바로 띄웁니다!
        self.main_page.show_dialog(error_snackbar)
        
        self.main_page.update()
        return
      
      print("심사통과: 메인 화면으로 이동")
      self.on_login_success()

      # 2. 터미널에서 데이터 확인용 출력
      login_data = json.dumps({"id": uid, "email": u_email, "password": u_pw})
      print(f"--- [데이터 확인] ---")
      print(f"ID: {uid} | Email: {u_email}")
      print(f"성공 데이터: {login_data}")

      # 3. [핵심] 유효성 검사 없이 바로 성공 콜백 실행
      # 이 줄이 실행되면 무조건 다음 화면으로 넘어갑니다.
      self.on_login_success() 

    except Exception as err:
      # 만약 여기서 에러가 난다면 UI 경로(controls[1] 등)의 문제입니다.
      print(f"🔥 [Rollback 상태 에러]: {err}")
      if self.main_page:
        self.main_page.update()

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
