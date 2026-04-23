import flet as ft

def radio_group(value, on_change, contents, spacing=0, layout_type=None):
    layout_content = ft.Row(controls=contents)
    if layout_type == "column": layout_content = ft.Column(spacing=spacing, controls=contents)
    return ft.RadioGroup(
        value=value,
        on_change=on_change,
        content=layout_content
    )