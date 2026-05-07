import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------

def flat_button(text, text_color=ft.Colors.GREY_600, scale=1.0, icon=None, size=14, expand=None, on_click=None, disabled=False, bgcolor=ft.Colors.GREY_100, visible=True):
    return ft.Button(
        visible=visible,
        icon=icon,
        scale=scale,
        bgcolor=bgcolor,
        content=dogdog.basic_text(value=text, color=text_color, size=size),
        expand=expand,
        on_click=on_click,
        disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREY_300,
            shape=ft.RoundedRectangleBorder(radius=5), 
            padding=ft.Padding.only(left=10, right=10)
        )
    )

def flat_over_button(text, text_color=ft.Colors.GREY_600, size=14, expand=None, on_click=None, bgcolor=ft.Colors.GREY_100, visible=True):
    return ft.Container(
        padding=ft.padding.only(top=10, bottom=10),
        alignment=ft.Alignment.CENTER,
        on_click=on_click,
        ink=True,
        bgcolor=bgcolor,
        border_radius=10,
        visible=visible,
        expand=expand,
        # width=size*2,
        # height=size*1.5,
        content=dogdog.basic_text(value=text, color=text_color, size=size)
    )

def icon_flat_button(text, icon:str, on_click=None):
    return ft.Container(
        expand=True,
        height=90,
        on_click=on_click,
        ink=True,
        border_radius=ft.border_radius.all(10),
        border=ft.Border.all(width=2, color=ft.Colors.GREY_200),
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_100, offset=ft.Offset(x=0, y=3)),
        bgcolor="#ffffff",
        content=ft.Column(
            spacing=5,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src=icon, width=40, height=40, fit=ft.BoxFit.CONTAIN),
                dogdog.basic_text(value=text, size=16, weight="bold")
            ]
        )
    )


def flat_icon_text_button(icon, value):
    return ft.Container(
        ink=True,
        border_radius=ft.border_radius.all(10),
        padding=4,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=5,
            controls=[
                ft.Icon(icon=icon, color=ft.Colors.GREY_600, size=16),
                dogdog.basic_text(value=value, color=ft.Colors.GREY_600),
            ]
        )
    )