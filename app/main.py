# -------------------------------------------------------------------------------------------------------
import flet as ft
import domains
import time
import asyncio
import components as dogdog

# 테스트 아이디(test7)로 테스트 설정
IS_TEST_MODE = False
test_page = ""
# -------------------------------------------------------------------------------------------------------
# Mobile Platform
# flet build apk --verbose --compile-app --compile-packages --arch arm64-v8a
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
            self.is_onboarding_complete = False  # Default until sync

            # 임시 로딩 뷰 생성 및 저장 (텍스트 갱신용)
            self.loading_text = ft.Text(
                "데이터를 릴레이하는 중입니다...", size=16, weight="bold"
            )

            loading_view = ft.View(
                route="/loading",
                bgcolor="#FFFFFF",
                controls=[
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[ft.ProgressRing(), self.loading_text],
                    )
                ],
            )
            self.page.views.append(loading_view)
            self.page.update()

            self.page.run_task(self.dev_auto_login)
        else:
            self.is_onboarding_complete = False
            target_route = "/home" if self.is_onboarding_complete else "/sign_up"
            if self.page.route == target_route:
                self.routing_view(page_name=target_route)
            else:
                page.go(target_route)

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
            payload = {"email": "test042806@test.com", "password": "A12345678!"}
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

            # 즉시 홈 화면으로 이동 및 갱신
            if self.page.route == "/home":
                await self.routing_view(page_name="/home")
            else:
                self.page.go("/home")

            self.page.update()

        except Exception as e:
            print(f"[DEV] Error during auto relay: {e}")

            # 화면에 에러 표시 및 3초 대기 후 가입 화면으로 이동
            if hasattr(self, "loading_text"):
                self.loading_text.value = (
                    f"테스트 계정 정보를 불러올 수 없습니다.\n(에러: {e})"
                )
                self.loading_text.color = ft.Colors.RED
                self.page.update()
                await asyncio.sleep(3)

            self.is_onboarding_complete = False
            self.page.go("/sign_up")
            self.page.update()

    # ---------------------------------------------------------------------------------------------------
    # Route Change & Android OnBackPressedCallback Event
    # ---------------------------------------------------------------------------------------------------
    async def on_route_change(self, e):
        route = e.route
        # self.page.overlay.clear()
        if (
            len(self.page.views) > 1
            and self.page.views[-2].route == route
            and route != "/history"
        ):
            self.page.views.pop()
        elif len(self.page.views) == 0 or self.page.views[-1].route != route:
            # 새 페이지로 이동 시 기존 뷰 스택을 비워 메모리 누수 및 잔상 방지
            self.page.views.clear()
            await self.routing_view(page_name=route)

    def handle_back(self, e=None):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.go(self.page.views[-1].route)

    # ---------------------------------------------------------------------------------------------------
    # View Routing Event
    # ---------------------------------------------------------------------------------------------------
    async def routing_view(self, page_name):
        # 1. 하단 앱바 설정
        appbar_status = [
            (ft.Icons.HOME, "Home", lambda _: self.page.go("/home")),
            (ft.Icons.CALENDAR_MONTH, "Log", lambda _: self.page.go("/log")),
            ("skeleton.png", None, lambda _: self.page.go("/shop")),
            (
                ft.Icons.MESSENGER_OUTLINE_ROUNDED,
                "Contents",
                lambda _: self.page.go("/contents"),
            ),
            (ft.Icons.PERSON_OUTLINE, "MyPage", lambda _: self.page.go("/mypage")),
        ]

        # 2. 라우트 성격 분류
        onboarding_routes = [
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

        else:
            # --- 일반 서비스 뷰 생성 (Home Tile) ---
            if page_name == "/home":
                self.page.views.clear()
                self.page.update()  # 뷰를 비운 직후 즉시 갱신하여 로딩 화면처럼 보이게 함

            home_background, main_container_content = domains.home_tile(
                page=self.page,
                popup=self.popup,
                content_page=page_name,
                change_page_callback=self.page.go,
            )
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
            # 일반 서비스 뷰에는 하단 앱바를 붙임
            new_view.bottom_appbar = dogdog.home_bottom_appbar(appbar_status, page_name)

        self.page.views.append(new_view)
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
        ft.run(main=main, assets_dir="assets")
