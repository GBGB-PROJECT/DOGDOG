# -------------------------------------------------------------------------------------------------------
from datetime import date
from dateutil.relativedelta import relativedelta
import re, hashlib
import flet as ft
import domains as domains
import components as dogdog
# -------------------------------------------------------------------------------------------------------
class Api_push_Data:
    data = {}
# -------------------------------------------------------------------------------------------------------
def on_boarding_tile(page: ft.Page, popup, content_page:str, change_page_callback):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    def show_error(text:str):
        page.show_dialog(ft.SnackBar(content=ft.Text(value=text), open=True, behavior=ft.SnackBarBehavior.FLOATING))
    top = ft.Row(controls=[dogdog.onboarding_top_bar()])
    focus_field = ft.TextField(
            border_color=ft.Colors.TRANSPARENT, height=0, opacity=0,
            focus_color=ft.Colors.TRANSPARENT, read_only=True
    )
    regex_email = re.compile(
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._]+[@][a-zA-Z][A-Za-z.]+[.]\w{2,}"
    )
    # ---------------------------------------------------------------------------------------------------
    # On Boarding Tile Routeing
    # ---------------------------------------------------------------------------------------------------
    if content_page == "/sign_up":
        async def sign_up_next(e):
            if storage.get("user_email") and storage.get("user_name") and storage.get("user_password"):
                if not re.fullmatch(pattern=regex_email, string=storage.get("user_email")): # type: ignore
                    show_error(text="유효한 이메일 형식이 아닙니다.")
                    return
                hash_pw = hashlib.sha256(storage.get("user_password").encode()).hexdigest() # type: ignore
                Api_push_Data.data.update({
                    "user_email": storage.get("user_email"), 
                    "user_name": storage.get("user_name"), 
                    "user_password": hash_pw
                })
                await focus_field.focus()
                page.update()
                change_page_callback("/pet_info")
            else:
                show_error(text="이메일, 닉네임, 비밀번호를 모두 입력해주세요.")
                return
        top = ft.Row(controls=[dogdog.onboarding_top_bar(case=1)])
        content = domains.sign_up_view(page=page)
        bottom = ft.Row(controls=[
            dogdog.continue_button(on_click=sign_up_next) 
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/pet_info":
        async def pet_info_next(e):
            if (storage.get("breed_text") and
                storage.get("pet_name") and
                storage.get("pet_weight")):
                if storage.get("pet_birth_day"):
                    birth = str(storage.get("pet_birth_day"))
                elif storage.get("pet_age_year") and storage.get("pet_age_month"):
                    age_month = int(storage.get("pet_age_month").split()[0]) # type: ignore
                    age_year = int(storage.get("pet_age_year").split()[0]) # type: ignore
                    birth = str(date.today() - relativedelta(months=age_month, years=age_year))
                else: 
                    show_error("생년월일을 선택해주세요.")
                    return
                try:
                    pet_weight_str = str(storage.get("pet_weight"))
                    weight_val = float(pet_weight_str)
                    if weight_val <= 0 or weight_val >= 120:
                        show_error(text="정상적인 무게를 입력해주세요.")
                        return
                    if "." in pet_weight_str and len(pet_weight_str.split(".")[1]) > 2:
                        show_error(text="무게는 소수점 두 자리까지만 입력 가능합니다.")
                        return
                except ValueError:
                    show_error(text="올바른 숫자 형식으로 무게를 입력해주세요.")
                    return
                gender = storage.get("pet_gender")
                if gender == "수컷":
                    sex = 1
                    is_neutered = False
                elif gender == "암컷":
                    sex = 2
                    is_neutered = False
                elif gender == "수컷 (중성화)":
                    sex = 1
                    is_neutered = True
                elif gender == "암컷 (중성화)":
                    sex = 2
                    is_neutered = True
                else: 
                    show_error(text="성별을 선택해주세요.")
                    return
                Api_push_Data.data.update({
                    "nickname": storage.get("pet_name"), "image_path": storage.get("image_path"),
                    "breed_id": storage.get("breed_id"), "birth": birth,
                    "sex": sex, "is_neutered": is_neutered, "weight": storage.get("pet_weight")
                })
                await focus_field.focus()
                page.update()
                change_page_callback("/pet_obesity")
            else:
                show_error(text="이름, 품종, 생년월일, 성별, 무게를 모두 입력해주세요.")
                return
        content = domains.pet_info_view(page=page, popup=popup)
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/sign_up")),
            dogdog.continue_button(on_click=pet_info_next),
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/pet_obesity":
        def pet_obesity_next(e):
            if storage.get("body_score"):
                Api_push_Data.data.update({"bcs": storage.get("body_score")})
                change_page_callback("/pet_activity")
            else:
                show_error(text="체형을 선택해주세요.")
                return
        content = domains.pet_obesity_view(page=page)
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_info")),
            dogdog.continue_button(on_click=pet_obesity_next),
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/pet_activity":
        async def pet_activity_next(e):
            meals = [storage.get("breakfast"), storage.get("lunch"), storage.get("dinner")]
            has_meals = any(meals)
            if storage.get("radio_time") and has_meals:
                feeding_count = sum(1 for meal in meals if meal)
                Api_push_Data.data.update({
                    "feeding_count": feeding_count, "daily_walks": int(storage.get("radio_time")) # type: ignore
                })
                await focus_field.focus()
                page.update()
                change_page_callback("/pet_health")
            else:
                show_error(text="급여 시간(최소 1개)과 산책 시간을 선택해주세요.")
                return
        content = domains.pet_activity_view(page=page)
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_obesity")),
            dogdog.continue_button(on_click=pet_activity_next),
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/pet_health":
        async def pet_health_next(e):
            if storage.get("allergy"): Api_push_Data.data.update({"allergy": storage.get("allergy")})
            if storage.get("disease"): Api_push_Data.data.update({"disease": storage.get("disease")})
            await focus_field.focus()
            page.update()
            change_page_callback("/pet_food")
        content = domains.pet_health_view(page=page)
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_activity")),
            dogdog.continue_button(on_click=pet_health_next),
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/pet_food":
        async def pet_food_next(e):
            if storage.get("product_id") and storage.get("food_weight"):
                if storage.get("food_weight") > storage.get("product_weight"): # type: ignore
                    show_error(text="정상적인 잔여량을 입력해주세요.")
                    return
                Api_push_Data.data.update({
                    "product_id": int(storage.get("product_id")), # type: ignore
                    "food_weight": storage.get("food_weight")})
                # ---------------------------------------------------------------------------------------
                # API Insert Point
                # ---------------------------------------------------------------------------------------
                await focus_field.focus()
                page.update()
                try:
                    await popup.show_loading_open(e)
                    storage.set("api_insert_data", Api_push_Data.data)
                    # -----------------------------------------------------------------------------------
                    # API Insert [page.session.store.get("api_insert_data")]
                    # -----------------------------------------------------------------------------------
                    change_page_callback("/sign_up_success")
                except:
                    popup.show_popup_close(e)
                    show_error(text=f"서버에 접속할 수 없습니다.\n잠시 후 다시 시도해주세요.\n{e}")
            else:
                show_error(text="현재 급여 중인 사료와 용량, 잔여량을 선택/입력해주세요.")
                return
        content = domains.pet_food_view(page=page, popup=popup)
        bottom = ft.Row(controls=[
            dogdog.arrow_back(on_click=lambda e: change_page_callback("/pet_health")),
            dogdog.continue_button(on_click=pet_food_next),
        ])
    # ---------------------------------------------------------------------------------------------------
    elif content_page == "/sign_up_success":
        basic_content = ft.Row(
            expand=True,
            controls=[
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=domains.signup_success_view(page=page)
        )])
        focus_field = None
        return basic_content, focus_field
    # ---------------------------------------------------------------------------------------------------
    # On Boarding Content and Dummy Focus Field Change
    # ---------------------------------------------------------------------------------------------------
    basic_content = [
        top,
        ft.Container(
            expand=True,
            padding=ft.Padding.only(top=20),
            content=ft.Column(
                scroll=ft.ScrollMode.HIDDEN,
                expand=True,
                spacing=10,
                controls=content if isinstance(content, list) else [content] # type: ignore
            )
        ),
        focus_field,
        bottom
    ]
    return basic_content, focus_field