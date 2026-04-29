# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------
def sign_up_view(page: ft.Page):
    storage = page.session.store
    # -----------------------------------------------------------------------------------------------
    # Default Value
    # -----------------------------------------------------------------------------------------------
    def email_on_change(e):
        storage.set("user_email", e.control.value)
    def name_on_change(e):
        storage.set("user_name", e.control.value)
    def password_on_change(e):
        storage.set("user_password", e.control.value)
    email_input = dogdog.input_textfield(
        hint_text="example@gmail.com", max_length=None, # type: ignore
        on_change=email_on_change, input_type="email"
    )
    name_input = dogdog.input_textfield(
        hint_text="닉네임", on_change=name_on_change
    )
    password_input = dogdog.input_textfield(
        hint_text="비밀번호", max_length=None, # type: ignore
        on_change=password_on_change, input_type="password"
    )
    if storage.get("user_email"):
        email_input.value = storage.get("user_email") # type: ignore
    if storage.get("user_name"):
        name_input.value = storage.get("user_name") # type: ignore
    if storage.get("user_password"):
        password_input.value = storage.get("user_password") # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Sign Up Page
    # ---------------------------------------------------------------------------------------------------
    content_column = [
        dogdog.basic_text(value="프로필을 완성하세요.", weight="bold", size=24),
        dogdog.basic_text(value="이메일", weight="bold"),
        email_input,
        ft.Container(height=10),
        dogdog.basic_text(value="닉네임", weight="bold"),
        name_input,
        dogdog.basic_text(value="비밀번호", weight="bold"),
        password_input,
    ]
    
    return content_column