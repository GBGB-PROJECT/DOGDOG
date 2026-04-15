"""frame과 연결되어 frame의 내용물을 채우는 파일"""
import flet as ft
from domain.views.home import home_view
from domain.views.inventory import inventory_view 
from domain.views.sales import sales_view 

# erp_homecontent.view,     
MENU_ITEMS = {
    "홈": home_view.erp_home_view,  
    "매출관리": inventory_view.erp_inventory_view, 
    "원가관리": lambda: ft.Container(content=ft.Text("원가관리 준비 중")),
    "구매관리": sales_view.erp_sales_view,
    "상품관리": lambda: ft.Container(content=ft.Text("상품관리 준비 중")),
    "생산관리": lambda: ft.Container(content=ft.Text("생산관리 준비 중")),
    "재고관리": lambda: ft.Container(content=ft.Text("재고관리 준비 중")),
    "물류관리": lambda: ft.Container(content=ft.Text("물류관리 준비 중")),
    "고객관리": lambda: ft.Container(content=ft.Text("고객관리 준비 중")),
    "영업관리": lambda: ft.Container(content=ft.Text("영업관리 준비 중")),
    "회계관리": lambda: ft.Container(content=ft.Text("회계관리 준비 중")),
    "인사관리": lambda: ft.Container(content=ft.Text("인사관리 준비 중")),
    "시스템관리": lambda: ft.Container(content=ft.Text("시스템관리 준비 중")),
}

"""각 side바의 제목 탭을 의미함
    1차 메뉴: 최초 클릭
    2차 메뉴: 1차 클릭 수 세부 항목을 재클릭"""

'''재고관리 메뉴 - inventory'''
# 재고관리 1차 메뉴 -> 최초 출력
INVENTORY_MAIN_ITEMS = [
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
]

# ☑️ 추가: 재고관리 관련 상태 전체 묶음
INVENTORY_ALL_ITEMS = [
    "재고관리",
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]


##  재고 관리 2차 메뉴: 상품 재고관리에 대한 세부 항목
INVENTORY_PRODUCT_ITEMS = [
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]
'''==================== 재고관리 종료 ===================='''

'''상품관리 메뉴 - sales'''
# ☑️ 추가: 상품관리 1차 메뉴
MERCHANDISE_MAIN_ITEMS = [
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# ☑️ 추가: 상품관리 전체 묶음
MERCHANDISE_ALL_ITEMS = [
    "상품관리",
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# ☑️ 추가: 생산관리 1차 메뉴
PRODUCTION_MAIN_ITEMS = [
    "생산실적",
    "생산입고",
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]

# ☑️ 추가: 생산관리 전체 묶음
PRODUCTION_ALL_ITEMS = [
    "생산관리",
    "생산실적",
    "생산입고",
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]
'''==================== 상품관리 종료 ===================='''
