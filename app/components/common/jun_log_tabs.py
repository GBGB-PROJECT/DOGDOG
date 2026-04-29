import flet as ft
from components.layout.jun_texts import Txt
from components.common.jun_ui_boxes import white_long_box3
from components.common.jun_layout_tokens import WIDE_CONTENT_WIDTH, SECTION_GAP
from components.common.jun_colors import (
    TEXT_PRIMARY,
    SURFACE_WHITE,
)


# ✅ 로그 화면 공통 상단 탭 라벨
LOG_TAB_LABELS = ["전체", "급여량", "음수량", "활동량"]


# ✅ 공통 상단 탭 UI
# - selected_index: 현재 선택된 탭 index
# - on_tab_change: 탭 클릭 시 실행할 함수
def build_log_top_tabs(selected_index, on_tab_change):
    tab_controls = []

    for i, label in enumerate(LOG_TAB_LABELS):
        is_selected = selected_index == i

        tab_controls.append(
            ft.Container(
                expand=True,
                height=50,
                on_click=lambda e, idx=i: on_tab_change(idx),
                content=ft.Column(
                    spacing=6,
                    alignment=ft.MainAxisAlignment.END,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        Txt(
                            label,
                            size=16,
                            color=TEXT_PRIMARY if is_selected else ft.Colors.GREY,
                            weight=ft.FontWeight.W_700 if is_selected else ft.FontWeight.W_500,
                        ),
                        ft.Container(
                            height=3,
                            width=60,
                            bgcolor=TEXT_PRIMARY if is_selected else ft.Colors.TRANSPARENT,
                            border_radius=10,
                        ),
                    ],
                ),
            )
        )

    return ft.Container(
        width=WIDE_CONTENT_WIDTH,
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=tab_controls,
        ),
    )


# ✅ 공통 선택형 로그 박스
# - 선택된 item이면 회색 배경
def build_selectable_log_box(item_key, text, time_text, selected_key, on_select):
    return white_long_box3(
        text,
        time_text,
        bgcolor=ft.Colors.GREY_200 if selected_key == item_key else SURFACE_WHITE,
        on_click=lambda e, key=item_key: on_select(key),
    )


# ✅ 선택 상태 반영
def update_selected_log_item(item_key, selected_item, item_controls, tab_content):
    selected_item["key"] = item_key

    for key, control in item_controls.items():
        control.bgcolor = (
            ft.Colors.GREY_200 if key == selected_item["key"] else SURFACE_WHITE
        )

    tab_content.update()


# ✅ 선택형 로그 박스 생성
def make_selectable_log_box(
    item_key,
    text,
    time_text,
    selected_item,
    item_controls,
    tab_content,
):
    box = build_selectable_log_box(
        item_key=item_key,
        text=text,
        time_text=time_text,
        selected_key=selected_item["key"],
        on_select=lambda key: update_selected_log_item(
            key,
            selected_item,
            item_controls,
            tab_content,
        ),
    )
    item_controls[item_key] = box
    return box


# ✅ 탭 내용 컬럼 생성
def build_log_tab_content(items, selected_item, item_controls, tab_content):
    return ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=SECTION_GAP,
        controls=[
            make_selectable_log_box(
                item_key,
                text,
                time_text,
                selected_item,
                item_controls,
                tab_content,
            )
            for item_key, text, time_text in items
        ],
    )


# ✅ 탭 변경 공통 처리
def apply_log_tab_change(
    index,
    selected_top_tab,
    selected_item,
    item_controls,
    tab_content,
    top_tabs_area,
    tab_data_map,
    page,
):
    selected_top_tab["index"] = index
    item_controls.clear()
    selected_item["key"] = None

    tab_content.content = build_log_tab_content(
        tab_data_map.get(index, []),
        selected_item,
        item_controls,
        tab_content,
    )

    top_tabs_area.content = build_log_top_tabs(
        selected_index=selected_top_tab["index"],
        on_tab_change=lambda idx: apply_log_tab_change(
            idx,
            selected_top_tab,
            selected_item,
            item_controls,
            tab_content,
            top_tabs_area,
            tab_data_map,
            page,
        ),
    )

    page.update()