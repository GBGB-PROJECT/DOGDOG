"""frame과 연결되어 frame의 내용물을 채우는 파일"""
import flet as ft
from domain.views.home import home_view
from domain.views.inventory import inventory_view 
from domain.views.sales import sales_view 

from domain.views.inventory import inventory_status_view
from domain.views.inventory import inventory_product_detail_view

# 👊 추가: 상품관리 화면 연결
from domain.views.merchandise import merchandise_view
from domain.views.merchandise import merchandise_master_view
from domain.views.merchandise import merchandise_info_detail_view




## ============= 페이지 이동 (실질)

# 👊 추가: 왼쪽 메인 사이드바에만 보여줄 1차 메뉴 목록
ERP_MAIN_MENU_ITEMS = [
    "홈",
    "매출관리",
    "원가관리",
    "구매관리",
    "상품관리",
    "생산관리",
    "재고관리",
    "물류관리",
    "고객관리",
    "영업관리",
    "회계관리",
    "인사관리",
    "시스템관리",
]

# erp_homecontent.view,     
MENU_ITEMS = {
    "홈": home_view.erp_home_view,
    "매출관리": inventory_view.erp_inventory_view,
    "원가관리": lambda: ft.Container(content=ft.Text("원가관리 준비 중")),
    "구매관리": sales_view.erp_sales_view,
    "상품관리": lambda: ft.Container(content=ft.Text("상품관리 준비 중")),

    # 👊 수정: 임시 텍스트 → 실제 상품관리 메인 화면 연결
    "상품관리": merchandise_view.erp_merchandise_view,

    # 👊 추가: 상품관리 하위 메뉴 연결
    "상품마스터정보관리": merchandise_master_view.erp_merchandise_master_view,

    "상품 상세 정보 관리": merchandise_info_detail_view.erp_merchandise_info_detail_view,

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

    "상품별 재고 상세": inventory_product_detail_view.erp_inventory_product_detail_view,
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

## =============== 라우트 연결목적
### 라우트 연결을 위한 더미
MENU_TO_ROUTE = {
    "홈": "/home",
    "매출관리": "/sales",
    "원가관리": "/cost",
    "구매관리": "/purchase",
    "상품관리": "/merchandise",
    "상품카테고리관리": "/merchandise/category",
    "상품마스터정보관리": "/merchandise/master",
    "상품 상세 정보 관리": "/merchandise/detail",
    "자재명세서": "/merchandise/bom",
    "생산관리": "/production",
    "생산실적": "/production/performance",
    "생산입고": "/production/inbound",
    "발주 관리": "/production/order",
    "품질 및 이력 관리": "/production/quality",
    "거래처 관리": "/production/customer",
    "재고관리": "/inventory",
    "창고관리": "/inventory/warehouse",
    "원자재 재고 관리": "/inventory/raw-material",
    "상품 재고 관리": "/inventory/product",
    "재고 현황": "/inventory/product/status",
    "상품별 재고 상세": "/inventory/product/detail",
    "입고/출고 관리": "/inventory/product/inout",
    "상품 부자재 관리": "/inventory/sub-material",
    "물류관리": "/logistics",
    "고객관리": "/customer",
    "영업관리": "/business",
    "회계관리": "/accounting",
    "인사관리": "/hr",
    "시스템관리": "/system",
}

ROUTE_TO_MENU = {route: menu for menu, route in MENU_TO_ROUTE.items()}
LOGIN_ROUTE = "/login"
DEFAULT_AUTH_ROUTE = "/home"

def normalize_route(route: str | None) -> str:
    """빈 route나 끝 슬래시를 정리합니다."""
    if not route:
        return LOGIN_ROUTE

    cleaned = route.strip()
    if not cleaned:
        return LOGIN_ROUTE

    if cleaned != "/" and cleaned.endswith("/"):
        cleaned = cleaned[:-1]
    return cleaned

def get_menu_by_route(route: str | None) -> str | None:
    """route에 대응하는 메뉴명을 반환합니다."""
    normalized = normalize_route(route)

    if normalized in ("/", LOGIN_ROUTE):
        return None

    return ROUTE_TO_MENU.get(normalized)



def get_route_by_menu(menu_name: str) -> str:
    """메뉴명에 대응하는 route를 반환합니다."""
    return MENU_TO_ROUTE.get(menu_name, DEFAULT_AUTH_ROUTE)

def get_view_by_route(route: str | None):
    """route 기준으로 실제 우측 본문 뷰를 반환합니다."""
    menu_name = get_menu_by_route(route)

    if not menu_name:
        return ft.Container(content=ft.Text("로그인 화면입니다."))

    return MENU_ITEMS.get(
        menu_name,
        lambda: ft.Container(content=ft.Text("화면을 찾을 수 없습니다")),
    )()