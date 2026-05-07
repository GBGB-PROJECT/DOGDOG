# erp/api/erp_httpx_api.py

import time
from collections import OrderedDict
from threading import RLock

import httpx

# 🔥 FastAPI 서버 주소
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv("ERP_API_URL") if os.getenv("ERP_API_URL") else "http://localhost:8001"

# 🔥 화면 전환 속도 개선
# - 요청마다 새 연결을 만들지 않고 공통 httpx.Client를 재사용한다.
_CLIENT = httpx.Client(
    base_url=BASE_URL,
    timeout=10.0,
    limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
)
_GET_CACHE = OrderedDict()
_GET_CACHE_TTL_SECONDS = 20.0
_GET_CACHE_MAX_SIZE = 256
_GET_CACHE_LOCK = RLock()


def _cache_key(path: str, params: dict | None = None):
    frozen_params = tuple(sorted((params or {}).items()))
    return path, frozen_params


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
    key = _cache_key(path, params)
    now = time.monotonic()
    with _GET_CACHE_LOCK:
        cached = _GET_CACHE.get(key)
        if cached and now - cached["time"] <= _GET_CACHE_TTL_SECONDS:
            cached["time"] = now
            _GET_CACHE.move_to_end(key)
            return cached["data"]

    try:
        response = _CLIENT.get(path, params=params)
        response.raise_for_status()
        result = response.json()
        data = result.get("data", {})
        fetched_at = time.monotonic()
        with _GET_CACHE_LOCK:
            _GET_CACHE[key] = {"time": fetched_at, "data": data}
            _GET_CACHE.move_to_end(key)
            while len(_GET_CACHE) > _GET_CACHE_MAX_SIZE:
                _GET_CACHE.popitem(last=False)
        return data

    except httpx.HTTPStatusError as e:
        print(f"🔥 API 응답 오류: {url}")
        print(f"status_code={e.response.status_code}")
        print(e.response.text)
        return {}

    except httpx.RequestError as e:
        print(f"API request failed: {url}")
        print(e)
        return {}

    except Exception as e:
        print(f"Unexpected API error: {url}")
        print(e)
        return {}


def _extract_error_message(result):
    detail = result.get("detail") if isinstance(result, dict) else None
    if isinstance(detail, dict):
        return detail.get("message") or str(detail)
    if isinstance(detail, str):
        return detail
    if isinstance(result, dict):
        return result.get("message") or str(result)
    return str(result)


def _mutate(method: str, path: str, payload: dict | None = None):
    url = f"{BASE_URL}{path}"
    try:
        response = _CLIENT.request(method, path, json=payload or {})
        result = response.json()
        response.raise_for_status()
        with _GET_CACHE_LOCK:
            _GET_CACHE.clear()
        return result.get("data", {})
    except httpx.HTTPStatusError as e:
        try:
            result = e.response.json()
        except Exception:
            result = {"detail": e.response.text}
        raise RuntimeError(_extract_error_message(result)) from e
    except httpx.RequestError as e:
        raise RuntimeError(f"API 요청 실패: {url} / {e}") from e
    except Exception as e:
        raise RuntimeError(f"API 처리 실패: {url} / {e}") from e


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

def fetch_customers(search_type="email", keyword="", limit=50, offset=0, start_date=None, end_date=None):
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


def fetch_customers_page(search_type="email", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    return _list_request(
        "/erp/customer/info",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )


def count_customers(search_type="email", keyword="", start_date=None, end_date=None):
    result = _list_request(
        "/erp/customer/info",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        # 🔥 수정: 고객 정보 조회는 가입일 기준 DatePicker만 사용하므로
        # 🔥 정의되지 않은 date_filter_type을 전송하지 않음
    )

    return result["pagination"].get("total_count", 0)


# =========================================================
# ☑️ 고객 주문 조회
# =========================================================

def fetch_customer_orders(search_type="order_number", keyword="", limit=50, offset=0, start_date=None, end_date=None):
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


def fetch_customer_orders_page(search_type="order_number", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    return _list_request(
        "/erp/customer/order",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )


def count_customer_orders(search_type="order_number", keyword="", start_date=None, end_date=None):
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

def fetch_customer_subscriptions(search_type="subs_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
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


def fetch_customer_subscriptions_page(search_type="subs_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    page = (offset // limit) + 1

    return _list_request(
        "/erp/customer/subscription",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
    )


def count_customer_subscriptions(search_type="subs_id", keyword="", start_date=None, end_date=None):
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

def fetch_employees(search_type="username", keyword="", limit=50, offset=0, start_date=None, end_date=None):
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


def count_employees(search_type="username", keyword="", start_date=None, end_date=None):
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


def fetch_inbounds_page(
    search_type="inbound_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_filter_type="inbound_start",
    include_total=True,
):
    page = (offset // limit) + 1

    return _list_request(
        "/erp/production/inbound",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        date_filter_type=date_filter_type,
        include_total=include_total,
    )


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
    search_type="product",
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
    search_type="product",
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


def fetch_purchase_orders_page(
    search_type="purchase_order_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    page = (offset // limit) + 1

    return _list_request(
        "/erp/production/purchase-order",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )


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



def create_product_detail(*args, **kwargs):
    payload = args[0] if args else kwargs
    return _mutate("POST", "/erp/merchandise/details", payload)


def update_product_detail(product_id, payload):
    return _mutate("PATCH", f"/erp/merchandise/details/{product_id}", payload)


def create_supplier(*args, **kwargs):
    payload = args[0] if args else kwargs
    return _mutate("POST", "/erp/production/supplier", payload)


def update_supplier(supplier_id, payload):
    return _mutate("PATCH", f"/erp/production/supplier/{supplier_id}", payload)

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
    date_filter_type="inbound_complete",  # 🔥 추가: DatePicker 날짜 기준
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
        # 🔥 추가: 검색조건과 날짜 기준 분리
        date_filter_type=date_filter_type,
    )

    return result["items"]


def fetch_defectives_page(
    search_type="inbound_id",
    keyword="",
    page=1,
    size=50,
    start_date=None,
    end_date=None,
    offset=None,
    limit=None,
    date_filter_type="inbound_complete",
    include_total=True,
):
    if limit:
        size = limit

    if offset is not None and limit:
        page = (offset // limit) + 1

    return _list_request(
        "/erp/production/defective",
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=size,
        start_date=start_date,
        end_date=end_date,
        date_filter_type=date_filter_type,
        include_total=include_total,
    )


def count_defectives(
    search_type="inbound_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_filter_type="inbound_complete",  # 🔥 추가: DatePicker 날짜 기준
):
    result = _list_request(
        "/erp/production/defective",
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        # 🔥 수정: 목록 조회와 count 조회의 날짜 기준을 동일하게 전달
        date_filter_type=date_filter_type,
    )

    return result["pagination"].get("total_count", 0)
