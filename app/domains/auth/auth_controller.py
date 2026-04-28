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

            # -------------------------------------------------------------------------------------------
            # [추가] 실시간 데이터 동기화 (홈 화면 렌더링용)
            # -------------------------------------------------------------------------------------------
            # 3. 반려견 정보 동기화 (pet_list)
            print("[AuthController] 반려동물 상세 정보 동기화 중...")
            res_pets = await self.api_client.get("/pets")
            if res_pets.status_code == 200:
                pets_data = res_pets.json().get("data") or []
                real_pet_list = {}
                for pet in pets_data:
                    p_id = pet.get("pet_id")
                    real_pet_list[p_id] = {
                        "nickname": pet.get("nickname", "이름없음"),
                        "birth_day": pet.get("birth_day", "2023-01-01"),
                        "sex": pet.get("sex", 1), # 정수형 저장
                        "profile_image": pet.get("profile_image"),
                    }
                self.page.session.store.set("pet_list", real_pet_list)
                
                # 만약 pet_id가 없는데 조회된 데이터가 있다면 첫 번째 펫을 기본값으로
                if not pet_id and pets_data:
                    pet_id = pets_data[0].get("pet_id")
                    self.page.session.store.set("current_pet_id", pet_id)
            
            # 4. 대시보드 통계 데이터 동기화
            if pet_id:
                print(f"[AuthController] 대시보드 데이터 동기화 중... (ID: {pet_id})")
                res_dash = await self.api_client.get(f"/home/dashboard/{pet_id}")
                if res_dash.status_code == 200:
                    dash_data = res_dash.json().get("data") or {}
                    self.page.session.store.set("customer_detail", {"dashboard_sync": dash_data})
                    
                    # 활동 로그(history) 세션 동기화
                    real_history = dash_data.get("history", {})
                    if not isinstance(real_history, dict):
                        real_history = {}
                    self.page.session.store.set("history", real_history)
                else:
                    # 데이터가 없는 경우(콜드 스타트) 빈 값 세팅
                    self.page.session.store.set("customer_detail", {"dashboard_sync": {}})
                    self.page.session.store.set("history", {})

            # 온보딩 완료 플래그 (main.py에서 참조 가능하도록 세션에 기록)
            self.page.session.store.set("is_onboarding_complete", True)

            print(
                f"[AuthController] Session storage updated (Token & Data Sync)"
            )

            # 5. 세션 업데이트 보장 및 이동
            self.page.update()
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
