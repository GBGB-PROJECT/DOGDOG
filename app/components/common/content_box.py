import flet as ft

def content_container(content_list, on_click=None):
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=10, bottom=10),
        on_click=on_click,
        ink=True,
        border_radius=ft.border_radius.all(10),
        border=ft.Border.all(width=2, color=ft.Colors.GREY_200),
        shadow=ft.BoxShadow(blur_radius=2, color=ft.Colors.GREY_100, offset=ft.Offset(x=0, y=3)),
        bgcolor="#ffffff",
        content=ft.Column(
            controls=content_list
        )
    )