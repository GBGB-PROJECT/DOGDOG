import flet as ft
import datetime

def picker_field(text, on_click=None, icon=None):
    font_color = ft.Colors.OUTLINE

    if type(text) == datetime.datetime: # datetime.datetime 문자열 형식
        font_color = None
        text = text.strftime(format="%Y-%m-%d") # 2026-03-31 15:00:00.000Z -> 26-03-31

    if icon: contents = [
        ft.Text(
            value=text, color=font_color, expand=True,
            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        ),
        ft.Icon(icon=icon, color=ft.Colors.OUTLINE)
    ]
    else: contents = [
        ft.Text(
            value=text, color=font_color, expand=True,
            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS
        )
    ]

    return ft.Container(
        height=48,
        border=ft.Border.all(color=ft.Colors.OUTLINE_VARIANT),
        border_radius=10,
        padding=ft.Padding.only(left=14, right=14),
        on_click=on_click,
        content=ft.Row(alignment=ft.MainAxisAlignment.SPACE_BETWEEN,controls=contents) # type: ignore
    )