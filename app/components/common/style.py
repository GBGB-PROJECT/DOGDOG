import flet as ft

class Style:
    TextStyle = (
        ft.TextStyle(
            size=14, weight=ft.FontWeight("w600"), font_family="Pretendard", overflow=ft.TextOverflow.ELLIPSIS
        )
    )
    
    DropdownOptionStyle = ft.ButtonStyle(bgcolor="#FBEEAC", text_style=TextStyle)

def TextStyle(size=14, weight="w600", color=ft.Colors.BLACK):
    return ft.TextStyle(height=-1,
        size=size, weight=ft.FontWeight(value=weight), font_family="Pretendard", overflow=ft.TextOverflow.ELLIPSIS, color=color
    )