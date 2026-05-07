import flet as ft

from components.common.erp_view_style import (
    FIELD_BG,
    FIELD_BORDER,
    FIELD_TEXT,
    HINT_TEXT,
    BUTTON_BG,
    BUTTON_TEXT,
    BUTTON_BORDER,
    TEXT_PRIMARY,
    TEXT_ROW,
)


def build_text(
    value,
    size=12,
    color=TEXT_PRIMARY,
    weight=ft.FontWeight.W_400,
    text_align=ft.TextAlign.LEFT,
    max_lines=1,
):
    # 🔥 ERP 조회 화면 공통 Text
    return ft.Text(
        value=str(value or ""),
        size=size,
        color=color,
        weight=weight,
        text_align=text_align,
        max_lines=max_lines,
        overflow=ft.TextOverflow.CLIP,
    )


def date_value_box(text, on_click=None, width=138, align_x=-1, center_text=False, hint_when_empty=False, ink=False):
    # 🔥 ERP 조회 화면 공통 DatePicker 표시 박스
    return ft.Container(
        width=width,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        padding=ft.Padding.only(left=14, right=14),
        alignment=ft.Alignment(align_x, 0),
        ink=ink if on_click else False,
        on_click=on_click,
        content=ft.Text(
            value=text or "",
            size=13,
            color=HINT_TEXT if hint_when_empty and not text else FIELD_TEXT,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER if center_text else ft.TextAlign.LEFT,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )


def date_value_box_center(text, on_click=None):
    # 🔥 가운데 정렬 날짜 박스가 필요한 화면용
    return date_value_box(text, on_click=on_click, align_x=0, center_text=True)


def date_value_box_hint(text, on_click=None):
    # 🔥 값이 없을 때 hint 색상을 써야 하는 화면용
    return date_value_box(text, on_click=on_click, hint_when_empty=True, ink=True)


def calendar_icon_box(on_click=None):
    # 🔥 ERP 조회 화면 공통 달력 버튼
    return ft.Container(
        width=38,
        height=38,
        bgcolor=FIELD_BG,
        border=ft.Border.all(1, FIELD_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        ink=True if on_click else False,
        on_click=on_click,
        content=ft.Icon(
            ft.Icons.CALENDAR_MONTH_OUTLINED,
            size=18,
            color="#4B5563",
        ),
    )


def action_button(text, on_click=None, width=78, bgcolor=BUTTON_BG, color=BUTTON_TEXT, run_async=False):
    # 🔥 ERP 조회 화면 공통 액션 버튼
    # - 클릭 즉시 버튼 자체를 먼저 갱신해서 API 호출 전에도 반응이 보이게 한다.
    button = ft.Container(
        width=width,
        height=38,
        bgcolor=bgcolor,
        border=ft.Border.all(1, BUTTON_BORDER),
        border_radius=6,
        alignment=ft.Alignment(0, 0),
        ink=True,
        content=ft.Text(
            value=text,
            size=13,
            color=color,
            weight=ft.FontWeight.W_500,
            text_align=ft.TextAlign.CENTER,
            max_lines=1,
            overflow=ft.TextOverflow.CLIP,
        ),
    )

    def handle_click(e):
        if on_click is None or getattr(button, "_erp_clicking", False):
            return

        setattr(button, "_erp_clicking", True)
        button.opacity = 0.62
        try:
            button.update()
        except Exception:
            pass

        def finish_click():
            button.opacity = 1
            setattr(button, "_erp_clicking", False)
            try:
                button.update()
            except Exception:
                pass

        def run_handler():
            try:
                on_click(e)
            finally:
                finish_click()

        if run_async and getattr(e, "page", None) is not None:
            e.page.run_thread(run_handler)
            return

        try:
            return on_click(e)
        finally:
            finish_click()

    button.on_click = handle_click
    return button


def build_expand_table_cell(
    text,
    expand,
    align_x=0,
    weight=ft.FontWeight.W_400,
    color=TEXT_ROW,
    size=12,
    max_lines=1,
):
    # 🔥 expand 기반 테이블 셀
    return ft.Container(
        expand=expand,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=text,
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.CENTER if align_x == 0 else (ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT),
            max_lines=max_lines,
        ),
    )


def build_width_table_cell(
    text,
    width,
    align_x=0,
    weight=ft.FontWeight.W_400,
    color=TEXT_ROW,
    size=12,
    max_lines=1,
):
    # 🔥 width 기반 테이블 셀
    return ft.Container(
        width=width,
        alignment=ft.Alignment(align_x, 0),
        content=build_text(
            value=text,
            size=size,
            color=color,
            weight=weight,
            text_align=ft.TextAlign.CENTER if align_x == 0 else (ft.TextAlign.RIGHT if align_x == 1 else ft.TextAlign.LEFT),
            max_lines=max_lines,
        ),
    )
