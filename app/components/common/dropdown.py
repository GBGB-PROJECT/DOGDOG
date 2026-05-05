import flet as ft

def dropdown_menu(
        label, 
        event, 
        options,
        expand=True,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.OUTLINE_VARIANT,
    ):
    return ft.Dropdown(
        hint_text=label,
        expand=expand,
        text_size=14, ## ft.Text Default Size
        border=border,
        border_color=border_color,
        border_radius=10,
        hint_style=ft.TextStyle(color=ft.Colors.OUTLINE),
        bgcolor=ft.Colors.WHITE,
        on_select=event,
        options=options,
        value=options[0].key,
    )

def dropdown_menu_option(text:str, icon=None, icon_color=None, key=None):
    return ft.dropdown.Option(
        key=key,
        text=text,
        trailing_icon=ft.Icon(icon=icon, color=icon_color, size=30), # type: ignore
    )