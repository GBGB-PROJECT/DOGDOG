import flet as ft
from erp.components import layout as lay


# 2. 메인 함수 안으로 모든 UI 로직 이동 (안전성 확보)
def erp_main(page: ft.Page):
    page.title = "ERP"
    page.bgcolor = ft.Colors.WHITE # ft.Colors가 아닌 ft.colors 소문자 사용
    
    # 1. 콘텐츠 영역 선언
    content_area = ft.Container(expand=True, content=erp_common.MENU_ITEMS["홈"]())

    # 2. 메뉴 클릭 핸들러
    def on_menu_click(menu_name: str):
        # 문제점 2, 3 수정: 파라미터 사용 및 .content 속성 변경
        content_area.content = erp_common.MENU_ITEMS.get(menu_name, lambda: ft.Text(f"오류 화면 없음"))()

    # 3. 레이아웃 구성
    erp_home_view = ft.Row(
        expand=True,
        spacing=0,
        controls=[
            erp_layout.build_erp_sidebar(selected_menu="Home", on_menu_click=on_menu_click),
            ft.Column(
                expand=True,

                spacing=0,
                # 문제점 1 수정: topbar 아래에 content_area 배치
                controls=[erp_layout.build_erp_topbar(), content_area],
            ),
        ],
    )

    page.add(erp_home_view)

## 확인 목적이며 최종적으로는 main에서 연결되어야 한다.
ft.app(target=erp_main)