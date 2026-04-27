import flet as ft
from api_client import ApiClient


class AuthController:
    """
    AuthController: 인증 및 세션 관리를 담당하는 컨트롤러
    - 가입/로그인 후 토큰 처리 및 초기 데이터 동기화(Relay)를 수행합니다.
    """

    def __init__(self, page: ft.Page):
        self.page = page
        self.api_client = ApiClient(page)

    async def complete_relay(
        self, auth_data: dict, pet_id: int, customer_id: int = 1001
    ):
        """
        가입 또는 로그인 성공 직후, 발급된 토큰과 정보를 세션에 안전하게 저장하고
        홈 화면으로 리다이렉트합니다.
        """
        try:
            print(
                f"[AuthController] Starting session relay for Customer: {customer_id}..."
            )

            # 1. 토큰 저장
            if auth_data:
                self.page.session.store.set(
                    "access_token", auth_data.get("access_token")
                )
                self.page.session.store.set(
                    "refresh_token", auth_data.get("refresh_token")
                )

            # 2. 필수 ID 정보 저장
            self.page.session.store.set("customer_id", customer_id)
            if pet_id:
                self.page.session.store.set("current_pet_id", pet_id)

            # 온보딩 완료 플래그 (main.py에서 참조 가능하도록 세션에 기록)
            self.page.session.store.set("is_onboarding_complete", True)

            print(
                f"[AuthController] Session storage updated (Token): {self.page.session.store.get('access_token')}"
            )

            # 3. 세션 업데이트 보장
            self.page.update()

            # 4. 홈 화면으로 이동
            print("[AuthController] Relay complete. Navigating to /home")
            self.page.go("/home")

            return True

        except Exception as e:
            print(f"[AuthController] Relay 실패: {e}")
            return False

    async def check_email_duplicate(self, email: str):
        """
        이메일 중복 체크 API 호출 (기존 View에 있던 로직을 컨트롤러로 이동 가능)
        """
        try:
            res = await self.api_client.get(
                "/auth/check-email", params={"email": email}
            )
            if res.status_code == 200:
                return res.json().get("is_duplicate", False)
            return True  # 에러 발생 시 안전하게 중복으로 간주
        except Exception:
            return True
