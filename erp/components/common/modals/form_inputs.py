import flet as ft


def build_input_filter(field_type: str):
    if field_type == "int":
        return ft.InputFilter(
            regex_string=r"^[0-9]*$",
            replacement_string="",
        )

    if field_type == "float":
        return ft.InputFilter(
            regex_string=r"^[0-9.]*$",
            replacement_string="",
        )

    if field_type == "url":
        return ft.InputFilter(
            regex_string=r"^[a-zA-Z0-9:/?&=._\-#%+]*$",
            replacement_string="",
        )

    if field_type == "name":
        return ft.InputFilter(
            regex_string=r"^[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z\s]*$",
            replacement_string="",
        )

    if field_type == "email":
        return ft.InputFilter(
            regex_string=r"^[a-zA-Z0-9@._\-+]*$",
            replacement_string="",
        )

    if field_type == "phone":
        return ft.InputFilter(
            regex_string=r"^[0-9\-() ]*$",
            replacement_string="",
        )

    if field_type in ["bizno", "postal"]:
        return ft.InputFilter(
            regex_string=r"^[0-9\-]*$",
            replacement_string="",
        )

    if field_type == "date":
        return ft.InputFilter(
            regex_string=r"^[0-9\-]*$",
            replacement_string="",
        )

    return ft.InputFilter(
        regex_string=r"^[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z0-9\s_\-().,:/%]*$",
        replacement_string="",
    )


def build_textfield(
    value=None,
    on_change=None,
    field_type="text",
):
    return ft.TextField(
        width=420,
        height=40,
        value=value or "",
        on_change=on_change,
        text_size=14,
        border=ft.InputBorder.OUTLINE,
        border_color=ft.Colors.OUTLINE_VARIANT,
        border_radius=0,
        input_filter=build_input_filter(field_type),
        content_padding=ft.Padding.only(left=14, right=14),
        hint_text="YYYY-MM-DD" if field_type == "date" else None,
    )