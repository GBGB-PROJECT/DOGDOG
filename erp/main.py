import sys
import os
from pathlib import Path
import webbrowser
import flet as ft
from datetime import datetime
from components.common.task_controls import task_controls , views_controls

# =========================================================
# ☑️ 팀 공통 backend/db 패키지 import 경로 설정
# - erp/main.py를 직접 실행해도 DOGDOG/backend, DOGDOG/db를 찾을 수 있게 처리
# =========================================================
ERP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ERP_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# 홈페이지 프레임 연결
from domain.erp_homeframe import ErpFrame
# 홈페이지 erp 연결
from domain.views.auth.erp_login import ErpLoginView
# 라우터 인식을 위해서 content_move를 연결
from components.common import content_move as cm
from components.common.erp_busy_cursor import set_busy_cursor


def main(page: ft.Page):
    page.title = "개밥개밥푸드 ERP"
    # page.width = 1600
    # page.height = 800
    page.padding = 0
    page.bgcolor = ft.Colors.WHITE
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android="None",  # type: ignore
            ios="None",  # type: ignore
            macos="None",  # type: ignore
            linux="None",  # type: ignore
            windows="None",  # type: ignore
        ),
    )

    # 🔥 화면 전환 속도 개선
    # - 건형님이 바꾼 ft.View 라우팅 구조는 유지한다.
    # - 단, 메뉴 이동마다 ErpFrame/sidebar/topbar를 새로 만들지 않도록 한 번 만든 프레임을 재사용한다.
    erp_frame_holder = {"frame": None}
    erp_view_holder = {"view": None}

    def move_route(target_route: str):
        """
        🔥 로그인 이동 안정화
        - 현재 프로젝트에서는 page.go()로 정상 라우팅이 검증되어 있다.
        - push_route()는 버전에 따라 on_route_change가 기대대로 돌지 않아
        - 로그인 성공 후 화면이 멈춘 것처럼 보일 수 있으므로 여기서는 page.go()를 유지한다.
        """
        page.go(target_route)

    # router 기준의 단일 랜더 함수(router 변경 시 화면 조립)
    def render_route(route: str | None):
        print('전환 시작 >> ', datetime.now())
        normalized_route = cm.normalize_route(route)

        # / or 빈 경로 => 로그인 화면 간주
        if normalized_route in ("/", cm.LOGIN_ROUTE):
            # 🔥 로그인 화면으로 돌아오면 이전 ERP 프레임 참조 제거
            erp_frame_holder["frame"] = None
            erp_view_holder["view"] = None

            login_view = ErpLoginView(page, on_login_success=on_login_success)
            # ft.View 객체로 감싸서 views 배열에 추가
            page.views.clear()
            page.views.append(ft.View(route=normalized_route, controls=[login_view], padding=0))
            page.update()
        else:
            # 정의되지 않은 route => Home으로 보정
            resolved_menu = cm.get_menu_by_route(normalized_route)
            if resolved_menu is None:
                normalized_route = cm.DEFAULT_AUTH_ROUTE

            # 🔥 화면 전환 속도 개선
            # - 최초 진입 때만 ErpFrame을 생성한다.
            # - 이후 route 변경은 ErpFrame.set_route()로 우측 본문과 사이드바 선택 상태만 교체한다.
            frame = erp_frame_holder["frame"]
            current_view = page.views[-1] if page.views else None
            is_erp_view_mounted = (
                frame is not None
                and current_view is erp_view_holder["view"]
                and frame in current_view.controls
            )

            if frame is None:
                frame = ErpFrame(page, current_route=normalized_route)
                erp_frame_holder["frame"] = frame
                erp_view_holder["view"] = ft.View(
                    padding=0,
                    route=normalized_route,
                    controls=[frame],
                )
                page.views.clear()
                page.views.append(erp_view_holder["view"])
                page.update()
            elif is_erp_view_mounted:
                current_view.route = normalized_route
                frame.set_route(normalized_route, update=True)
            else:
                frame.set_route(normalized_route)
                erp_view_holder["view"] = ft.View(
                    padding=0,
                    route=normalized_route,
                    controls=[frame],
                )
                page.views.clear()
                page.views.append(erp_view_holder["view"])
                page.update()

        # 🔥 route 렌더링이 끝나면 화면 이동용 progress cursor 복구
        set_busy_cursor(page, False)
        task_controls()
        views_controls(page)
        print('전환 종료 >> ', datetime.now())

    # 로그인 성공
    def on_login_success():
        move_route(cm.DEFAULT_AUTH_ROUTE)

    # route 변경 시 재렌더하기
    def handle_route_change(e: ft.RouteChangeEvent):
        render_route(e.route)

    page.on_route_change = handle_route_change

    # 홈페이지 진입 시 => 현 라우터 기준으로 렌더링 하기
    render_route(page.route)


if __name__ == "__main__":
    import logging, warnings

    level = logging.INFO
    logging.basicConfig(level=level)
    warnings.filterwarnings(action="ignore")
    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None

    ft.app(
        main,
        assets_dir="components/assets",
        view=ft.AppView.WEB_BROWSER,
        web_renderer=ft.WebRenderer.CANVAS_KIT,
        port=34636,
    )
