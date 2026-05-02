import flet as ft


class MypageController:
    """
    마이페이지(/mypage)의 비즈니스 로직과 라우팅을 담당하는 컨트롤러
    """

    def __init__(self, page: ft.Page):
        self.page = page

    def go_to_feeding(self):
        """
        '급여 중인 제품 보러가기' 클릭 시 실행
        필요한 사전 작업이 있다면 여기서 처리 후 화면 이동
        """
        # 실제 등록해두신 급여 중인 제품 페이지 라우트 주소로 맞춰주세요 (예: /feeding 또는 /feeding_info)
        self.page.go("/feeding")

    def logout(self):
        """추후 구현할 로그아웃 로직"""
        pass
