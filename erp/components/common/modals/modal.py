import flet as ft
import os
import webbrowser

# 👊 수정: modals 폴더 내부 파일들을 상대경로로 import
from .field_defs import (
    PRODUCT_MASTER_FIELDS,
    PRODUCT_DETAIL_FIELDS,
    CUSTOMER_FIELDS,
    EMPLOYEE_FIELDS,
    CLIENT_FIELDS,
)
from .form_inputs import build_textfield
from .validators import validate_form, show_message


def build_form_row(page: ft.Page, field: dict, session_key: str):
    def on_change(e):
        page.session.store.set(session_key, e.control.value)   # 🔥 입력 즉시 session 저장

    tf = build_textfield(
        value=page.session.store.get(session_key) or "",
        on_change=on_change,
        field_type=field.get("type", "text"),
    )

    return ft.Row(
        controls=[
            ft.Container(
                width=130,
                alignment=ft.Alignment(-1, 0),
                content=ft.Text(
                    field["label"],
                    size=14,
                    weight=ft.FontWeight.W_600,
                ),
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
    # =========================================================
    # 👊 추가: 저장 성공 시 바깥으로 데이터 전달하는 콜백
    # =========================================================
    on_submit_success=None,
):
    title_text = ft.Text(
        register_title,
        size=18,
        weight=ft.FontWeight.W_700,
    )

    original_values = {}
    for field in fields:
        key = f"{session_prefix}_{field['key']}"
        original_values[key] = page.session.store.get(key)

    def has_saved_data():
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

    def submit(e):
        if not validate_form(page, fields, session_prefix):
            return

        # =========================================================
        # 👊 추가: 현재 입력값을 모아서 저장 성공 콜백으로 전달
        # =========================================================
        saved_data = {}
        for field in fields:
            key = f"{session_prefix}_{field['key']}"
            saved_data[field["key"]] = (page.session.store.get(key) or "").strip()

        if on_submit_success:
            on_submit_success(saved_data)

        refresh_title()
        show_message(page, "저장이 완료되었습니다.")
        close_handler(e)
        page.update()

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
        ft.Container(
            width=580,
            height=1,
            bgcolor="#D1D5DB",
        ),
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


def modal(page: ft.Page):
    page.title = "GaeBobGaeBob 시스템"
    page.padding = 30
    page.bgcolor = "#F3F4F6"

    dim_bg = ft.Container(
        visible=False,
        expand=True,
        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
    )

    popup_layer = ft.Container(
        visible=False,
        expand=True,
        alignment=ft.Alignment(0, 0),
    )

    def close_modal(e):
        dim_bg.visible = False
        popup_layer.visible = False
        popup_layer.content = None
        page.update()

    def open_master(e):
        popup_layer.content = build_modal(
            page=page,
            register_title="상품 마스터 정보 등록",
            edit_title="상품 마스터 정보 수정",
            fields=PRODUCT_MASTER_FIELDS,
            session_prefix="product_master",
            close_handler=close_modal,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        page.update()

    def open_detail(e):
        popup_layer.content = build_modal(
            page=page,
            register_title="상품 상세 정보 등록",
            edit_title="상품 상세 정보 수정",
            fields=PRODUCT_DETAIL_FIELDS,
            session_prefix="product_detail",
            close_handler=close_modal,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        page.update()

    def open_customer(e):
        popup_layer.content = build_modal(
            page=page,
            register_title="거래처 등록",
            edit_title="거래처 정보 수정",
            fields=CUSTOMER_FIELDS,
            session_prefix="customer",
            close_handler=close_modal,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        page.update()

    def open_employee(e):
        popup_layer.content = build_modal(
            page=page,
            register_title="사원 등록",
            edit_title="사원 정보 수정",
            fields=EMPLOYEE_FIELDS,
            session_prefix="employee",
            close_handler=close_modal,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        page.update()

    # =========================================================
    # ☑️ 추가: 고객 등록 / 고객 정보 수정 모달
    # =========================================================
    def open_client(e):
        popup_layer.content = build_modal(
            page=page,
            register_title="고객 등록",
            edit_title="고객 정보 수정",
            fields=CLIENT_FIELDS,
            session_prefix="client",
            close_handler=close_modal,
        )
        dim_bg.visible = True
        popup_layer.visible = True
        page.update()

    dim_bg.on_click = close_modal

    modal_view = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                ft.Text(
                    "모달 화면",
                    size=24,
                    weight=ft.FontWeight.W_700,
                ),
                ft.Container(height=20),
                ft.Button("상품 마스터 열기", on_click=open_master),
                ft.Button("상품 상세 열기", on_click=open_detail),
                ft.Button("거래처 정보 열기", on_click=open_customer),
                ft.Button("사원 정보 열기", on_click=open_employee),
                ft.Button("고객 정보 열기", on_click=open_client),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    modal_button = ft.Container(
        expand=True,
        content=ft.Stack(
            expand=True,
            controls=[
                modal_view,
                dim_bg,
                popup_layer,
            ],
        )
    )

    page.add(modal_button)


if __name__ == "__main__":
    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None

    ft.run(
        modal,
        assets_dir="assets",
        view=ft.AppView.WEB_BROWSER,
        port=34636,
    )