import flet as ft

class JunSnackBarUtils:
    """
    DOGDOG 프로젝트 표준 스낵바 유틸리티
    미니멀리즘 디자인 및 FLOATING 동작을 통일하여 사용합니다.
    """

    @staticmethod
    def _show_unified_snackbar(page: ft.Page, message: str, duration: int = 3000):
        """모든 스낵바의 뼈대가 되는 공통 렌더링 로직"""
        snack_bar = ft.SnackBar(
            content=ft.Text(message),
            behavior=ft.SnackBarBehavior.FLOATING,  # 하단 메뉴를 가리지 않음 (핵심)
            duration=duration,
        )
        page.overlay.append(snack_bar)
        snack_bar.open = True
        page.update()

    @staticmethod
    def show_success(page: ft.Page, message: str):
        """✅ 성공 메시지 (기본 테마 + FLOATING)"""
        JunSnackBarUtils._show_unified_snackbar(page, f"✅ {message}")

    @staticmethod
    def show_error(page: ft.Page, message: str):
        """🚨 에러 메시지 (기본 테마 + FLOATING)"""
        JunSnackBarUtils._show_unified_snackbar(page, f"🚨 {message}", duration=4000)

    @staticmethod
    def show_warning(page: ft.Page, message: str):
        """⚠️ 경고/안내 메시지 (기본 테마 + FLOATING)"""
        JunSnackBarUtils._show_unified_snackbar(page, f"⚠️ {message}")

    @staticmethod
    def show_not_implemented(page: ft.Page):
        """기능 구현 중 안내 메시지"""
        JunSnackBarUtils._show_unified_snackbar(page, "🛠️ 기능 구현중입니다.", duration=2000)