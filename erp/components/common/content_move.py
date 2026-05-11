"""frame과 연결되어 frame의 내용물을 채우는 파일"""
from importlib import import_module
import flet as ft


def _lazy_view(module_path: str, function_name: str):
    """
    🔥 화면 전환 속도 개선
    - content_move.py가 import될 때 모든 view.py를 한꺼번에 import하지 않는다.
    - 실제 route에 진입하는 순간 필요한 view.py만 import한다.
    """
    def _builder():
        module = import_module(module_path)
        return getattr(module, function_name)()

    return _builder


def _ready_view(text: str):
    return lambda: ft.Container(content=ft.Text(text))


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

# 🔥 추가: 아직 실제 화면이 없거나 의미 없는 준비중/빈 화면만 뜨는 1차 메뉴
# - 사이드바에서는 표시만 하고 클릭은 막는다.
DISABLED_MAIN_MENU_ITEMS = [
    "매출관리",
    "원가관리",
    "구매관리",
    "물류관리",
    "영업관리",
    "회계관리",
    "시스템관리",
]

# erp_homecontent.view,
MENU_ITEMS = {
    "홈": _lazy_view("domain.views.home.home_view", "erp_home_view"),
    "매출관리": _ready_view("매출관리 준비 중"),
    "원가관리": _ready_view("원가관리 준비 중"),
    "구매관리": _lazy_view("domain.views.sales.sales_view", "erp_sales_view"),

    # 🔥 수정: 상품관리 대분류를 누르면 안내/텍스트 화면이 아니라 기본 화면(상품 상세 정보 관리)을 바로 표시
    "상품관리": _lazy_view("domain.views.merchandise.product_detail_view", "erp_product_detail_view"),

    # 👊 추가: 상품관리 하위 메뉴 연결
    # "상품마스터정보관리": product_master_view.erp_product_master_view,

    "상품 상세 정보 관리": _lazy_view("domain.views.merchandise.product_detail_view", "erp_product_detail_view"),

    # 🔥 수정: 생산관리 대분류 화면을 생산현황 메뉴의 실제 화면으로 사용
    "생산관리": _lazy_view("domain.views.production.production_view", "erp_production_view"),

    # 🔥 추가: 기존 생산관리 대시보드 화면을 생산현황 하위 메뉴로 이동
    "생산현황": _lazy_view("domain.views.production.production_view", "erp_production_view"),

    "생산입고": _lazy_view("domain.views.production.inbound_view", "erp_inbound_view"),  # 🔥 추가: 생산입고 실제 입고 현황 화면 연결
    "불량 현황": _lazy_view("domain.views.production.defective_view", "erp_defective_view"),  # 🔥 추가: 불량현황조회 화면 연결
    "발주 관리": _lazy_view("domain.views.production.purchase_order_view", "erp_purchase_order_view"),
    "거래처 관리": _lazy_view("domain.views.production.production_supplier_view", "erp_production_supplier_view"),

    # 🔥 수정: 재고관리 대분류를 누르면 안내 화면이 아니라 기본 화면(재고 현황)을 바로 표시
    "재고관리": _lazy_view("domain.views.stock.stock_status_view", "erp_stock_status_view"),

    # ☑️ 추가: 재고관리 하위 메뉴 연결
    "재고 현황": _lazy_view("domain.views.stock.stock_status_view", "erp_stock_status_view"),

    "상품별 재고 상세": _lazy_view("domain.views.stock.stock_product_detail_view", "erp_stock_product_detail_view"),

    "물류관리": _ready_view("물류관리 준비 중"),

    "입고/출고 관리": _lazy_view("domain.views.stock.stock_inout_view", "erp_stock_inout_view"),

    # 🔥 수정: 고객관리 대분류를 누르면 안내/텍스트 화면이 아니라 기본 화면(고객 정보 관리)을 바로 표시
    "고객관리": _lazy_view("domain.views.customer.customer_info_view", "erp_customer_info_view"),

    # 🔥 추가: 고객관리 하위 메뉴 화면 연결
    "고객 정보 관리": _lazy_view("domain.views.customer.customer_info_view", "erp_customer_info_view"),
    # 🔥 수정: 고객 주문 관리 실제 화면 연결
    "고객 주문 관리": _lazy_view("domain.views.customer.customer_order_view", "erp_customer_order_view"),

    "고객 구독 관리": _lazy_view("domain.views.customer.customer_subscription_view", "erp_customer_subscription_view"),  # 🔥 수정: 고객 구독 관리 실제 화면 연결
    # "고객 문의 관리": lambda: ft.Container(
    #     expand=True,
    #     alignment=ft.Alignment(0, 0),
    #     content=ft.Text("고객 문의 관리 준비 중"),
    # ),
    # "고객 센터 관리": lambda: ft.Container(
    #     expand=True,
    #     alignment=ft.Alignment(0, 0),
    #     content=ft.Text("고객 센터 관리 준비 중"),
    # ),

    "영업관리": _ready_view("영업관리 준비 중"),
    "회계관리": _ready_view("회계관리 준비 중"),

    # 🔥 수정: 인사관리 대분류를 누르면 바로 실제 사원 관리 화면을 표시
    "인사관리": _lazy_view("domain.views.hr.employee_view", "erp_employee_view"),

    # 🔥 추가: 인사관리 하위 메뉴 - 사원 관리 실제 화면 연결
    "사원 관리": _lazy_view("domain.views.hr.employee_view", "erp_employee_view"),

    "시스템관리": _ready_view("시스템관리 준비 중"),
}

