import flet as ft

def basic_text(value:str="", spans=None, size=14, weight=None, color=ft.Colors.BLACK, expand=None):
    if weight == "bold": weight = ft.FontWeight.BOLD
    return ft.Text(
        spans=spans,
        expand=expand,
        value=value,
        size=size, 
        weight=weight, 
        color=color, 
        font_family="Pretendard"
    )