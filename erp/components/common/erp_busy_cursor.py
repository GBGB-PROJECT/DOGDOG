import flet as ft


BUSY_CURSOR_HOST_ATTR = "_erp_busy_cursor_host"
BUSY_CURSOR_STATE_ATTR = "_erp_is_busy_cursor"


def _safe_update(control):
    try:
        control.update()
    except Exception:
        pass


def register_busy_cursor_host(page: ft.Page, host):
    """
    🔥 ERP 전체 화면의 마우스 커서를 바꿀 대상 GestureDetector를 page 객체에 저장한다.
    - Flet 0.81.0 기준 Container(mouse_cursor=...)는 쓰지 않는다.
    - GestureDetector(mouse_cursor=...) 방식만 사용한다.
    - 이 프로젝트의 page.session은 page.session.store.set/get 구조라서
      page.session.set/get을 쓰면 AttributeError가 난다.
    - 컨트롤 객체는 세션 데이터가 아니라 런타임 참조이므로 page 속성에 저장한다.
    """
    if page is None:
        return

    setattr(page, BUSY_CURSOR_HOST_ATTR, host)

    # 🔥 이미 busy 상태에서 화면이 새로 만들어진 경우 새 host에도 즉시 반영
    busy = bool(getattr(page, BUSY_CURSOR_STATE_ATTR, False))
    if host is not None:
        host.mouse_cursor = ft.MouseCursor.PROGRESS if busy else ft.MouseCursor.BASIC


def set_busy_cursor(page: ft.Page | None, busy: bool):
    """🔥 조회/API/화면 이동 중 ERP 전체 커서를 PROGRESS로 바꾼다."""
    if page is None:
        return

    next_busy = bool(busy)
    current_busy = bool(getattr(page, BUSY_CURSOR_STATE_ATTR, False))
    if current_busy == next_busy:
        return

    setattr(page, BUSY_CURSOR_STATE_ATTR, next_busy)
    host = getattr(page, BUSY_CURSOR_HOST_ATTR, None)

    if host is not None:
        host.mouse_cursor = ft.MouseCursor.PROGRESS if next_busy else ft.MouseCursor.BASIC
        _safe_update(host)


def with_busy_cursor(on_click):
    """🔥 버튼/카드 on_click 핸들러를 busy cursor 처리용으로 감싼다."""
    if on_click is None:
        return None

    def _wrapped(e):
        page = getattr(e, "page", None)
        set_busy_cursor(page, True)
        try:
            return on_click(e)
        finally:
            set_busy_cursor(page, False)

    return _wrapped


def go_with_busy_cursor(page: ft.Page | None, route: str):
    """
    🔥 page.go() 직전 커서를 PROGRESS로 바꾼다.
    - 실제 복구는 main.py의 render_route() 마지막에서 처리한다.
    """
    if page is None:
        return

    page.go(route)


def busy_cursor_control(control):
    """
    🔥 hover만으로 PROGRESS 커서가 뜨지 않게 기본 커서로 감싼다.
    - 실제 PROGRESS 커서는 with_busy_cursor()/go_with_busy_cursor() 실행 중에만 page host에 적용한다.
    - 조회/초기화 버튼 위에 마우스만 올려도 로딩처럼 보이던 문제를 막는다.
    """
    return ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.BASIC,
        content=control,
    )
