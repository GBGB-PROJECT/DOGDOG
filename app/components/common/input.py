import flet as ft
import components as dogdog

def input_textfield(value=None,
    max_length=10, label=None, hint_text=None, suffix=None, input_type=None, on_change=None, password=None,
    text_filter=ft.InputFilter(regex_string=r"^[ㄱ-ㅎ|ㅏ-ㅣ|가-힣-a-zA-Zㆍ]*$", replacement_string=""),
    cancel_event=False
):
    if input_type == "int":
        text_filter = ft.InputFilter(regex_string=r"^[0-9]*$", replacement_string="")
        max_length = 6
    elif input_type == "float":
        text_filter = ft.InputFilter(regex_string=r"^[0-9.]*$", replacement_string="")
        max_length = 6
    elif input_type == "phone":
        text_filter = ft.InputFilter(regex_string=r"^[0-9\-]*$", replacement_string="")
        max_length = 13
    elif input_type == "password":
        text_filter = ft.InputFilter(
            regex_string=r"^[a-zA-Z0-9.~\!\@\#\$\%\^\&\*\_\-\=\+]*$", replacement_string="")
        max_length = 20
        password = True
    elif input_type == "email":
        text_filter = ft.InputFilter(regex_string=r"[a-zA-Z0-9@._\-\+]*", replacement_string="")
    text_field = ft.TextField(
        width=float('inf'),
        label=label,
        expand=True,
        password=password, # type: ignore
        can_reveal_password=password, # type: ignore
        hint_text=hint_text,
        on_change=on_change,
        text_size=14, # ft.Text Default Size
        suffix=suffix,
        hint_style=ft.TextStyle(color=ft.Colors.OUTLINE),
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.OUTLINE_VARIANT,
        border_radius=10,
        content_padding=ft.Padding.only(left=14, right=14),
        max_length=max_length,
        input_filter=text_filter,
        counter=ft.Container(),
        value=value
    )
    if cancel_event:
        # field.controls[0].controls[0].value = ""
        def field_clear(e, field):
            field.value = ""
            field.update()
        text_field.border_color = ft.Colors.TRANSPARENT
        text_field.content_padding = 0
        text_field.margin = ft.margin.only(top=-10, bottom=-10)
        return ft.Column(spacing=0, margin=ft.margin.only(top=-10), controls=[
            ft.Row(expand=True, vertical_alignment=ft.CrossAxisAlignment.CENTER, controls=[
                text_field,
                ft.IconButton(
                    icon=ft.Icons.CANCEL, icon_color=ft.Colors.GREY_400, 
                    icon_size=20, on_click=lambda e:field_clear(e, text_field))
            ]),
            ft.Divider(height=1)
        ])
    return text_field

def list_input_textfield(hint_text=None, suffix=None, input_type=None, on_change=None):
    text_filter = ft.InputFilter(regex_string=r"^[ㄱ-ㅎ|ㅏ-ㅣ|가-힣-a-zA-Zㆍ]*$")
    if input_type == "int": text_filter = ft.InputFilter(regex_string=r"^[0-9-.]*$", replacement_string="")
    return ft.TextField(
        width=float('inf'),
        hint_text=hint_text,
        on_change=on_change,
        text_size=14, # ft.Text Default Size
        suffix=suffix,
        hint_style=ft.TextStyle(color=ft.Colors.OUTLINE),
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.OUTLINE_VARIANT,
        border_radius=10,
        content_padding=ft.Padding.only(left=14, right=14),
        input_filter=text_filter
    )