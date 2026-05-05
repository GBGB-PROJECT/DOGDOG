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

    async def process_logout(self, e=None):
        """API 연동 및 세션 초기화를 포함한 로그아웃 로직"""
        import httpx

        print("🔍 [MypageController] 로그아웃 프로세스 시작")
        access_token = self.page.session.store.get("access_token")

        if access_token:
            try:
                # 1. 백엔드 로그아웃 API 호출 (200 여부 상관없이 프론트 세션은 지움)
                async with httpx.AsyncClient(timeout=5.0) as client:
                    await client.post(
                        "http://localhost:8000/api/v1/auth/logout",
                        headers={"Authorization": f"Bearer {access_token}"},
                    )
                    print("✅ [MypageController] 서버 로그아웃 처리 완료")
            except Exception as ex:
                print(f"⚠️ [MypageController] 서버 API 호출 중 예외 발생 (무시됨): {ex}")

        # 2. [핵심] 프론트엔드 세션 안전하게 삭제
        keys_to_remove = [
            "access_token",
            "refresh_token",
            "current_pet_id",
            "pet_list",
            "history",
            "customer_detail",
            "pet_food_detail",
            "is_onboarding_complete",
        ]

        for k in keys_to_remove:
            # 1. 일반 session에서 삭제 시도
            try:
                self.page.session.remove(k)
            except Exception:
                pass

            # 2. session.store에서 삭제 시도 (커스텀 스토리지인 경우 대비)
            try:
                self.page.session.store.remove(k)
            except Exception:
                pass

        # (선택) 로컬 스토리지 정보도 삭제 시도
        if hasattr(self.page, "client_storage"):
            try:
                self.page.client_storage.remove("access_token")
            except:
                pass

        print("✅ [MypageController] 로컬 세션 초기화 완료")

        # 3. 안내 스낵바 노출 및 라우팅
        snack_bar = ft.SnackBar(
            content=ft.Text(value="로그아웃 되었습니다."),
            behavior=ft.SnackBarBehavior.FLOATING,
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()

        self.page.go("/login")
