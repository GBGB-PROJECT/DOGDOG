# -------------------------------------------------------------------------------------------------------
import flet as ft
from flet import DeviceOrientation
import domains
import time
import asyncio
import components as dogdog

IS_TEST_MODE = True
test_page = ""
# -------------------------------------------------------------------------------------------------------
# Mobile Platform
# flet build apk --verbose --compile-app --compile-packages --arch arm64-v8a
# -------------------------------------------------------------------------------------------------------
test_page = "Browser" # APP Build Test 시 주석 처리
# -------------------------------------------------------------------------------------------------------
class Front_dogdog:
    def __init__(self, page: ft.Page):
        # -----------------------------------------------------------------------------------------------
        # Default Page Value
        # -----------------------------------------------------------------------------------------------
        self.page = page
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
            ),page_transitions=ft.PageTransitionsTheme(
                android="None", # type: ignore
                ios="None", # type: ignore
                macos="None", # type: ignore
                linux="None", # type: ignore
                windows="None", # type: ignore
            )
        )
        page.on_route_change = self.on_route_change
        page.on_view_pop = self.handle_back
        # -----------------------------------------------------------------------------------------------
        # Init First View & dev_auto_login Trigger
        # -----------------------------------------------------------------------------------------------
        page.views.clear()
        
        if IS_TEST_MODE:
            self.is_onboarding_complete = False # Default until sync
            
            # 임시 로딩 뷰 생성 및 저장 (텍스트 갱신용)
            self.loading_text = ft.Text("데이터를 릴레이하는 중입니다...", size=16, weight="bold")
            
            loading_view = ft.View(
                route="/loading",
                bgcolor="#FFFFFF",
                controls=[
                    ft.Column(
                        expand=True,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.ProgressRing(),
                            self.loading_text
                        ]
                    )
                ]
            )
            self.page.views.append(loading_view)
            self.page.update()
            
            self.page.run_task(self.dev_auto_login)
        else:
            self.is_onboarding_complete = False
            target_route = "/home" if self.is_onboarding_complete else "/sign_up"
            if self.page.route == target_route: self.routing_view(page_name=target_route)
            else: page.go(target_route)
            
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
            payload = {"email": "test7@test.com", "password": "A12345678!"}
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
                    await self.page.client_storage.set_async("access_token", access_token)
                    print("[DEV] client_storage에 토큰 저장 성공")
                except Exception as e:
                    print(f"[DEV] client_storage 저장 실패 (무시됨): {e}")
                    
            print("<< 로그인 성공!")
            
            print(">> 유저 및 Pet ID 조회를 시도합니다...")
            # Step B-1: Get pet_id
            res_user = await api_client.get("/users/id", params={"email": "test7@test.com"})
            if res_user.status_code != 200:
                raise Exception(f"Get User failed: {res_user.status_code}")
            
            try:
                # JSON 구조: {"success": true, "data": {"customer_id": 1001, "pets": [{"pet_id": 3001}]}}
                user_data = res_user.json().get("data", {})
                pets = user_data.get("pets", [])
                
                if pets and len(pets) > 0:
                    pet_id = pets[0].get("pet_id")
                    if not pet_id:
                        raise Exception("pets 배열 내에 pet_id가 없습니다.")
                else:
                    raise Exception("pets 배열이 비어 있습니다.")
            except Exception as e:
                raise Exception(f"JSON 파싱 에러: {e}")
                
            self.page.session.store.set("current_pet_id", pet_id)
            
            # UI 렌더링을 위한 임시 pet_list 구조체 생성
            mock_pet_list = {
                pet_id: {"nickname": "테스트댕댕이", "birth_day": "2023-01-01", "sex": "1", "profile_image": None}
            }
            self.page.session.store.set("pet_list", mock_pet_list)
            
            print(f"<< Pet ID({pet_id}) 조회 성공 및 임시 pet_list 초기화 완료!")
            
            print(f">> 대시보드 데이터(Pet ID: {pet_id}) 조회를 시도합니다...")
            # Step B-2: Get dashboard
            res_dash = await api_client.get(f"/home/dashboard/{pet_id}")
            if res_dash.status_code != 200:
                raise Exception(f"Dashboard sync failed: {res_dash.status_code}")
                
            dash_data = res_dash.json().get("data", res_dash.json())
            print("<< 대시보드 데이터 조회 성공!")
            
            # Map dashboard data to UI state
            customer_detail = {
                "dashboard_sync": dash_data
            }
            self.storage.set("customer_detail", customer_detail)
            
            # UI 렌더링을 위한 임시 history(활동 로그) 구조체 생성
            mock_history = {
                33: {"category":"급여량", "log_status":"77", "log_date":"2026-04-25 13:41:30.000"},
                88: {"category":"산책", "log_status":"30", "log_date":"2026-04-25 18:41:30.000"}
            }
            self.page.session.store.set("history", mock_history)
            
            print("[DEV] Auto login relay Success. Routing to /home")
            self.is_onboarding_complete = True
            
            if self.page.route == "/home":
                self.routing_view(page_name="/home")
            else:
                self.page.go("/home")
                
            self.page.update()
                
        except Exception as e:
            print(f"[DEV] Error during auto relay: {e}")
            
            # 화면에 에러 표시 및 3초 대기
            if hasattr(self, 'loading_text'):
                self.loading_text.value = f"오류 발생: {e}"
                self.loading_text.color = ft.Colors.RED
                self.page.update()
                await asyncio.sleep(3)
                
            self.is_onboarding_complete = False
            self.page.go("/sign_up")
    # ---------------------------------------------------------------------------------------------------
    # Route Change & Android OnBackPressedCallback Event
    # ---------------------------------------------------------------------------------------------------
    def on_route_change(self, e):
        route = e.route
        if len(self.page.views) > 1 and self.page.views[-2].route == route:
            self.page.views.pop()
            self.page.update()
        elif len(self.page.views) == 0 or self.page.views[-1].route != route:
            self.routing_view(page_name=route)
    def handle_back(self, e=None):
        if len(self.page.views) > 1:
            self.page.views.pop()
            self.page.go(self.page.views[-1].route)
    # ---------------------------------------------------------------------------------------------------
    # View Routing Event
    # ---------------------------------------------------------------------------------------------------  
    def routing_view(self, page_name):
        appbar_status = [
            # Icon , Text , On_click
            (ft.Icons.HOME, "Home", lambda _:self.page.go("/home")),
            (ft.Icons.CALENDAR_MONTH, "Log", lambda _:self.page.go("/log")),
            ("skeleton.png", None, lambda _:self.page.go("/shop")),
            (ft.Icons.MESSENGER_OUTLINE_ROUNDED, "Contents", lambda _:self.page.go("/contents")),
            (ft.Icons.PERSON_OUTLINE, "MyPage", lambda _:self.page.go("/mypage")),
        ]
        if self.is_onboarding_complete == False:
            basic_content, focus_field = domains.on_boarding_tile(
                page=self.page, content_page=page_name, change_page_callback=self.page.go
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
                expand=True, controls=basic_content # type: ignore
            )
            layout = ft.Container(expand=True, padding=20, on_click=view_click, content=main_column)
            new_view = ft.View(
                route=page_name, padding=0, spacing=0, bgcolor="#FFFFFF", controls=[layout]
            )
            if page_name == "/sign_up_success":
                new_view.bgcolor = "#FEF3B9"
                self.page.views.clear()
                layout.on_click = lambda _:self.page.go("/home")
                self.is_onboarding_complete = True
        else:
            # print(len(self.page.views))
            if page_name == "/home":
                self.page.views.clear()
            home_background , main_container_content = domains.home_tile(
                page=self.page, content_page=page_name, change_page_callback=self.page.go
            )
            main_container = ft.Container(expand=True, padding=ft.Padding.only(left=10, right=10), 
            content=ft.Column(
                expand=True,
                controls=main_container_content))
            layout = ft.Stack(expand=True, controls=[home_background, main_container])
            new_view = ft.View(
                route=page_name, padding=0, spacing=0, bgcolor="#FFFFFF", controls=[layout]
            )
            new_view.bottom_appbar = dogdog.home_bottom_appbar(appbar_status, page_name)
        self.page.views.append(new_view)
        self.page.update()
# -------------------------------------------------------------------------------------------------------
async def main(page: ft.Page): 
    front_end = Front_dogdog(page=page)
    if page.platform == ft.PagePlatform.ANDROID:
        await page.set_allowed_device_orientations([DeviceOrientation.PORTRAIT_UP])
# -------------------------------------------------------------------------------------------------------
if test_page == "Browser":
    import logging, warnings
    level=logging.INFO
    logging.basicConfig(level=level)
    warnings.filterwarnings(action="ignore")
    if __name__ == "__main__":
        import webbrowser, os
        if os.getenv(key="FLET_NO_BROWSER"):
            webbrowser.open = lambda *args: None
        ft.run(main=main, assets_dir="assets", view=ft.AppView.WEB_BROWSER, port=34636)
else:
    if __name__ == "__main__": ft.run(main=main, assets_dir="assets")