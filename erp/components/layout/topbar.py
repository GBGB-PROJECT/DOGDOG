import flet as ft
from ..common import color as c


# =========================================================
# ☑️ 상단 사용자 드롭다운 메뉴 목록
# =========================================================
TOPBAR_MENU_ITEMS = [
    "메신저",
    "개인정보 관리",
    "전자문서 관리",
    "근태관리",
    "자사제품 구매",
    "일정관리",
    "회의실 예약",
    "공지게시판",
    "커뮤니티 게시판",
    "로그아웃",
]


# =========================================================
# ☑️ 드롭다운 내부 메뉴 아이템 1개
# =========================================================
def _build_topbar_popup_item(text: str):
    return ft.PopupMenuItem(
        content=ft.Container(
            width=180,
            padding=ft.padding.only(left=12, right=12, top=10, bottom=10),
            content=ft.Text(
                value=text,
                size=14,
                weight=ft.FontWeight.W_600,
                color="#2B2F36",
            ),
        ),
        data=text,
    )


# =========================================================
# ☑️ ERP 상단바
# =========================================================
def build_erp_topbar(on_top_menu_click=None):
    # 🔥 드롭다운 메뉴 클릭 시 실행
    def _handle_top_menu_click(e: ft.ControlEvent):
        selected_menu = e.control.data

        if on_top_menu_click:
            on_top_menu_click(selected_menu)

    return ft.Container(
        height=68,
        bgcolor=c.MAIN_COLOR,
        padding=ft.padding.symmetric(horizontal=24),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.END,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.NOTIFICATIONS_NONE,
                    color=ft.Colors.WHITE,
                    size=20,
                ),
                ft.Container(width=24),

                # ☑️ 프로필 이미지
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=16,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src="leader.png",
                        fit=ft.BoxFit.COVER,
                    ),
                ),
                ft.Container(width=10),

                # ☑️ 사용자 정보
                ft.Column(
                    spacing=0,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Text(
                            value="나팀장",
                            color=ft.Colors.WHITE,
                            size=13,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            value="lmlmjang@gmail.com",
                            color=c.SUBTEXT_COLOR,
                            size=10,
                        ),
                    ],
                ),
                ft.Container(width=4),

                # 🔥 기존 Icon → PopupMenuButton 으로 변경
                ft.PopupMenuButton(
                    tooltip="사용자 메뉴",
                    icon=ft.Icons.KEYBOARD_ARROW_DOWN,
                    icon_color=ft.Colors.WHITE,
                    menu_position=ft.PopupMenuPosition.UNDER,
                    style=ft.ButtonStyle(
                        padding=0,
                        overlay_color=ft.Colors.TRANSPARENT,
                    ),
                    items=[
                        _build_topbar_popup_item(item)
                        for item in TOPBAR_MENU_ITEMS
                    ],
                    on_select=_handle_top_menu_click,
                ),
            ],
        ),
    )