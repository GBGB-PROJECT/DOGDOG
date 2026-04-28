# erp/api/erp_httpx_api.py

import httpx

# 🔥 FastAPI 서버 주소
BASE_URL = "http://127.0.0.1:8000"


def _get(path: str, params: dict | None = None):
    """
    🔥 공통 GET 요청 함수
    - FastAPI 응답 구조:
      {
        "success": True,
        "message": "...",
        "data": {...}
      }
    """
    url = f"{BASE_URL}{path}"

    try:
        response = httpx.get(url, params=params, timeout=10.0)
        response.raise_for_status()
        result = response.json()
        return result.get("data", {})
    except httpx.RequestError as e:
        print(f"🔥 API 요청 실패: {url}")
        print(e)
        return {}


def _list_request(path: str, search_type="", keyword="", page=1, size=50, start_date=None, end_date=None, **extra):
    params = {
        "search_type": search_type,
        "keyword": keyword,
        "page": page,
        "size": size,
    }

    if start_date:
        params["start_date"] = str(start_date)

    if end_date:
        params["end_date"] = str(end_date)

    params.update(extra)

    data = _get(path, params=params)

    return {
        "items": data.get("items", []),
        "pagination": data.get(
            "pagination",
            {
                "page": page,
                "size": size,
                "total_count": 0,
                "total_pages": 1,
            },
        ),
    }


# =========================================================
# ☑️ 고객 정보 조회
# =========================================================

def fetch_customers(search_type="customer_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/customer/info",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_customers(search_type="customer_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/customer/info",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 고객 주문 조회
# =========================================================

def fetch_customer_orders(search_type="order_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/customer/order",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_customer_orders(search_type="order_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/customer/order",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 고객 구독 조회
# =========================================================

def fetch_customer_subscriptions(search_type="subscription_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/customer/subscription",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_customer_subscriptions(search_type="subscription_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/customer/subscription",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 사원 정보 조회
# =========================================================

def fetch_employees(search_type="employee_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/hr",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_employees(search_type="employee_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/hr",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 상품 상세 정보 조회
# =========================================================

def fetch_product_join_rows(search_type="product_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/merchandise/details",  # 🔥 상품 상세 정보 API 실제 경로로 수정",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_product_join_rows(search_type="product_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/merchandise/details",  # 🔥 상품 상세 정보 API 실제 경로로 수정",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 생산 입고 현황 조회
# =========================================================

def fetch_inbounds(
    search_type="inbound_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_filter_type="inbound_start",
):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/production/inbound",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        # 🔥 생산관리 카드에서 넘어온 월 기준은 검색조건이 바뀌어도 유지
        date_filter_type=date_filter_type,
    )

    return result["items"]


def count_inbounds(
    search_type="inbound_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_filter_type="inbound_start",
):
    result = _list_request(
        "/erp/production/inbound",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        # 🔥 생산관리 카드에서 넘어온 월 기준은 검색조건이 바뀌어도 유지
        date_filter_type=date_filter_type,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 거래처 조회
# =========================================================

def fetch_suppliers(search_type="supplier_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/production/supplier",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_suppliers(search_type="supplier_id", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/production/supplier",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 상품별 재고 상세 조회
# =========================================================

def fetch_stocks(
    search_type="product_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_filter_type="expiration_date",
):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/stock/product-detail",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        date_filter_type=date_filter_type,
    )

    return result["items"]


def count_stocks(
    search_type="product_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_filter_type="expiration_date",
):
    result = _list_request(
        "/erp/stock/product-detail",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        date_filter_type=date_filter_type,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 생산관리 대시보드
# =========================================================

def fetch_production_dashboard(year=None, month=None):
    params = {}

    if year:
        params["year"] = year

    if month:
        params["month"] = month

    return _get("/erp/production/dashboard", params=params)

# =========================================================
# ☑️ 재고 현황 대시보드
# =========================================================

def fetch_stock_dashboard(year=None, month=None):
    params = {}

    if year:
        params["year"] = year

    if month:
        params["month"] = month

    return _get("/erp/stock/dashboard", params=params)

# =========================================================
# ☑️ 재고 입고/출고 관리
# =========================================================

def fetch_stock_inouts(
    search_type="all",
    keyword="",
    inout_type="all",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/stock/inout",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        inout_type=inout_type,
    )

    return result["items"]


def count_stock_inouts(
    search_type="all",
    keyword="",
    inout_type="all",
    start_date=None,
    end_date=None,
):
    result = _list_request(
        "/erp/stock/inout",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        inout_type=inout_type,
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 발주관리
# =========================================================

def fetch_purchase_orders(
    search_type="purchase_order_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    page = (offset // limit) + 1

    result = _list_request(
        "/erp/production/purchase-order",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )

    return result["items"]


def count_purchase_orders(
    search_type="purchase_order_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    result = _list_request(
        "/erp/production/purchase-order",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )

    return result["pagination"].get("total_count", 0)


def fetch_purchase_order_detail(purchase_order_id):
    data = _get(f"/erp/production/purchase-order/{purchase_order_id}")
    return data.get("item", {})


def fetch_purchase_order_items(purchase_order_id):
    data = _get(f"/erp/production/purchase-order/{purchase_order_id}/items")
    return data.get("items", [])


# =========================================================
# ⚠️ 등록 기능은 현재 API에 POST가 없으면 httpx 전환 불가
# =========================================================

def create_customer(*args, **kwargs):
    print("🔥 create_customer는 아직 POST API가 필요합니다.")
    return None


def create_employee(*args, **kwargs):
    print("🔥 create_employee는 아직 POST API가 필요합니다.")
    return None


def create_product_detail(*args, **kwargs):
    print("🔥 create_product_detail는 아직 POST API가 필요합니다.")
    return None


def create_supplier(*args, **kwargs):
    print("🔥 create_supplier는 아직 POST API가 필요합니다.")
    return None

# =========================================================
# ☑️ 불량현황조회
# - 기존 공통 _list_request() 사용
# - _request_json 함수는 이 파일에 없으므로 사용하면 NameError 발생
# =========================================================

def fetch_defectives(
    search_type="inbound_id",
    keyword="",
    page=1,
    size=50,
    start_date=None,
    end_date=None,
    offset=None,  # 🔥 기존 view 호출 호환용
    limit=None,   # 🔥 기존 view 호출 호환용
):
    # 🔥 defective_view.py가 offset/limit를 같이 넘겨도 기존 조회 화면들과 같은 방식으로 page/size 계산
    if limit:
        size = limit

    if offset is not None and limit:
        page = (offset // limit) + 1

    result = _list_request(
        "/erp/production/defective",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=size,
        start_date=start_date,
        end_date=end_date,
    )

    return result["items"]


def count_defectives(
    search_type="inbound_id",
    keyword="",
    start_date=None,
    end_date=None,
):
    result = _list_request(
        "/erp/production/defective",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
    )

    return result["pagination"].get("total_count", 0)
