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
        """이메일 로그인 처리 (httpx 직접 통신 버전)"""
        
        import re
        
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

        endpoint = "http://localhost:8000/api/v1/auth/login"
        payload = {
            "email": email,
            "password": password
        }

        try:
            # 2. httpx.AsyncClient를 사용하여 비동기 통신 (사전 검증 + 본 로그인)
            async with httpx.AsyncClient(timeout=10.0) as client:
                # 4단계: 가입 여부 사전 검증 API 호출
                check_endpoint = f"http://localhost:8000/api/v1/auth/check-email?email={email}"
                check_res = await client.get(check_endpoint)
                
                if check_res.status_code == 200:
                    is_duplicate = check_res.json().get("is_duplicate", False)
                    # is_duplicate가 False(사용 가능)이면, 가입된 적이 없다는 뜻이므로 로그인 차단
                    if not is_duplicate:
                        self._show_snack_bar("가입되지 않은 이메일입니다.")
                        return
                
                # 사전 검증을 통과한 경우에만 실제 로그인 API 호출
                print(f"🚀 [LoginController] 본 로그인 API 호출 시작: {endpoint}")
                response = await client.post(
                    url=endpoint,
                    json=payload, # application/json 형식 보장
                    headers={"Content-Type": "application/json"}
                )

                # 3. 통신 성공 (200 OK) 처리
                if response.status_code == 200:
                    res_data = response.json()
                    
                    # 토큰 추출 및 세션 저장
                    # API 응답 구조에 따라 'authorization' 또는 루트에서 추출
                    auth = res_data.get("authorization", res_data) 
                    access_token = auth.get("access_token")
                    refresh_token = auth.get("refresh_token")

                    if access_token and refresh_token:
                        self.storage.set("access_token", access_token)
                        self.storage.set("refresh_token", refresh_token)
                        
                        # ---------------------------------------------------------------------------------------
                        # [신규 추가] 완벽한 세션 초기화 및 데이터 동기화 (dev_auto_login 흐름 이식)
                        # ---------------------------------------------------------------------------------------
                        try:
                            # 1. 반려동물 목록 조회 및 세션 동기화
                            print("🔍 [LoginController] 반려동물 목록 조회 및 세션 동기화 시작")
                            pets_res = await client.get(
                                "http://localhost:8000/api/v1/pets",
                                headers={"Authorization": f"Bearer {access_token}"}
                            )
                            
                            if pets_res.status_code == 200:
                                pets_data = pets_res.json().get("data", [])
                                if pets_data:
                                    first_pet = pets_data[0]
                                    pet_id = first_pet.get("pet_id")
                                    
                                    # 전체 반려동물 리스트 구성 (세션 저장용)
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
                                    print(f"✅ [LoginController] current_pet_id 및 pet_list 설정 완료: {pet_id}")
                                    
                                    # 2. 대시보드 데이터 사전 동기화 (Data Prefetch)
                                    print(f"🔍 [LoginController] 대시보드 데이터(Pet ID: {pet_id}) 조회를 시도합니다...")
                                    res_dash = await client.get(
                                        f"http://localhost:8000/api/v1/home/dashboard/{pet_id}",
                                        headers={"Authorization": f"Bearer {access_token}"}
                                    )
                                    
                                    if res_dash.status_code == 200:
                                        dash_data = res_dash.json().get("data") or {}
                                    else:
                                        dash_data = {}
                                        print(f"⚠️ [LoginController] Dashboard sync failed. Using empty data.")

                                    # 활동 로그 동기화 (history)
                                    real_history = dash_data.get("history", {})
                                    if not isinstance(real_history, dict):
                                        real_history = {}
                                    self.storage.set("history", real_history)

                                    # 대시보드 전체 데이터 저장
                                    customer_detail = {"dashboard_sync": dash_data}
                                    self.storage.set("customer_detail", customer_detail)
                                    print("✅ [LoginController] 대시보드 데이터 사전 동기화 완료!")

                                    # 3. 사료 상세 정보 조회 및 세션 저장
                                    try:
                                        res_food = await client.get(
                                            f"http://localhost:8000/api/v1/pets/{pet_id}/pet_food",
                                            headers={"Authorization": f"Bearer {access_token}"}
                                        )
                                        pet_food_data = (
                                            res_food.json().get("data") or {}
                                            if res_food.status_code == 200
                                            else {}
                                        )
                                        self.storage.set("pet_food_detail", pet_food_data)
                                        print("✅ [LoginController] 사료 상세 정보 조회 및 저장 완료!")
                                    except Exception as e:
                                        print(f"⚠️ [LoginController] 사료 정보 조회 실패 (무시): {e}")
                                        self.storage.set("pet_food_detail", {})

                                    # 모든 데이터 동기화가 끝난 후
                                    self.storage.set("is_onboarding_complete", True)

                                else:
                                    print("⚠️ [LoginController] 등록된 반려동물이 없습니다.")
                                    self._show_snack_bar("등록된 반려동물이 없습니다. 온보딩을 진행해 주세요.")
                                    # 필요시 온보딩 페이지로 라우팅
                                    # self.change_page_callback("/pet_info")
                                    # return
                            else:
                                print(f"❌ [LoginController] 반려동물 목록 조회 실패 (Status: {pets_res.status_code})")
                        except Exception as sync_ex:
                            print(f"❌ [LoginController] 데이터 동기화 중 예외 발생: {sync_ex}")

                        print("✅ [LoginController] 로그인 및 완벽한 데이터 동기화 완료")
                        #self._show_snack_bar("로그인 성공!")
                        
                        # 모든 동기화 절차가 끝난 후 홈으로 이동
                        self.change_page_callback("/home")
                    else:
                        self._show_snack_bar("서버 응답 형식이 올바르지 않습니다.")
                
                # 4. 로그인 실패 처리
                else:
                    print(f"⚠️ [LoginController] 로그인 실패 (Status: {response.status_code})")
                    self._show_snack_bar("이메일 또는 비밀번호가 일치하지 않습니다.")

        # 5. 네트워크 에러 처리 (서버 다운 등)
        except httpx.RequestError as req_ex:
            print(f"❌ [LoginController] 네트워크 에러: {str(req_ex)}")
            self._show_snack_bar("서버와 통신할 수 없습니다. 네트워크 상태를 확인해 주세요.")
        
        except Exception as ex:
            print(f"❌ [LoginController] 기타 예외 발생: {str(ex)}")
            self._show_snack_bar(f"처리 중 오류가 발생했습니다: {str(ex)}")

    def _show_snack_bar(self, message: str):
        """안내용 스낵바 출력"""
        snack_bar = ft.SnackBar(
            content=ft.Text(value=message),
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
