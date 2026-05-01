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
def _build_topbar_popup_item(text: str, on_click_handler):
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
        on_click=on_click_handler,
    )


# =========================================================
# ☑️ ERP 상단바
# =========================================================
def build_erp_topbar(page: ft.Page, on_top_menu_click=None):
    ## 세션 불러오기 erp_login에서 가져온 것(확인 완료)
    client_name = page.session.store.get("emp_name") or "로그인 실패"
    client_pos = page.session.store.get("emp_pos") or "직위 불러오기 오류"
    client_email = page.session.store.get("emp_email") or "email@example.com"
    
    # 🔥 드롭다운 메뉴 클릭 시 실행
    def _handle_top_menu_click(e: ft.ControlEvent):
        selected_menu = e.control.data

        if selected_menu == "로그아웃":
                print("✅ 로그아웃 클릭 이벤트 발생")  # 터미널에서 클릭 작동 여부 디버깅용
                page.session.store.clear()        # 1. 세션 초기화
                page.views.clear()            # 2. 현재 화면의 모든 위젯(ErpFrame 등) 강제 삭제
                page.go("/login")                # 3. 로그인 라우트로 이동 (main.py의 라우팅 트리거)                   # 4. 화면 즉시 새로고침
                return

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
                            value=f"{client_name} ({client_pos})",
                            color=ft.Colors.WHITE,
                            size=13,
                            weight=ft.FontWeight.W_700,
                        ),
                        ft.Text(
                            value=client_email,
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
                        _build_topbar_popup_item(item, _handle_top_menu_click)
                        for item in TOPBAR_MENU_ITEMS
                    ],
                    #on_select=_handle_top_menu_click,
                ),
            ],
        ),
    )