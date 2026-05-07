import flet as ft


# ============================================================
# ✅ 공통 다이얼로그 재오픈 함수
# - 기존 dialog가 열려 있으면 닫고 새 dialog를 연다
# ============================================================
def reopen_dialog(page: ft.Page, new_dialog):
    try:
        page.pop_dialog()
    except Exception:
        pass

    page.show_dialog(new_dialog)