import flet as ft
from api_client import ApiClient
from domains.auth.auth_controller import AuthController

class LoginController:
    """
    [Controller] LoginController
    역할: 로그인 프로세스의 비즈니스 로직(입력 검증, API 통신, 세션 관리)을 담당합니다.
    """
    def __init__(self, page: ft.Page):
        self.page = page
        self.api_client = ApiClient(page)
        self.auth_controller = AuthController(page)

    async def process_email_login(self, email: str, password: str):
        """이메일 로그인 처리"""
        if not email or not password:
            self._show_snack_bar("이메일과 비밀번호를 모두 입력해 주세요.")
            return

        try:
            # 1. 로그인 API 호출 (POST /auth/login)
            payload = {
                "email": email,
                "password": password
            }
            
            print(f"[LoginController] Attempting login for: {email}")
            res = await self.api_client.post("/auth/login", data=payload)

            if res.status_code == 200:
                res_data = res.json()
                auth_data = res_data.get("auth", {})
                pet_id = res_data.get("pet_id")
                customer_id = res_data.get("customer_id")

                # 2. AuthController를 통한 세션 저장 및 데이터 동기화
                # redirect_to=None으로 설정하여 여기서 직접 제어함
                success = await self.auth_controller.complete_relay(
                    auth_data=auth_data,
                    pet_id=pet_id,
                    customer_id=customer_id,
                    redirect_to=None
                )

                if success:
                    print("✅ [LoginController] Login and Sync Success!")
                    self.page.go("/home")
                else:
                    self._show_snack_bar("세션 동기화 중 오류가 발생했습니다.")
            
            elif res.status_code == 401:
                self._show_snack_bar("이메일 또는 비밀번호가 올바르지 않습니다.")
            else:
                error_msg = res.json().get("detail", "로그인에 실패했습니다.")
                self._show_snack_bar(f"로그인 실패: {error_msg}")

        except Exception as ex:
            print(f"❌ [LoginController] Fatal Error: {str(ex)}")
            self._show_snack_bar(f"시스템 오류: {str(ex)}")

    def _show_snack_bar(self, message: str):
        """에러 메시지용 스낵바 출력"""
        snack_bar = ft.SnackBar(
            content=ft.Text(value=message),
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
