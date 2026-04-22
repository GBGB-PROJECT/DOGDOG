import sys
import os
from pathlib import Path
import webbrowser
import flet as ft

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

def main(page: ft.Page):
  page.title = "개밥개밥푸드 ERP"
  page.window_width = 1600
  page.window_height = 800
  page.padding = 0
  page.bgcolor = ft.Colors.WHITE

  # router 기준의 단일 랜더 함수(router 변경 시 화면 조립)
  def render_route(route:str|None):
    normalized_route = cm.normalize_route(route)

    # / or 빈 경로 => 로그인 화면 간주
    if normalized_route in ("/", cm.LOGIN_ROUTE):
      login_view = ErpLoginView(page, on_login_success=on_login_success)
      page.clean()
      page.add(login_view)
      return

    # 정의되지 않은 route => Home으로 보
    resolved_menu = cm.get_menu_by_route(normalized_route)
    if resolved_menu is None:
      normalized_route = cm.DEFAULT_AUTH_ROUTE

    page.clean()
    page.add(ErpFrame(page, current_route=normalized_route))

  # 로그인 성공
  def on_login_success():
    page.go(cm.DEFAULT_AUTH_ROUTE)

  # route 변경 시 재랜더하기
  def handel_render_change(e: ft.RouteChangeEvent):
    render_route(e.route)

  page.on_route_change = handel_render_change

  # 홈페이지 진입 시 => 현 라우터 기준으로 랜더링 하기
  render_route(page.route)

if __name__ == "__main__":
    if os.getenv("FLET_NO_BROWSER"):
        webbrowser.open = lambda *args, **kwargs: None

    ft.app(
        main,
        assets_dir="components/assets",
        view=ft.AppView.WEB_BROWSER,
        port=34636,
    )