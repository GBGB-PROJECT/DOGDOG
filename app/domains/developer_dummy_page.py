import flet as ft
import components as dogdog

def dummy_view(page: ft.Page):
    message = dogdog.basic_text(
        value="이용에 불편을 드려 죄송합니다.\n더 나은 서비스를 위해 열심히 준비하고 있습니다.", 
        weight="bold", color=ft.Colors.GREY_600)
    message.text_align = ft.TextAlign.CENTER
    return ft.Container(
        padding=ft.Padding.only(left=20, right=20, top=20),
        bgcolor="#ffffff",
        alignment=ft.Alignment.CENTER,
        content=ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src="developer_image.png", scale=0.8),
                message
    ]))