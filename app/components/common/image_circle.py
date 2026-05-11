import flet as ft

def image_circle(event, size, src=None, shadow=True): # type: ignore
    if shadow:
        image_shadow = ft.BoxShadow(
            spread_radius=2,
            blur_radius=20,
            color=ft.Colors.with_opacity(1, ft.Colors.OUTLINE_VARIANT),
            offset=ft.Offset(0, -4),
        )
    else: image_shadow = None
    return ft.Container(
        width=size,
        height=size,
        shape=ft.BoxShape.CIRCLE,
        shadow=image_shadow,
        on_click=event,
        image=ft.DecorationImage(src=src, fit=ft.BoxFit.COVER),
    )
