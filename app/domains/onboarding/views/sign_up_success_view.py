# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def signup_success_view(page: ft.Page):
    # ---------------------------------------------------------------------------------------------------
    # Pet Obesity Page
    # ---------------------------------------------------------------------------------------------------
    return [
        ft.Image(src="checkone.png", width=150, height=150),
        dogdog.basic_text(value="회원 가입이 완료되었습니다.", weight="bold", size=20),
        dogdog.basic_text(value=page.session.store.get(key="api_insert_data"))
    ]