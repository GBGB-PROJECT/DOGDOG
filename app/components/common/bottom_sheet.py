import flet as ft

def bottom_sheet(content:list):
    return ft.BottomSheet(
        open=False,
        draggable=True,
        # fullscreen=True,
        maintain_bottom_view_insets_padding=True,
        content=ft.Container(
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=ft.BorderRadius.only(
                top_left=20,
                top_right=20,
            ),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color=ft.Colors.with_opacity(0.2, ft.Colors.OUTLINE_VARIANT),
                offset=ft.Offset(0, -4),
            ),
            content=ft.Column(
                # expand=True,
                spacing=10,
                controls=content
            )
        )
    )