# -------------------------------------------------------------------------------------------------------
import flet as ft
import components as dogdog
import datetime
# -------------------------------------------------------------------------------------------------------
def home_layout(page, view=None, text=None, pet_list=None, back_event=None):
    # ---------------------------------------------------------------------------------------------------
    # Default Value
    # ---------------------------------------------------------------------------------------------------
    storage = page.session.store
    if pet_list is None:
        pet_list = storage.get("pet_list")
    # ---------------------------------------------------------------------------------------------------    
    # OnBackPressedCallback
    # ---------------------------------------------------------------------------------------------------
    def handle_back(e=None):
        if len(page.views) > 1:
            page.views.pop()
            page.go(page.views[-1].route)
    # ---------------------------------------------------------------------------------------------------    
    # Dropdown Menu Select Event
    # ---------------------------------------------------------------------------------------------------
    def select_event(e):
        birth_day = None
        sex = None
        profile_image = None
        for row_id , row in pet_list.items():
            if int(row_id) == int(e.data):
                birth_day = row.get("birth_day")
                sex = row.get("sex")
                profile_image = row.get("profile_image")
        if birth_day and sex:
            pet_dropdown_list.helper_text = pet_dropdown_list_helper_text(
                birth_day=birth_day, sex=sex
            )
        left_header_image.image.src = profile_image if profile_image else "dogclay.png" # type: ignore
        left_header.update()
        storage.set("customer_pet_name", pet_dropdown_list.text)
        storage.set("customer_pet_id", pet_dropdown_list.value)
    # ---------------------------------------------------------------------------------------------------    
    # Dropdown Menu Helper Test Change Def
    # ---------------------------------------------------------------------------------------------------        
    def pet_dropdown_list_helper_text(birth_day, sex):
        if not birth_day:
            return "(생일 정보 없음)"
        
        birth_day = str(birth_day).split("T")[0]
        birth = datetime.datetime.strptime(birth_day, "%Y-%m-%d")
        now = datetime.datetime.now()
        years = now.year - birth.year
        months = now.month - birth.month
        if now.day < birth.day: months -= 1
        if months < 0:
            years -= 1
            months += 12
        sex_symbol = "♂️" if sex == "1" else "♀️"
        return f"({years}년 {months}개월, {sex_symbol})"
    # ---------------------------------------------------------------------------------------------------    
    # Page Header
    # ---------------------------------------------------------------------------------------------------
    background_height = 100
    home_background = ft.Container(
        bgcolor="#FEF3B9" if text != "개밥개밥푸드" else "#E6001A", height=background_height, 
        border_radius=ft.BorderRadius.only(bottom_left=30, bottom_right=30))
    center_header = ft.Container()
    right_header = ft.IconButton(
        icon=ft.Icons.NOTIFICATIONS_NONE, icon_color=ft.Colors.GREY_500, 
        icon_size=26, on_click=lambda _: page.go("/notification"))
    if text == "알림" or text == "알림 설정":
        right_header = ft.Container(width=26)
    elif text == "개밥개밥푸드":
        def go_shop_search(e):
            import random

            hint_texts = [
                "Tip: 브랜드로 검색해보세요!",
                "Tip: 성분으로 검색해보세요!",
                "Tip: 상품명으로 검색해보세요!",
                "Tip: 기능 키워드로 검색해보세요!",
                "Tip: 건식, 습식 같은 타입으로 검색해보세요!",
                "Tip: 퍼피, 어덜트, 시니어 같은 연령대로 검색해보세요!",
            ]

            page.session.store.set("shop_search_hint", random.choice(hint_texts))
            page.go("/shop/search")

        right_header = ft.Row(spacing=3, alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.IconButton(
                icon=ft.Icons.SEARCH, icon_color=ft.Colors.WHITE, icon_size=26, 
                on_click=go_shop_search
            ),
            ft.IconButton(
                icon=ft.Icons.NOTIFICATIONS_NONE, icon_color=ft.Colors.WHITE, icon_size=26, 
                on_click=lambda _: page.go("/notification")
            ),
            ft.IconButton(
                icon=ft.Icons.SHOPPING_CART, icon_color=ft.Colors.WHITE, icon_size=26, 
                on_click=lambda _: page.go("/shop/cart")
            )
        ])
    header_container_padding = 40
    # ---------------------------------------------------------------------------------------------------
    # Page Top Banner Edit
    # ---------------------------------------------------------------------------------------------------
    if view == "home":
        background_height = 160
        home_background.height = background_height
        
        # [방어 코드] pet_list가 유효한지 가장 먼저 체크합니다.
        if pet_list:
            first_pet_id = next(iter(pet_list.keys()))
            first_pet_birth_day = pet_list.get(first_pet_id).get("birth_day") or None # type: ignore
            first_pet_birth_sex = pet_list.get(first_pet_id).get("sex") # type: ignore
            first_pet_profile_image = (
                pet_list.get(first_pet_id).get("profile_image") # type: ignore
                if pet_list.get(first_pet_id).get("profile_image") else "dogclay.png") # type: ignore

            # 드롭다운 목록 생성
            pet_list_name = [
                ft.DropdownOption(
                    key=f"{row_id}", text=row.get("nickname"), style=dogdog.Style.DropdownOptionStyle
                ) for row_id , row in pet_list.items()
            ]
        else:
            # 강아지 정보가 아예 없을 때의 기본값 처리
            first_pet_id = "none"
            first_pet_birth_day = str(datetime.date.today())
            first_pet_birth_sex = "1"
            first_pet_profile_image = "dogclay.png"
            pet_list_name = [ft.DropdownOption(key="none", text="등록된 강아지가 없습니다.")]

        pet_dropdown_list = ft.Dropdown(
            content_padding=0,
            helper_text=pet_dropdown_list_helper_text(
                birth_day=first_pet_birth_day, sex=first_pet_birth_sex
            ),
            on_select=select_event,
            helper_style=dogdog.TextStyle(color=ft.Colors.OUTLINE, size=12),
            height=50,
            text_style=dogdog.TextStyle(),
            trailing_icon=ft.Icons.KEYBOARD_ARROW_DOWN,
            selected_trailing_icon=ft.Icons.KEYBOARD_ARROW_UP,
            value=str(first_pet_id), # 타입 일관성을 위해 str로 변환
            menu_style=ft.MenuStyle(bgcolor="#DBD19F", padding=0),
            border_width=0,
            options=pet_list_name
        )
        
        # [방어 코드] pet_list가 있을 때만 루프를 실행하여 세션에 이름 저장
        if pet_list:
            storage.set("customer_pet_id", pet_dropdown_list.value)
            for row_id , row in pet_list.items():
                # [수정 지침] 데이터 타입을 str로 일치시켜 안전하게 비교
                if str(row_id) == str(pet_dropdown_list.value):
                    storage.set("customer_pet_name", row.get("nickname"))
        
        left_header_image = dogdog.image_circle(src=first_pet_profile_image, event=None, size=80, shadow=False)
        left_header = ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.END,
            height=80, spacing=10, controls=[
                left_header_image,
                ft.Container(padding=0, width=120, height=70, content=pet_dropdown_list)])
    # ---------------------------------------------------------------------------------------------------    
    else:
        header_container_padding = 50
        left_header = ft.IconButton(
            icon=ft.Icons.ARROW_BACK_IOS_NEW, icon_color=ft.Colors.GREY_500, icon_size=26, 
            on_click=back_event if back_event else handle_back
        ) if text != "개밥개밥푸드" else ft.Container(
                                                ink=True,
                                                border_radius=8,
                                                padding=ft.padding.symmetric(horizontal=4, vertical=6),
                                                on_click=lambda _: page.go("/shop"),
                                                content=dogdog.basic_text(
                                                    value=text,
                                                    weight="bold",
                                                    size=16,
                                                    color=ft.Colors.WHITE,
                                                ),
                                            )
        center_header = dogdog.basic_text(value=text, weight="bold", size=16) # type: ignore
    # ---------------------------------------------------------------------------------------------------
    # Page Top Banner
    # ---------------------------------------------------------------------------------------------------
    top_banner = ft.Container(
        padding=ft.Padding.only(top=header_container_padding),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[left_header, center_header, right_header]
    )) if text != "개밥개밥푸드" else ft.Container(
        padding=ft.Padding.only(top=header_container_padding, left=20, right=20),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[left_header, right_header]
    ))
    # ---------------------------------------------------------------------------------------------------
    return home_background , top_banner