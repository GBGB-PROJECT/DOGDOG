# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains
from domains.onboarding.views.splash import splash_view
import time
import asyncio
import components as dogdog

# 테스트 아이디로 테스트 설정
IS_TEST_MODE = False
test_page = ""
# -------------------------------------------------------------------------------------------------------
# Mobile Platform
# flet build apk --verbose --compile-app --compile-packages --arch arm64-v8a
# flet build apk --verbose --compile-app --compile-packages #맥용
# -------------------------------------------------------------------------------------------------------
test_page = "Browser"  # APP Build Test 시 주석 처리


# -------------------------------------------------------------------------------------------------------
class Front_dogdog:
    def __init__(self, page: ft.Page):
        # -----------------------------------------------------------------------------------------------
        # Default Page Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
        self.popup = dogdog.Popup(page)
        self.storage = page.session.store
        self.home_feeding_guide_popup = True
        page.title = "Dog Dog"
        page.theme_mode = ft.ThemeMode.LIGHT
        page.fonts = {"Pretendard": "fonts/Pretendard-Regular.otf"}
        page.theme = ft.Theme(
            font_family="Pretendard",
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLACK,
                on_primary=ft.Colors.WHITE,
                surface=ft.Colors.WHITE,
                on_surface=ft.Colors.BLACK,
                on_surface_variant=ft.Colors.BLACK,
            ),
            page_transitions=ft.PageTransitionsTheme(
                android="None",  # type: ignore
                ios="None",  # type: ignore
                macos="None",  # type: ignore
                linux="None",  # type: ignore
                windows="None",  # type: ignore
            ),
        )
        page.on_route_change = self.on_route_change
        page.on_view_pop = self.handle_back
        # -----------------------------------------------------------------------------------------------
        # Init First View & dev_auto_login Trigger
        # -----------------------------------------------------------------------------------------------
        page.views.clear()

        if IS_TEST_MODE:
            self.is_onboarding_complete = False
            page.go("/splash")  # 스플래시로 먼저 진입
            self.page.run_task(self.dev_auto_login)
        else:
            self.is_onboarding_complete = False
            page.go("/splash")  # 일반 모드에서도 스플래시 우선

    # ---------------------------------------------------------------------------------------------------
    # Dev Auto Login Relay
    # ---------------------------------------------------------------------------------------------------
    async def dev_auto_login(self, *args):
        try:
            from api_client import ApiClient

            api_client = ApiClient(self.page)

            print("[DEV] Starting auto login relay...")
            print(">> 로그인을 시도합니다...")
            # Step A: Login
            payload = {"email": "test050205@test.com", "password": "A12345678!"}
            res_login = await api_client.post("/auth/login", data=payload)
            if res_login.status_code != 200:
                raise Exception(f"Login failed: {res_login.text}")

            token_data = res_login.json()
            print(f"로그인 응답 데이터: {token_data}")

            # 1. FastAPI 기본 구조 확인
            access_token = token_data.get("access_token")
            # 2. 만약 없다면 authorization 내부 확인
            if not access_token:
                access_token = token_data.get("authorization", {}).get("access_token")

            if not access_token:
                raise Exception("로그인 응답에서 access_token을 찾을 수 없습니다.")

            self.page.session.store.set("access_token", access_token)

            # client_storage 안전 저장 로직
            if hasattr(self.page, "client_storage"):
                try:
                    await self.page.client_storage.set_async(
                        "access_token", access_token
                    )
                    print("[DEV] client_storage에 토큰 저장 성공")
                except Exception as e:
                    print(f"[DEV] client_storage 저장 실패 (무시됨): {e}")

            print("<< 로그인 성공!")

            print(">> 유저 및 Pet ID 조회를 시도합니다...")
            # Step B-1: Get pet_id
            # Step B-1: Get pet_id and pet info (API Response 1 format)
            print(">> 반려동물 목록 조회를 시도합니다...")
            res_pets = await api_client.get("/pets")
            if res_pets.status_code != 200:
                raise Exception(f"Get Pets failed: {res_pets.status_code}")

            try:
                # API 응답 1: {"status": "success", "data": [{"pet_id": 3001, "nickname": "...", ...}]}
                pets_data = res_pets.json().get("data") or []
                if not pets_data:
                    raise Exception("등록된 반려동물이 없습니다. (Cold Start)")

                # 리스트의 첫 번째 항목에서 정보 추출
                first_pet = pets_data[0]
                pet_id = first_pet.get("pet_id")

                # 전체 반려동물 리스트 구성 (세션 저장용)
                real_pet_list = {}
                for pet in pets_data:
                    p_id = pet.get("pet_id")
                    real_pet_list[p_id] = {
                        "nickname": pet.get("nickname", "이름없음"),
                        "birth_day": pet.get("birth_day", "2023-01-01"),
                        "sex": pet.get("sex", 1),  # 정수형으로 저장 (지시 사항 준수)
                        "profile_image": pet.get("profile_image"),
                    }

                self.page.session.store.set("pet_list", real_pet_list)
                self.page.session.store.set("current_pet_id", pet_id)
                print(f"<< 반려동물 정보 동기화 완료! (ID: {pet_id})")

            except Exception as e:
                raise Exception(f"Pet Info 파싱 에러: {e}")

            # -------------------------------------------------------------------------------------------
            # Step B-2: Get dashboard
            # -------------------------------------------------------------------------------------------
            print(f">> 대시보드 데이터(Pet ID: {pet_id}) 조회를 시도합니다...")
            res_dash = await api_client.get(f"/home/dashboard/{pet_id}")
            if res_dash.status_code != 200:
                # 콜드 스타트 상태일 경우 빈 딕셔너리로 진행 유도 (에러 발생시키지 않음)
                print(
                    f"[DEV] Dashboard sync failed: {res_dash.status_code}. Using empty data."
                )
                dash_data = {}
            else:
                dash_data = res_dash.json().get("data") or {}

            print("<< 대시보드 데이터 조회 성공!")

            # 사료 상세 정보 조회 및 세션 저장
            try:
                res_food = await api_client.get(f"/pets/{pet_id}/pet_food")
                pet_food_data = (
                    res_food.json().get("data") or {}
                    if res_food.status_code == 200
                    else {}
                )
                self.storage.set("pet_food_detail", pet_food_data)
                print("<< 사료 상세 정보 조회 및 저장 성공!")
            except Exception as e:
                print(f"[DEV] 사료 정보 조회 실패 (무시): {e}")
                self.storage.set("pet_food_detail", {})

            # 2. 활동 로그 동기화 (history)
            real_history = dash_data.get("history", {})
            if not isinstance(real_history, dict):
                real_history = {}
            self.page.session.store.set("history", real_history)

            # 3. 대시보드 전체 데이터 저장
            customer_detail = {"dashboard_sync": dash_data}
            self.storage.set("customer_detail", customer_detail)

            print("[DEV] Auto login relay Success. Routing to /home")
            self.is_onboarding_complete = True

            # 스플래시 화면이 로직을 제어하므로 명시적 이동 제거 또는 /splash로 유지
            if self.page.route != "/splash":
                self.page.go("/splash")

            self.page.update()

        except Exception as e:
            print(f"[DEV] Auto login failed: {e}")

    async def refresh_home_data(self):
        """대시보드 데이터를 다시 fetch하고 화면을 갱신합니다."""
        try:
            from api_client import ApiClient

            api_client = ApiClient(self.page)

            pet_id = (
                self.storage.get("pet_id")
                or self.storage.get("customer_pet_id")
                or self.storage.get("current_pet_id")
            )

            print(f"🏠 [HOME DEBUG] Dashboard API 호출 시도 - Pet ID: {pet_id}")
            res_dash = await api_client.get(f"/home/dashboard/{pet_id}")

            if res_dash.status_code == 200:
                dash_data = res_dash.json().get("data") or {}
                print(f"🏠 [HOME DEBUG] 수신된 데이터: {res_dash.json()}")

                # 사료 상세 정보 조회 및 세션 저장
                try:
                    res_food = await api_client.get(f"/pets/{pet_id}/pet_food")
                    pet_food_data = (
                        res_food.json().get("data") or {}
                        if res_food.status_code == 200
                        else {}
                    )
                    self.storage.set("pet_food_detail", pet_food_data)
                    print("🏠 [HOME DEBUG] 사료 상세 정보 갱신 완료!")
                except Exception as e:
                    print(f"[HOME DEBUG] 사료 정보 갱신 실패 (무시): {e}")
                    self.storage.set("pet_food_detail", {})

                # 1. 활동 로그 동기화
                real_history = dash_data.get("history", {})
                self.page.session.store.set("history", real_history)

                # 2. 대시보드 전체 데이터 저장
                customer_detail = {"dashboard_sync": dash_data}
                self.storage.set("customer_detail", customer_detail)

                # 3. 화면 갱신
                if self.page.route == "/home":
                    await self.routing_view(page_name="/home")
                self.page.update()
                print("🏠 [HOME DEBUG] 대시보드 데이터 갱신 완료!")
            else:
                print(f"[HOME DEBUG] Dashboard refresh failed: {res_dash.status_code}")
        except Exception as e:
            print(f"[HOME DEBUG] Error during dashboard refresh: {e}")

    # ---------------------------------------------------------------------------------------------------
    # Route Change & Android OnBackPressedCallback Event
    # ---------------------------------------------------------------------------------------------------
    async def on_route_change(self, e):
        route = e.route
        
        # [수정 1] 라우팅 게이트키퍼: 모든 페이지 이동 시 팝업 잔상 강제 소거
        self.page.overlay.clear()
        self.page.dialog = None
        self.page.update()
        if (
            len(self.page.views) > 1
            and self.page.views[-2].route == route
            and route != "/history"
        ):
            self.page.views.pop()
        elif len(self.page.views) == 0 or self.page.views[-1].route != route:
            # 새 페이지로 이동 시 기존 뷰 스택을 유지하여 뒤로가기 기능을 지원함
            # self.page.views.clear()  # 스택 유지를 위해 주석 처리
            await self.routing_view(page_name=route)

    def handle_back(self, e=None):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.go(self.page.views[-1].route)

    # ---------------------------------------------------------------------------------------------------
    # View Routing Event
    # ---------------------------------------------------------------------------------------------------
    async def routing_view(self, page_name):
        # [치명적 버그 수정] 페이지 이동 시 모든 팝업, 다이얼로그, 오버레이 강제 초기화 (잔상 제거)
        self.page.dialog = None
        self.page.banner = None

        # 팝업 바텀시트 등 오버레이 요소들 안전하게 닫고 비우기
        for control in self.page.overlay[:]:
            if hasattr(control, "open"):
                control.open = False
        self.page.overlay.clear()

        self.page.update()  # UI 상태 즉시 반영

        if not "address" in page_name:
            dogdog.task_controls(30)
        # 1. 하단 앱바 설정
        appbar_status = [
            # Icon , Text , On_click
            (ft.Icons.HOME, "Home", lambda _: self.page.go("/home")),
            (ft.Icons.CALENDAR_MONTH, "Log", lambda _: self.page.go("/log")),
            (
                "skeleton.png" if not "/shop" in page_name else "shop.png",
                None,
                lambda _: self.page.go("/shop"),
            ),
            (
                ft.Icons.MESSENGER_OUTLINE_ROUNDED,
                "Contents",
                lambda _: self.page.go("/contents"),
            ),
            (ft.Icons.PERSON_OUTLINE, "MyPage", lambda _: self.page.go("/mypage")),
        ]

        # 2. 라우트 성격 분류
        if page_name == "/splash":
            self.page.views.append(splash_view(self.page))
            self.page.update()
            return

        onboarding_routes = [
            "/login",
            "/login_email",
            "/sign_up",
            "/pet_info",
            "/pet_obesity",
            "/pet_activity",
            "/pet_health",
            "/pet_food",
            "/sign_up_success",
        ]

        # 3. [교통 정리] 온보딩 라우트와 일반(홈) 라우트를 명확히 분리
        if page_name in onboarding_routes:
            # --- 온보딩 뷰 생성 (On-boarding Tile) ---
            basic_content, focus_field = domains.on_boarding_tile(
                page=self.page,
                popup=self.popup,
                content_page=page_name,
                change_page_callback=self.page.go,
            )

            async def view_click(e):
                if focus_field:
                    self.page.update()
                    if focus_field.page:
                        try:
                            await asyncio.sleep(0.1)
                            await focus_field.focus()
                        except Exception:
                            pass
                    self.page.update()

            main_column = ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                controls=basic_content,  # type: ignore
            )
            layout = ft.Container(
                expand=True, padding=20, on_click=view_click, content=main_column
            )
            new_view = ft.View(
                route=page_name,
                padding=0,
                spacing=0,
                bgcolor="#FFFFFF",
                controls=[layout],
            )
            # 온보딩 완료 시점 처리
            if page_name == "/sign_up_success":
                new_view.bgcolor = "#FEF3B9"
                self.page.views.clear()
                layout.on_click = lambda _: self.page.go("/home")
                self.page.session.store.set("is_onboarding_complete", True)
                self.home_feeding_guide_popup = True  # 온보딩 완료 시 팝업 노출 활성화

        else:
            # --- 일반 서비스 뷰 생성 (Home Tile) ---
            if page_name == "/home":
                self.page.views.clear()
                self.page.update()  # 뷰를 비운 직후 즉시 갱신하여 로딩 화면처럼 보이게 함

            # [해결] home_tile이 비동기 함수가 되었으므로 await를 추가하여 언패킹 에러를 방지합니다.
            home_background, main_container_content = await domains.home_tile(
                page=self.page,
                popup=self.popup,
                content_page=page_name,
                change_page_callback=self.page.go,
                on_refresh_callback=self.refresh_home_data,
            )
            print("refresh_home_data: ", self.refresh_home_data)
            main_container = ft.Container(
                expand=True,
                padding=ft.Padding.only(left=10, right=10),
                content=ft.Column(expand=True, controls=main_container_content),
            )
            layout = ft.Stack(expand=True, controls=[home_background, main_container])
            new_view = ft.View(
                route=page_name,
                padding=0,
                spacing=0,
                bgcolor="#FFFFFF",
                controls=[layout],
            )
            not_bottom_appbar = [
                # page_name
                "/shop/product",
                "/shop/order",
                "/shop/subs_start",
                "/shop/subs_order",
                "/shop/address",
            ]
            if not any(page in page_name for page in not_bottom_appbar):
                new_view.bottom_appbar = dogdog.home_bottom_appbar(
                    appbar_status, page_name
                )
        self.page.views.append(new_view)
        # [해결] 홈 화면 진입 시 AI 권장 급여량 팝업 연동 (TypeError 해결 및 API 연동)
        if page_name == "/home" and self.home_feeding_guide_popup:
            try:
                # [신규 추가] 급여 중인 사료 정보가 없으면 팝업 노출 차단
                pet_food_detail = self.storage.get("pet_food_detail")

                # 사료 데이터가 비어있거나, 딕셔너리가 아니거나, 내용이 없으면 건너뜀
                if (
                    not pet_food_detail
                    or not isinstance(pet_food_detail, dict)
                    or not pet_food_detail.get("pet_food_id")
                ):
                    print(
                        "[DEBUG] 등록된 사료 정보가 없어 권장 급여량 팝업을 차단합니다."
                    )
                else:
                    from api_client import ApiClient

                    api_client = ApiClient(self.page)

                    # 1. 세션에서 정보 획득
                    pet_id = self.storage.get("current_pet_id")
                    pet_list = self.storage.get("pet_list") or {}
                    pet_info = pet_list.get(pet_id) or pet_list.get(str(pet_id)) or {}
                    pet_name = pet_info.get("nickname", "반려견")

                    # 2. 권장 급여량 API 호출 및 안전한 파싱
                    guide_intake = 0
                try:
                    res_guide = await api_client.get(f"/calc_feeding/{pet_id}/guide")
                    if res_guide.status_code == 200:
                        # [DEBUG] 원본 데이터 확인용 로그 추가
                        raw_data = res_guide.json()
                        print(f"[DEBUG] Guide API 응답: {raw_data}")

                        # 백엔드 실제 Key(adjusted_daily_food_g)를 사용하여 데이터 추출
                        resp_data = raw_data.get("data", {})
                        val = resp_data.get("adjusted_daily_food_g", 0)

                        # 소수점 대비 정수 변환 (예: 168.0 -> 168)
                        guide_intake = int(float(val))
                except Exception as api_err:
                    print(f"[DEBUG] 권장량 API 파싱 에러 (기본값 0 사용): {api_err}")

                # 3. 팝업 호출 (문자열로 변환하여 전달)
                self.popup.show_feeding_guide_open(pet_name, str(guide_intake))

            except Exception as e:
                print(f"[ERROR] 팝업 연동 중 치명적 오류: {e}")
            finally:
                # 4. 재노출 방지 (세션 유지 동안 1회)
                self.home_feeding_guide_popup = False
        dogdog.views_controls(self.page)
        self.page.update()  # 최종 뷰 추가 후 갱신


# -------------------------------------------------------------------------------------------------------
async def main(page: ft.Page):
    front_end = Front_dogdog(page=page)
    if page.platform == ft.PagePlatform.ANDROID:
        await page.set_allowed_device_orientations([ft.DeviceOrientation.PORTRAIT_UP])


# -------------------------------------------------------------------------------------------------------
if test_page == "Browser":
    import logging, warnings

    level = logging.INFO
    logging.basicConfig(level=level)
    warnings.filterwarnings(action="ignore")
    if __name__ == "__main__":
        import webbrowser, os

        if os.getenv(key="FLET_NO_BROWSER"):
            webbrowser.open = lambda *args: None
        ft.run(
            main=main,
            assets_dir="assets",
            view=ft.AppView.WEB_BROWSER,
            port=34636,
            web_renderer=ft.WebRenderer.CANVAS_KIT,
        )
else:
    if __name__ == "__main__":
        ft.run(main=main, assets_dir="assets", web_renderer=ft.WebRenderer.CANVAS_KIT)
