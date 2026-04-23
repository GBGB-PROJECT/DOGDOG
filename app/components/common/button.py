import flet as ft
import components as dogdog
# -------------------------------------------------------------------------------------------------------

def flat_button(text, scale=0.8, icon=None, size=None, expand=None, on_click=None, disabled=True, bgcolor=ft.Colors.GREY_100):
    return ft.Button(
        icon=icon,
        width=size,
        height=size,
        scale=scale,
        bgcolor=bgcolor,
        content=dogdog.basic_text(value=text, color=ft.Colors.GREY_600),
        expand=expand,
        on_click=on_click,
        disabled=disabled,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.GREY_300,
            shape=ft.RoundedRectangleBorder(radius=5), 
            padding=ft.Padding.only(left=10, right=10)
        )
    )

def icon_flat_button(text, icon, on_click=None):
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