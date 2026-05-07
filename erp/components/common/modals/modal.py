import flet as ft

from .validators import show_message, validate_field_value


def _field_key(session_prefix: str, field: dict):
    return f"{session_prefix}_{field['key']}"


def _is_empty_required(field: dict, value: str):
    return field.get("required", False) and not (value or "").strip()


def build_form_row(field: dict, control: ft.TextField):
    return ft.Row(
        controls=[
            ft.Container(
                width=130,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(field["label"], size=14, weight=ft.FontWeight.W_600),
            ),
            control,
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
    initial_values=None,
):
    is_edit_mode = mode == "edit"
    field_controls = {}

    title_text = ft.Text(
        edit_title if is_edit_mode else register_title,
        size=18,
        weight=ft.FontWeight.W_700,
    )
    error_text = ft.Text("", size=13, color="#DC2626", visible=False)
    confirm_panel = ft.Container(visible=False)
    pending_data = {"value": None}

    def initial_value_for(field):
        if initial_values is not None:
            return initial_values.get(field["key"], "") or ""
        return page.session.store.get(_field_key(session_prefix, field)) or ""

    def current_value(field):
        control = field_controls[field["key"]]
        return (control.value or "").strip()

    def show_inline_error(message: str):
        error_text.value = message
        error_text.visible = True
        confirm_panel.visible = False
        try:
            error_text.update()
            confirm_panel.update()
        except Exception:
            page.update()

    def clear_inline_error():
        error_text.value = ""
        error_text.visible = False

    def validate_local_form():
        values = {}
        for field in fields:
            value = current_value(field)
            values[field["key"]] = value
            if _is_empty_required(field, value):
                show_inline_error(f"{field['label']}을(를) 입력해주세요.")
                return None

        for field in fields:
            error = validate_field_value(field, values[field["key"]])
            if error:
                show_inline_error(error)
                return None

        clear_inline_error()
        return values

    def cancel_modal(e):
        close_handler(e)

    def close_confirm(e):
        pending_data["value"] = None
        confirm_panel.visible = False
        confirm_panel.update()

    def do_submit(e, saved_data):
        def worker():
            try:
                if on_submit_success:
                    on_submit_success(saved_data)
            except Exception as exc:
                show_inline_error(f"저장 실패: {exc}")
                return

            show_message(page, "저장이 완료되었습니다.")
            close_handler(e)

        if getattr(e, "page", None) is not None:
            e.page.run_thread(worker)
            return
        worker()

    def confirm_submit(e):
        saved_data = pending_data["value"]
        pending_data["value"] = None
        confirm_panel.visible = False
        confirm_panel.update()
        if saved_data is not None:
            do_submit(e, saved_data)

    def submit(e):
        saved_data = validate_local_form()
        if saved_data is None:
            return

        if confirm_message:
            pending_data["value"] = saved_data
            confirm_panel.visible = True
            confirm_panel.update()
            return

        do_submit(e, saved_data)

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
        control = ft.TextField(
            width=420,
            height=40,
            value=initial_value_for(field),
            on_change=None,
            text_size=14,
            border=ft.InputBorder.OUTLINE,
            border_color=ft.Colors.OUTLINE_VARIANT,
            border_radius=0,
            content_padding=ft.Padding.only(left=14, right=14),
            hint_text="YYYY-MM-DD" if field.get("type") == "date" else None,
            suffix="kg" if field.get("key") == "spec_weight" else None,
        )
        field_controls[field["key"]] = control
        form_controls.append(build_form_row(field, control))
        form_controls.append(ft.Container(height=10))

    confirm_panel.padding = 16
    confirm_panel.bgcolor = "#F8FAFC"
    confirm_panel.border = ft.Border.all(1, "#CBD5E1")
    confirm_panel.border_radius = 8
    confirm_panel.content = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("확인", size=15, weight=ft.FontWeight.W_700),
            ft.Text(confirm_message or "", size=13, color="#334155"),
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=8,
                controls=[
                    ft.TextButton("취소", on_click=close_confirm),
                    ft.TextButton("확인", on_click=confirm_submit),
                ],
            ),
        ],
    )

    form_controls.extend(
        [
            error_text,
            ft.Container(height=6),
            confirm_panel,
            ft.Container(height=10),
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                spacing=10,
                controls=[
                    ft.Button("저장", on_click=submit),
                    ft.Button("취소", on_click=cancel_modal),
                ],
            ),
        ]
    )

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
