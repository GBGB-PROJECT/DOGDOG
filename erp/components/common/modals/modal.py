import flet as ft

from .form_inputs import build_textfield
from .validators import validate_form, show_message


def build_form_row(page: ft.Page, field: dict, session_key: str):
    def on_change(e):
        page.session.store.set(session_key, e.control.value)

    suffix_text = "kg" if field.get("key") == "spec_weight" else None
    tf = build_textfield(
        value=page.session.store.get(session_key) or "",
        on_change=on_change,
        field_type=field.get("type", "text"),
        suffix_text=suffix_text,
    )

    return ft.Row(
        controls=[
            ft.Container(
                width=130,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(field["label"], size=14, weight=ft.FontWeight.W_600),
            ),
            tf,
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )


def build_modal(
    page: ft.Page,
    register_title: str,
    edit_title: str,
    fields: list,
    session_prefix: str,
    close_handler,
    on_submit_success=None,
    mode="register",
    confirm_message=None,
):
    is_edit_mode = mode == "edit"
    title_text = ft.Text(
        edit_title if is_edit_mode else register_title,
        size=18,
        weight=ft.FontWeight.W_700,
    )

    original_values = {}
    for field in fields:
        key = f"{session_prefix}_{field['key']}"
        original_values[key] = page.session.store.get(key)

    def has_saved_data():
        if is_edit_mode:
            return True
        for field in fields:
            key = f"{session_prefix}_{field['key']}"
            if page.session.store.get(key):
                return True
        return False

    def refresh_title():
        title_text.value = edit_title if has_saved_data() else register_title

    def cancel_modal(e):
        for key, value in original_values.items():
            page.session.store.set(key, value)
        close_handler(e)

    def close_confirm(e, dialog):
        dialog.open = False
        e.page.update()

    def confirm_submit(e, dialog, callback):
        dialog.open = False
        e.page.update()
        callback()

    def submit(e):
        if not validate_form(page, fields, session_prefix):
            return

        def do_submit():
            saved_data = {}
            for field in fields:
                key = f"{session_prefix}_{field['key']}"
                saved_data[field["key"]] = (page.session.store.get(key) or "").strip()

            try:
                if on_submit_success:
                    on_submit_success(saved_data)
            except Exception as exc:
                show_message(page, f"저장 실패: {exc}")
                page.update()
                return

            refresh_title()
            show_message(page, "저장이 완료되었습니다.")
            close_handler(e)
            page.update()

        if confirm_message:
            dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("확인", size=18, weight=ft.FontWeight.W_700),
                content=ft.Text(confirm_message, size=13),
                actions=[
                    ft.TextButton("취소", on_click=lambda ce: close_confirm(ce, dialog)),
                    ft.TextButton("확인", on_click=lambda ce: confirm_submit(ce, dialog, do_submit)),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
            page.show_dialog(dialog)
            page.update()
            return

        do_submit()

    form_controls = [
        ft.Container(
            content=ft.Row(
                controls=[
                    title_text,
                    ft.IconButton(
                        icon=ft.Icons.CLOSE_SHARP,
                        icon_color=ft.Colors.GREY_700,
                        icon_size=24,
                        on_click=cancel_modal,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ),
        ft.Container(height=8),
        ft.Container(width=580, height=1, bgcolor="#D1D5DB"),
        ft.Container(height=16),
    ]

    for field in fields:
        full_key = f"{session_prefix}_{field['key']}"
        form_controls.append(build_form_row(page, field, full_key))
        form_controls.append(ft.Container(height=10))

    form_controls.append(
        ft.Row(
            alignment=ft.MainAxisAlignment.END,
            spacing=10,
            controls=[
                ft.Button("저장", on_click=submit),
                ft.Button("취소", on_click=cancel_modal),
            ],
        )
    )

    refresh_title()
    modal_height = min(page.height * 0.9, 820) if page.height else 820

    return ft.Container(
        width=700,
        height=modal_height,
        padding=24,
        bgcolor=ft.Colors.WHITE,
        border_radius=0,
        shadow=ft.BoxShadow(
            blur_radius=18,
            spread_radius=1,
            color=ft.Colors.with_opacity(0.18, ft.Colors.BLACK),
        ),
        content=ft.Column(
            controls=form_controls,
            tight=True,
            scroll=ft.ScrollMode.AUTO,
        ),
    )