"""각 side바의 제목 탭을 의미함
    1차 메뉴: 최초 클릭
    2차 메뉴: 1차 클릭 수 세부 항목을 재클릭"""

'''재고관리 메뉴 - stock'''
# 재고관리 1차 메뉴 -> 최초 출력
STOCK_MAIN_ITEMS = [
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
]

# ☑️ 추가: 재고관리 관련 상태 전체 묶음
STOCK_ALL_ITEMS = [
    "재고관리",
    "창고관리",
    "원자재 재고 관리",
    "상품 재고 관리",
    "상품 부자재 관리",
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]

# 🔥 추가: 아직 실제 화면이 없거나 의미 없는 화면으로 이어지는 재고관리 하위 메뉴
# - 글자색은 그대로 두고 클릭만 막는다.
DISABLED_STOCK_MENU_ITEMS = [
    "창고관리",
    "원자재 재고 관리",
    "상품 부자재 관리",
]


##  재고 관리 2차 메뉴: 상품 재고관리에 대한 세부 항목
STOCK_PRODUCT_ITEMS = [
    "재고 현황",
    "상품별 재고 상세",
    "입고/출고 관리",
]
# ☑️ 
STOCK_MAIN_ITEMS = STOCK_MAIN_ITEMS
STOCK_ALL_ITEMS = STOCK_ALL_ITEMS
STOCK_PRODUCT_ITEMS = STOCK_PRODUCT_ITEMS

'''==================== 재고관리 종료 ===================='''

