# -------------------------------------------------------------------------------------------------------
import flet as ft
from flet import DeviceOrientation
import domains
import time , asyncio
import components as dogdog
from api.user_data import User
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
        # User Data Check
        # -----------------------------------------------------------------------------------------------
        if User.pet_list:
            self.storage.set("pet_list", User.pet_list)
            (self.storage.set("customer_detail", User.customer_food_detail)
                if User.customer_food_detail else None)
            self.storage.set("history", User.pet_log) if User.pet_log else None
            self.is_onboarding_complete = True
        else:
            self.is_onboarding_complete = False
        # -----------------------------------------------------------------------------------------------
        # Init First View
        # -----------------------------------------------------------------------------------------------
        page.views.clear()
        target_route = "/home" if self.is_onboarding_complete else "/sign_up"
        if self.page.route == target_route: self.routing_view(page_name=target_route)
        else: page.go(target_route)
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
                    await focus_field.focus()
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
                self.storage.clear()
                self.storage.set("pet_list", User.pet_list)
                (self.storage.set("customer_detail", User.customer_food_detail)
                    if User.customer_food_detail else None)
                self.storage.set("history", User.pet_log) if User.pet_log else None
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