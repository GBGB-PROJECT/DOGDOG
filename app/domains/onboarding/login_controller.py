import flet as ft
import httpx
import asyncio

class LoginController:
    """
    [Controller] LoginController
    역할: 이메일 로그인 프로세스를 httpx를 통해 비동기적으로 처리하고 세션을 관리합니다.
    """
    def __init__(self, page: ft.Page, change_page_callback):
        self.page = page
        self.storage = page.session.store
        self.change_page_callback = change_page_callback

    async def process_email_login(self, email: str, password: str):
        """이메일 로그인 처리 (ApiClient 통합 버전)"""
        
        import re
        from api_client import ApiClient
        
        print(f"DEBUG: email='{email}', pw='{password}'")
        
        # 1단계: 빈 값 검증
        if not email or not password:
            self._show_snack_bar("이메일과 비밀번호를 모두 입력해 주세요.")
            return

        # 2단계: 길이 검증
        if len(email) > 50:
            self._show_snack_bar("이메일은 50자를 초과할 수 없습니다.")
            return

        # 3단계: 형식 검증 (정규 표현식)
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        if not re.match(email_regex, email):
            self._show_snack_bar("올바른 이메일 형식이 아닙니다.")
            return

        try:
            api = ApiClient(self.page)
            
            # 4단계: 가입 여부 사전 검증 API 호출 (ApiClient 활용)
            print(f"🔍 [LoginController] 가입 여부 사전 검증 시작: {email}")
            check_res = await api.get(f"/auth/check-email?email={email}")
            
            if check_res.status_code == 200:
                is_duplicate = check_res.json().get("is_duplicate", False)
                if not is_duplicate:
                    self._show_snack_bar("가입되지 않은 이메일입니다.")
                    return
            
            # 5단계: 본 로그인 API 호출
            print(f"🚀 [LoginController] 본 로그인 API 호출 시작")
            payload = {"email": email, "password": password}
            
            try:
                response = await api.post("/auth/login", data=payload)
                
                # [수정] 400, 401, 404 등 실패 응답 처리
                if response.status_code in [400, 401, 404]:
                    self._show_snack_bar("잘못된 비밀번호이거나 가입되지 않은 이메일입니다.")
                    return

                if response.status_code == 200:
                    res_data = response.json()
                    auth = res_data.get("authorization", res_data) 
                    access_token = auth.get("access_token")
                    refresh_token = auth.get("refresh_token")

                    if access_token and refresh_token:
                        self.storage.set("access_token", access_token)
                        self.storage.set("refresh_token", refresh_token)
                        
                        # ---------------------------------------------------------------------------------------
                        # [데이터 동기화] ApiClient를 활용하여 안전하게 데이터 Prefetch
                        # ---------------------------------------------------------------------------------------
                        try:
                            # 1. 반려동물 목록 조회
                            pets_res = await api.get("/pets")
                            if pets_res.status_code == 200:
                                pets_data = pets_res.json().get("data", [])
                                if pets_data:
                                    first_pet = pets_data[0]
                                    pet_id = first_pet.get("pet_id")
                                    
                                    real_pet_list = {}
                                    for pet in pets_data:
                                        p_id = pet.get("pet_id")
                                        real_pet_list[p_id] = {
                                            "nickname": pet.get("nickname", "이름없음"),
                                            "birth_day": pet.get("birth_day", "2023-01-01"),
                                            "sex": pet.get("sex", 1),
                                            "profile_image": pet.get("profile_image"),
                                        }

                                    self.storage.set("pet_list", real_pet_list)
                                    self.storage.set("current_pet_id", pet_id)
                                    
                                    # [핵심 수정] 반려동물이 존재하면 데이터 동기화 결과와 관계없이 기본 플래그 우선 설정
                                    self.storage.set("is_onboarding_complete", True)
                                    self.storage.set("trigger_feeding_guide_popup", True)
                                    
                                    # 2. 대시보드 데이터 동기화
                                    res_dash = await api.get(f"/home/dashboard/{pet_id}")
                                    dash_data = res_dash.json().get("data") or {} if res_dash.status_code == 200 else {}

                                    self.storage.set("history", dash_data.get("history", {}) if isinstance(dash_data.get("history"), dict) else {})
                                    self.storage.set("customer_detail", {"dashboard_sync": dash_data})

                                    # 3. 사료 상세 정보 조회 (고스트 데이터 방지)
                                    self.storage.set("pet_food_detail", {})
                                    res_food = await api.get(f"/pets/{pet_id}/pet_food")
                                    pet_food_data = res_food.json().get("data") or {} if res_food.status_code == 200 else {}
                                    self.storage.set("pet_food_detail", pet_food_data)

                                else:
                                    self._show_snack_bar("등록된 반려동물이 없습니다. 온보딩을 진행해 주세요.")
                            else:
                                print(f"❌ [LoginController] 반려동물 목록 조회 실패 (Status: {pets_res.status_code})")
                        except Exception as sync_ex:
                            print(f"❌ [LoginController] 데이터 동기화 중 예외 발생 (일부 생략될 수 있음): {sync_ex}")

                        self.change_page_callback("/home")
                        return
                    else:
                        self._show_snack_bar("서버 응답 형식이 올바르지 않습니다.")
                        return
                else:
                    self._show_snack_bar("로그인 정보가 일치하지 않습니다.")
                    return

            except httpx.HTTPStatusError as status_ex:
                print(f"❌ [LoginController] HTTP 상태 에러: {status_ex}")
                self._show_snack_bar("잘못된 비밀번호입니다.")
                return

        except Exception as ex:
            print(f"❌ [LoginController] 처리 중 예외 발생: {str(ex)}")
            self._show_snack_bar("서버와 통신할 수 없습니다. 네트워크 상태를 확인해 주세요.")
            return

    def _show_snack_bar(self, message: str):
        """안내용 스낵바 출력"""
        snack_bar = ft.SnackBar(
            content=ft.Text(value=message),
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
