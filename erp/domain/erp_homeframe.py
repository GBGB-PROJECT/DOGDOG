import flet as ft
from components import layout as ly
from components import common as cm

# ☑️ 추가: 협업 파일 그대로 사용 (menu → view 연결용)
from components.common import home_content_move as hcm


# 1. 클래스로 정의하여 '독립적인 기계'처럼 만듭니다.
class ErpFrame(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page
        self.expand = True

        self.selected_menu = "홈"  # 🔥🔥
        
        # ☑️ 추가: 사이드바 영역을 따로 관리 (index 접근 제거)
        self.sidebar_area = ft.Container()

        # [A] 알맹이가 들어갈 빈 공간(도화지)을 미리 준비합니다.
        # 초기값으로 '홈' 화면을 띄웁니다.
        self.content_area = ft.Container(
            expand=True, 
            content=cm.MENU_ITEMS["홈"]()
        )

        # [B] 메뉴 클릭 시 알맹이를 갈아 끼우는 함수
        def on_menu_click(menu_name: str):

            # 🔥 선택된 메뉴 상태 업데이트 🔥
            self.selected_menu = menu_name

            # ☑️ 추가: sidebar를 안전하게 갱신 (index 접근 제거)
            self.sidebar_area.content = ly.build_erp_sidebar(
                selected_menu=self.selected_menu,
                on_menu_click=on_menu_click,
            )

            # ☑️ 수정: 협업 파일 기준으로 view 가져오기
            new_content = hcm.MENU_ITEMS.get(
                menu_name,
                lambda: ft.Text("화면을 찾을 수 없습니다")
            )()

            # 2. 도화지의 내용물 교체
            self.content_area.content = new_content

            # ☑️ 수정: update 위치를 맨 마지막으로 이동 (중요)
            self.update()

        # ☑️ 추가: 초기 사이드바 세팅
        self.sidebar_area.content = ly.build_erp_sidebar(
            selected_menu=self.selected_menu,
            on_menu_click=on_menu_click,
        )

        # [C] 전체 레이아웃 조립 (사이드바 + (상단바 + 도화지))
        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                # 🔥 수정: 기존 direct 호출 → sidebar_area로 교체
                self.sidebar_area,
                
                # 오른쪽 전체 영역 (상단바 + 알맹이)
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        ly.build_erp_topbar(), # 상단바
                        self.content_area      # 우리가 갈아 끼울 도화지 영역
                    ],
                ),
            ],
        )

# --- 아래는 테스트용 (나중에 main.py가 완성되면 삭제하거나 주석처리하세요) ---
# def test_main(page: ft.Page):
#     page.title = "ERP 프레임 테스트"
#     page.bgcolor = ft.colors.WHITE
#     page.padding = 0
    
#     frame = ErpFrame(page)
#     page.add(frame)

# #if __name__ == "__main__":
#     # 실행 시 경로 에러가 난다면 이전 답변의 sys.path 코드를 여기에만 잠시 넣으세요.
#     #ft.app(target=test_main)