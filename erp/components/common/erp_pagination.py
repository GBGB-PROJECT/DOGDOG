import math

import flet as ft


def calc_total_pages(total_count, page_size):
    # 🔥 ERP 조회 화면 공통 전체 페이지 계산
    return max(1, math.ceil((total_count or 0) / page_size))


def get_page_window(current_page, total_pages, radius=2):
    # 🔥 현재 페이지 주변 번호 생성
    start_page = max(1, current_page - radius)
    end_page = min(total_pages, current_page + radius)
    return range(start_page, end_page + 1)


def get_page_items(current_page, total_pages):
    current_page = max(1, min(current_page or 1, total_pages or 1))
    total_pages = max(1, total_pages or 1)

    if total_pages <= 5:
        return list(range(1, total_pages + 1))

    if current_page <= 3:
        return [1, 2, 3, 4, None, total_pages]

    if current_page >= total_pages - 2:
        return [1, None, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]

    return [1, None, current_page - 1, current_page, current_page + 1, None, total_pages]


def build_pagination_bar(
    current_page,
    total_pages,
    on_page_change,
    *,
    width=40,
    height=40,
    border_radius=10,
    spacing=8,
    top_padding=14,
    bottom_padding=6,
):
    if total_pages <= 1:
        return None

    def build_page_button(label, page_no=None, selected=False, disabled=False):
        text_color = ft.Colors.WHITE if selected else "#0F172A"
        if disabled:
            text_color = "#94A3B8"

        return ft.Container(
            width=width,
            height=height,
            border_radius=border_radius,
            bgcolor="#2563EB" if selected else ft.Colors.TRANSPARENT,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled or page_no is None else lambda e, p=page_no: on_page_change(p, e),
            content=ft.Text(
                value=str(label),
                size=16,
                color=text_color,
                weight=ft.FontWeight.W_700 if selected else ft.FontWeight.W_500,
                text_align=ft.TextAlign.CENTER,
            ),
        )

    def build_icon_button(icon_name, page_no, disabled=False):
        return ft.Container(
            width=width,
            height=height,
            border_radius=border_radius,
            alignment=ft.Alignment(0, 0),
            on_click=None if disabled else lambda e, p=page_no: on_page_change(p, e),
            content=ft.Icon(
                icon_name,
                size=20,
                color="#94A3B8" if disabled else "#0F172A",
            ),
        )

    controls = [
        build_icon_button(
            ft.Icons.CHEVRON_LEFT,
            current_page - 1,
            disabled=(current_page == 1),
        )
    ]

    for page_no in get_page_items(current_page, total_pages):
        if page_no is None:
            controls.append(
                ft.Container(
                    width=width,
                    height=height,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "...",
                        size=18,
                        color="#0F172A",
                        weight=ft.FontWeight.W_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
        else:
            controls.append(
                build_page_button(
                    page_no,
                    page_no,
                    selected=(page_no == current_page),
                )
            )

    controls.append(
        build_icon_button(
            ft.Icons.CHEVRON_RIGHT,
            current_page + 1,
            disabled=(current_page == total_pages),
        )
    )

    return ft.Container(
        padding=ft.Padding.only(top=top_padding, bottom=bottom_padding),
        alignment=ft.Alignment(0, 0),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=spacing,
            controls=controls,
        ),
    )
