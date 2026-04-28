import sys
import os
import json
import flet as ft
from components import common as cm
from domain.controller import auth

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
    self.id_input = cm.custom_textfield('사번', "account1") # label값, placeholder값
    self.email_input = cm.custom_textfield('이메일', "emp1@test.com")
    self.password_input = cm.custom_textfield("비밀번호", "hashed_pw", is_password=True)

    self.content = self.build_login_erp()

## 1-2. 로그인 버튼 클릭 시 로직
  def handle_login(self, e):
    try:
      # 1. 입력값 가져오기
      uid = self.id_input.controls[1].value
      u_email = self.email_input.controls[1].value
      u_pw = self.password_input.controls[1].value

      # 2. 에러 메시지 초기화
      self.id_input.controls[1].error_text = None
      self.email_input.controls[1].error_text = None
      self.password_input.controls[1].error_text = None

      # 3. 유효성 검사 실행
      is_valid, error_msg, error_type = auth.AuthController.validate_login(uid, u_email, u_pw)
      if not is_valid:
        # 유효성 실패 시 스낵바 (공식 예시 적용)
        self.main_page.show_dialog(ft.SnackBar(ft.Text(error_msg)))
        self.main_page.update()
        return
      ## 4. 백엔드 서버 인증 시도 => 2단계로 open 해야함(현재 user_data 내에 데이터가 있음.)
      try:
        response = auth.AuthController.login_user(uid, u_email, u_pw)

        actual_data = response.get("user_data", {})

        ## backend에서 가지고 왔는지 확인
        if not response.get("success"):
          raise Exception(response.get("msg", "로그인에 실패했습니다."))

        ## 데이터 계ㅡㅊㅇ에서 가져오기
        emp_id = actual_data.get("employee_id")
        emp_name = actual_data.get("username")
        emp_email = actual_data.get("email")
        emp_pos = actual_data.get("emp_position_id")   

        # [수정] 가장 원시적이지만 확실한 방법: page 객체에 직접 저장
        # 이렇게 하면 session이나 client_storage 에러를 피할 수 있습니다.
        self.main_page.user_id = emp_id
        self.main_page.user_name = emp_name
        self.main_page.user_email = emp_email
        self.main_page.user_pos = emp_pos

        ## 터미널 확인용
        print(f"✅ 로그인 성공: {emp_name}({emp_pos}) | ID: {emp_id}")
        self.on_login_success()

      except Exception as api_error:
        print(f"api 상세에러: {api_error}")  
        self.main_page.show_dialog(
          ft.SnackBar(ft.Text(f"인증 실패: {str(api_error)}"), bgcolor=cm.INCORRECT_POPUPCOLOR)
          )
        self.main_page.update()
        return

      except Exception as err:
        # 예상치 못한 시스템 로직 에러 처리
        print(f"🔥 [시스템 에러]: {err}")

      # 2. 터미널에서 데이터 확인용 출력
      login_data = json.dumps({"id": uid, "email": u_email, "password": u_pw})
      print(f"--- [데이터 확인] ---")
      print(f"ID: {uid} | Email: {u_email}")
      print(f"성공 데이터: {login_data}")

      # 3. [핵심] 유효성 검사 없이 바로 성공 콜백 실행
      # 이 줄이 실행되면 무조건 다음 화면으로 넘어갑니다.
      # self.on_login_success() 

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
  def dummy_success_action():
    print("로그인 버튼 클릭 완료! (테스트)")

  login_view = ErpLoginView(page, dummy_success_action)
  page.add(login_view)


# ## 테스트용 실행(이후에는 연결고리를 만들 것)
# if __name__ == "__main__": 
#   ft.app(target=main, assets_dir="assets")