'''상품관리 메뉴 - sales'''
# ☑️ 추가: 상품관리 1차 메뉴
PRODUCT_MAIN_ITEMS = [
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# 🔥 추가: 아직 실제 화면이 없거나 의미 없는 화면으로 이어지는 상품관리 하위 메뉴
# - 글자색은 그대로 두고 클릭만 막는다.
DISABLED_PRODUCT_MENU_ITEMS = [
    "상품카테고리관리",
    "상품마스터정보관리",
    "자재명세서",
]

# ☑️ 추가: 상품관리 전체 묶음
PRODUCT_ALL_ITEMS = [
    "상품관리",
    "상품카테고리관리",
    "상품마스터정보관리",
    "상품 상세 정보 관리",
    "자재명세서",
]

# ☑️ 추가: 생산관리 1차 메뉴
PRODUCTION_MAIN_ITEMS = [
    # 🔥 수정: 기존 생산관리 기본 화면을 생산실적이 아니라 생산현황 메뉴로 표시
    "생산현황",
    "생산입고",
    "불량 현황",  # 🔥 추가: 불량현황조회 메뉴
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]

# 🔥 추가: 아직 실제 화면이 없거나 의미 없는 화면으로 이어지는 생산관리 하위 메뉴
# - 글자색은 그대로 두고 클릭만 막는다.
DISABLED_PRODUCTION_MENU_ITEMS = [
    # 🔥 수정: 생산현황은 실제 화면이 있으므로 비활성에서 제외
    "품질 및 이력 관리",
]

# ☑️ 추가: 생산관리 전체 묶음
PRODUCTION_ALL_ITEMS = [
    "생산관리",
    "생산현황",
    "생산입고",
    "불량 현황",  # 🔥 추가: 불량현황조회 메뉴
    "발주 관리",
    "품질 및 이력 관리",
    "거래처 관리",
]

# 🔥 추가: 고객관리 하위 메뉴
CUSTOMER_MAIN_ITEMS = [
    "고객 정보 관리",
    "고객 주문 관리",
    "고객 구독 관리",
    "고객 문의 관리",
    "고객 센터 관리",
]

# 🔥 추가: 아직 실제 화면이 없거나 의미 없는 화면으로 이어지는 고객관리 하위 메뉴
# - 글자색은 그대로 두고 클릭만 막는다.
DISABLED_CUSTOMER_MENU_ITEMS = [
    "고객 문의 관리",
    "고객 센터 관리",
]

# 🔥 추가: 고객관리 확장 사이드바 진입 조건 묶음
CUSTOMER_ALL_ITEMS = [
    "고객관리",
    "고객 정보 관리",
    "고객 주문 관리",
    "고객 구독 관리",
    "고객 문의 관리",
    "고객 센터 관리",
]

# 🔥 추가: 인사관리 하위 메뉴
# - 현재 실제 화면이 있는 항목은 사원 관리 하나만 둔다.
HR_MAIN_ITEMS = [
    "사원 관리",
]

# 🔥 추가: 인사관리 확장 사이드바 진입 조건 묶음
HR_ALL_ITEMS = [
    "인사관리",
    "사원 관리",
]
'''==================== 상품관리 종료 ===================='''

## =============== 라우트 연결목적
### 라우트 연결을 위한 더미
MENU_TO_ROUTE = {
    "홈": "/home",
    "매출관리": "/sales",
    "원가관리": "/cost",
    "구매관리": "/purchase",
    # 🔥 수정: 상품관리 클릭 시 /merchandise 안내 화면이 아니라 상품 상세 정보 관리 route로 바로 이동
    "상품관리": "/merchandise/detail",
    "상품카테고리관리": "/merchandise/category",
    "상품 상세 정보 관리": "/merchandise/detail",
    "자재명세서": "/merchandise/bom",
    # 🔥 수정: 생산관리 클릭 시 중간/기본 화면 대신 생산현황 route로 바로 이동
    "생산관리": "/production/status",
    # 🔥 추가: 기존 생산관리 화면을 생산현황 메뉴 route로 연결
    "생산현황": "/production/status",
    "생산입고": "/production/inbound",
    "불량 현황": "/production/defective",  # 🔥 추가: 불량현황조회 route 연결
    "발주 관리": "/production/order",
    "품질 및 이력 관리": "/production/quality",
    "거래처 관리": "/production/supplier",
    # 🔥 수정: 재고관리 클릭 시 /stock 안내 화면이 아니라 재고 현황 route로 바로 이동
    "재고관리": "/stock/product/status",
    "창고관리": "/stock/warehouse",
    "원자재 재고 관리": "/stock/raw-material",

    # 🔥 수정: 상품 재고 관리도 기본 하위 화면인 재고 현황으로 바로 이동
    "상품 재고 관리": "/stock/product/status",
    "재고 현황": "/stock/product/status",
    "상품별 재고 상세": "/stock/product/detail",
    "입고/출고 관리": "/stock/product/inout",
    "상품 부자재 관리": "/stock/sub-material",
    "물류관리": "/logistics",
    # 🔥 수정: 고객관리 클릭 시 /customer 안내 화면이 아니라 고객 정보 관리 route로 바로 이동
    "고객관리": "/customer/info",
    # 🔥 추가: 고객관리 하위 메뉴 route 연결
    "고객 정보 관리": "/customer/info",
    "고객 주문 관리": "/customer/order",
    "고객 구독 관리": "/customer/subscription",
    "영업관리": "/business",
    "회계관리": "/accounting",
    # 🔥 수정: 인사관리 클릭 시 바로 사원 관리 route로 이동
    "인사관리": "/hr/employee",
    # 🔥 추가: 인사관리 하위 메뉴 route
    "사원 관리": "/hr/employee",
    "시스템관리": "/system",
}

ROUTE_TO_MENU = {route: menu for menu, route in MENU_TO_ROUTE.items()}
LOGIN_ROUTE = "/login"
DEFAULT_AUTH_ROUTE = "/home"

# 🔥 추가: 중간 메뉴 route로 들어와도 실제 기본 화면 route로 보정
# - /stock 은 재고관리 안내 화면이 아니라 재고 현황 화면으로 연결
# - /stock/product 는 상품 재고 관리의 기본 하위 화면인 재고 현황으로 연결
# - /customer 는 고객관리 안내/텍스트 화면이 아니라 고객 정보 관리 화면으로 연결
# - /merchandise 는 상품관리 안내/텍스트 화면이 아니라 상품 상세 정보 관리 화면으로 연결
# - /hr 은 인사관리 대분류 route가 아니라 사원 관리 화면으로 연결
# - /production 은 생산관리 대분류 route가 아니라 생산현황 화면으로 연결
ROUTE_ALIASES = {
    "/stock": "/stock/product/status",
    "/stock/product": "/stock/product/status",
    "/customer": "/customer/info",
    "/merchandise": "/merchandise/detail",
    "/hr": "/hr/employee",
    "/production": "/production/status",
}

def normalize_route(route: str | None) -> str:
    """빈 route나 끝 슬래시를 정리합니다."""
    if not route:
        return LOGIN_ROUTE

    cleaned = route.strip()
    if not cleaned:
        return LOGIN_ROUTE

    if cleaned != "/" and cleaned.endswith("/"):
        cleaned = cleaned[:-1]

    # 🔥 추가: 대분류/중간 메뉴 route를 실제 기본 하위 화면 route로 변환
    return ROUTE_ALIASES.get(cleaned, cleaned)

def get_menu_by_route(route: str | None) -> str | None:
    """route에 대응하는 메뉴명을 반환합니다."""
    normalized = normalize_route(route)

    if normalized in ("/", LOGIN_ROUTE):
        return None

    return ROUTE_TO_MENU.get(normalized)



def get_route_by_menu(menu_name: str) -> str:
    """메뉴명에 대응하는 route를 반환합니다."""
    # 🔥 추가: 비활성 메뉴는 혹시 다른 곳에서 호출되어도 의미 없는 화면으로 이동하지 않게 홈으로 보정
    if (
        menu_name in DISABLED_MAIN_MENU_ITEMS
        or menu_name in DISABLED_PRODUCT_MENU_ITEMS
        or menu_name in DISABLED_PRODUCTION_MENU_ITEMS
        or menu_name in DISABLED_CUSTOMER_MENU_ITEMS
    ):
        return DEFAULT_AUTH_ROUTE

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