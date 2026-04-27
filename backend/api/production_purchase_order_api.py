# =========================================================
# 🔥 발주관리 Frontend API Adapter
# - purchase_order_view.py에서 기존 service 함수처럼 호출할 수 있도록 함수명 유지
# - 내부 동작만 실제 HTTP API 호출로 변경
# =========================================================

from .api_client import get_json


def _date_to_text(value):
    if not value:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)[:10]


def _clean_params(params: dict):
    return {key: value for key, value in params.items() if value not in (None, "")}


def fetch_purchase_order_page(
    search_type="purchase_order_id",
    keyword="",
    page=1,
    size=50,
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    return get_json(
        "/erp/production/purchase-order",
        params=_clean_params(
            {
                "search_type": search_type,
                "keyword": keyword,
                "page": page,
                "size": size,
                "start_date": _date_to_text(start_date),
                "end_date": _date_to_text(end_date),
                "date_type": date_type,
            }
        ),
    )


def count_purchase_orders(
    search_type="purchase_order_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    payload = fetch_purchase_order_page(
        search_type=search_type,
        keyword=keyword,
        page=1,
        size=1,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )
    return int(payload.get("data", {}).get("pagination", {}).get("total_count", 0))


def fetch_purchase_orders(
    search_type="purchase_order_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_type="contract_date",
):
    page = (int(offset or 0) // int(limit or 50)) + 1
    payload = fetch_purchase_order_page(
        search_type=search_type,
        keyword=keyword,
        page=page,
        size=limit,
        start_date=start_date,
        end_date=end_date,
        date_type=date_type,
    )
    return payload.get("data", {}).get("items", [])


def fetch_purchase_order_detail(purchase_order_id):
    payload = get_json(f"/erp/production/purchase-order/{purchase_order_id}")
    return payload.get("data") or None


def fetch_purchase_order_items(purchase_order_id):
    payload = get_json(f"/erp/production/purchase-order/{purchase_order_id}/items")
    return payload.get("data", [])
