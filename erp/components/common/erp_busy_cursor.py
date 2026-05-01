# erp/components/common/erp_busy_cursor.py

import flet as ft


# =========================================================
# 🔥 ERP 공통 Busy Cursor 유틸
# - Flet 0.81.0에서는 Container(mouse_cursor=...) 방식이 안전하지 않다.
# - 실제 마우스 커서는 GestureDetector.mouse_cursor로 제어한다.
# - 조회 / 화면 이동처럼 잠깐 멈추는 동작에서 공통으로 사용한다.
# =========================================================

_BUSY_CURSOR_ATTR = "_erp_busy_cursor_target"
_BUSY_COUNT_ATTR = "_erp_busy_cursor_count"


def _get_cursor(name: str, fallback=None):
    try:
        return getattr(ft.MouseCursor, name)
    except Exception:
        return fallback


NORMAL_CURSOR = _get_cursor("BASIC")
BUSY_CURSOR = _get_cursor("PROGRESS", _get_cursor("WAIT"))
CLICK_CURSOR = _get_cursor("CLICK", NORMAL_CURSOR)


def install_busy_cursor(page: ft.Page, cursor_target):
    """
    🔥 ErpFrame에서 전체 화면을 감싼 GestureDetector를 page에 등록한다.
    - 각 조회 버튼은 이 등록된 target의 mouse_cursor만 바꾸면 된다.
    """
    if page is None or cursor_target is None:
        return

    setattr(page, _BUSY_CURSOR_ATTR, cursor_target)

    if not hasattr(page, _BUSY_COUNT_ATTR):
        setattr(page, _BUSY_COUNT_ATTR, 0)



def set_busy_cursor(page: ft.Page, busy: bool, do_update: bool = True):
    """
    🔥 busy=True  → 커서를 PROGRESS 모양으로 변경
    🔥 busy=False → 기존 BASIC 커서로 복구

    여러 이벤트가 겹쳐도 먼저 끝난 이벤트가 커서를 섣불리 복구하지 않도록
    간단한 count 방식으로 보호한다.
    """
    if page is None:
        return

    current_count = getattr(page, _BUSY_COUNT_ATTR, 0)

    if busy:
        current_count += 1
    else:
        current_count = max(0, current_count - 1)

    setattr(page, _BUSY_COUNT_ATTR, current_count)

    cursor_target = getattr(page, _BUSY_CURSOR_ATTR, None)
    if cursor_target is None:
        return

    cursor_target.mouse_cursor = BUSY_CURSOR if current_count > 0 else NORMAL_CURSOR

    if do_update:
        try:
            cursor_target.update()
        except Exception:
            try:
                page.update()
            except Exception:
                pass



def with_busy_cursor(handler):
    """
    🔥 on_click 핸들러 감싸기
    - 조회 버튼을 누르는 즉시 커서를 PROGRESS로 바꾸고
    - API 조회/테이블 갱신이 끝나면 다시 BASIC으로 돌린다.
    """
    if handler is None:
        return None

    def _wrapped(e):
        page = getattr(e, "page", None)
        set_busy_cursor(page, True)
        try:
            return handler(e)
        finally:
            set_busy_cursor(page, False)

    return _wrapped
