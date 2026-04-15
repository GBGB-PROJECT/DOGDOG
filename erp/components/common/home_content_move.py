"""frame과 연결되어 frame의 내용물을 채우는 파일"""
import flet as ft
from domain.views.home import home_view
from domain.views.inventory import inventory_view
from domain.views.sales import sales_view

# ☑️ 추가: 재고관리 하위 화면 import
from domain.views.inventory import inventory_status_view

# erp_homecontent.view,     
MENU_ITEMS = {
    "홈": home_view.erp_home_view,
    "매출관리": inventory_view.erp_inventory_view,
    "원가관리": lambda: ft.Container(content=ft.Text("원가관리 준비 중")),
    "구매관리": sales_view.erp_sales_view,
    "상품관리": lambda: ft.Container(content=ft.Text("상품관리 준비 중")),
    "생산관리": lambda: ft.Container(content=ft.Text("생산관리 준비 중")),

    # ☑️ 수정: 임시 텍스트 → 실제 재고관리 메인 화면 연결
    "재고관리": inventory_view.erp_inventory_view,

    "물류관리": lambda: ft.Container(content=ft.Text("물류관리 준비 중")),
    "고객관리": lambda: ft.Container(content=ft.Text("고객관리 준비 중")),
    "영업관리": lambda: ft.Container(content=ft.Text("영업관리 준비 중")),
    "회계관리": lambda: ft.Container(content=ft.Text("회계관리 준비 중")),
    "인사관리": lambda: ft.Container(content=ft.Text("인사관리 준비 중")),
    "시스템관리": lambda: ft.Container(content=ft.Text("시스템관리 준비 중")),

    # ☑️ 추가: 재고관리 하위 메뉴 연결
    "재고 현황": inventory_status_view.erp_inventory_status_view,
}