import flet as ft

from components.common.erp_view_style import CARD_BG, TEXT_PRIMARY


# =========================================================
# 🔥 ERP 조회 화면 공통 레이아웃
# - AUTH/HOME 영향 방지를 위해 ERP 조회 화면에서만 import해서 사용
# - 조회 화면 구조를 [필터바] → [제목/결과문구/테이블/페이지네이션] 순서로 통일
# =========================================================
def build_lookup_filter_bar(controls):
    return ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=ft.Padding.only(left=24, right=24, top=18, bottom=14),
        content=ft.Row(
            wrap=True,
            spacing=12,
            run_spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controls,
        ),
    )


def build_lookup_table_area(table_header, table_rows_holder, border=None):
    return ft.Container(
        expand=True,
        bgcolor=CARD_BG,
        border=border,
        border_radius=10,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Column(
            expand=True,
            spacing=0,
            controls=[
                table_header,
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        spacing=0,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[table_rows_holder],
                    ),
                ),
            ],
        ),
    )


def build_lookup_page_layout(
    *,
    page_title,
    result_text,
    table_area,
    pagination_holder,
    filter_controls=None,
    filter_bar=None,
    overlay_controls=None,
    title_size=22,
):
    # 🔥 ERP 조회 화면 공통 껍데기
    # - 필터바가 항상 최상단에 오도록 고정
    # - 우측 배경 얼룩 방지를 위해 최외곽/본문 배경을 흰색으로 고정
    # - 테이블과 페이지네이션은 본문 영역 안에서 동일한 순서로 배치
    filter_section = filter_bar if filter_bar is not None else build_lookup_filter_bar(filter_controls or [])

    page_content = ft.Container(
        expand=True,
        bgcolor=ft.Colors.WHITE,
        content=ft.Column(
            expand=True,
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                filter_section,
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.WHITE,
                    padding=ft.Padding.only(left=24, right=24, top=26, bottom=18),
                    content=ft.Column(
                        expand=True,
                        spacing=18,
                        controls=[
                            ft.Text(
                                value=page_title,
                                size=title_size,
                                weight=ft.FontWeight.W_700,
                                color=TEXT_PRIMARY,
                            ),
                            result_text,
                            table_area,
                            pagination_holder,
                        ],
                    ),
                ),
            ],
        ),
    )

    if overlay_controls:
        return ft.Stack(
            expand=True,
            controls=[page_content, *overlay_controls],
        )

    return page_content
