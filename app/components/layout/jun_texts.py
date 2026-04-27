import flet as ft


def Txt(
    value,
    size=14,
    color=ft.Colors.BLACK,
    weight=ft.FontWeight.W_600,
    text_align=None,
    max_lines=None,
    overflow=None,
    no_wrap=None,
):
    return ft.Text(
        value=value,
        size=size,
        color=color,
        weight=weight,
        font_family="Pretendard",
        text_align=text_align,
        max_lines=max_lines,
        overflow=overflow,
        no_wrap=no_wrap,
    )


def TxtBold(
    value,
    size=14,
    color=ft.Colors.BLACK,
    text_align=None,
    max_lines=None,
    overflow=None,
    no_wrap=None,
):
    return ft.Text(
        value=value,
        size=size,
        color=color,
        weight=ft.FontWeight.W_700,
        font_family="PretendardBold",
        text_align=text_align,
        max_lines=max_lines,
        overflow=overflow,
        no_wrap=no_wrap,
    )