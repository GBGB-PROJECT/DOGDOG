import flet as ft
import components as dogdog

def continue_button(value="Continue", bgcolor="#FEF3B9", text_color=ft.Colors.BLACK, on_click=None):
    return ft.Container(
        expand=9,
        height=50,
        ink=True,
        on_click=on_click,
        bgcolor=bgcolor,
        border_radius=10,
        alignment=ft.Alignment.CENTER,
        content=dogdog.basic_text(
            value=value,
            weight="bold",
            color=text_color
        )
    )

def arrow_back(on_click=None):
    return ft.Container(
        expand=1,
        on_click=on_click,
        content=ft.Icon(
            icon=ft.Icons.ARROW_BACK_IOS,
            size=22,
        ),
    )

def bottom_appbar(appbar_button_list:list):
    return ft.BottomAppBar(
        padding=0,
        height=80,
        bgcolor="#FFFFFF",
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                ft.Divider(height=1),
                ft.Row(controls=appbar_button_list, expand=True, spacing=0)
    ]))

def home_bottom_appbar(appbar_status, page_name):
    def appbar_button(icon, text, on_click):
        if f"/{text.lower()}" == page_name if type(text) == str else None:
            button_color = ft.Colors.BLACK
        else: button_color = ft.Colors.GREY_400
        if type(icon) == type("str"):
            if icon == "skeleton.png":
                bone_img = "shop.png" if page_name.startswith("/shop") else "skeleton.png"
            else:
                bone_img = icon
        
            return ft.Container(
                width=80,
                height=80,
                shape=ft.BoxShape.CIRCLE,
                offset=ft.Offset(0, -0.3),
                on_click=on_click,
                image=ft.DecorationImage(src=bone_img, fit=ft.BoxFit.COVER),
            )
        return ft.Container(
            padding=0,
            expand=True,
            ink=True,
            on_click=on_click,
            content=ft.Column(
                expand=True,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Icon(icon=icon, color=button_color, size=22),
                    dogdog.basic_text(value=text, size=12, color=button_color),
                ],
            ),
        )

    appbar_button_list = [appbar_button(
        icon=icon, text=text, on_click=on_click) for icon, text, on_click in appbar_status]
    
    return bottom_appbar(appbar_button_list=appbar_button_list)