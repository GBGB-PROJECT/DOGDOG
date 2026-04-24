import flet as ft

def basic_text(value:str="", spans=None, size=None, weight=None, color=ft.Colors.BLACK):
    if weight == "bold": weight = ft.FontWeight.BOLD
    return ft.Text(
        spans=spans,
        value=value,
        size=size, 
        weight=weight, 
        color=color, 
        font_family="Pretendard"
    )