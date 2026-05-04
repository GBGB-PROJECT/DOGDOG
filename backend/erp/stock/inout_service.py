# =========================================================
# 🔥 재고 입고/출고 관리 Service
# - Repository raw DB 값을 화면/API 응답 형태로 변환
# =========================================================

import math
from datetime import datetime

from .inout_repository import (
    count_stock_inout_rows,
    fetch_stock_inout_rows,
)


def _to_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _format_date(value):
    if not value:
        return "-"

    clean = str(value).strip()[:10]
    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return clean.replace(".", "-")


def _format_number(value):
    return f"{_to_int(value):,}"


def _format_quantity(value):
    return f"{_to_int(value):,} ea"


def _format_money(value):
    return f"{_to_int(value):,}"


def _format_weight(value):
    if value is None or value == "":
        return ""

    weight = _to_int(value)
    if weight <= 0:
        return ""

    return f"{weight:,}g"


def _format_product_no(product_detail_id, product_id):
    # 🔥 추가: 상품 상세 정보 관리와 동일하게 상품상세ID-상품ID 형식으로 상품번 표시
    if product_detail_id not in (None, "") and product_id not in (None, ""):
        return f"{product_detail_id}-{product_id}"
    return product_detail_id or product_id or "-"


def _format_item(row):
    inout_type = row.get("inout_type") or "-"
    inbound_id = row.get("inbound_id")
    sales_order_id = row.get("sales_order_id")

    if inout_type == "입고":
        base_id = inbound_id
    else:
        base_id = sales_order_id

    return {
        "inout_type": inout_type,
        "base_id": base_id,
        "inbound_id": inbound_id,
        "sales_order_id": sales_order_id,
        "product_id": row.get("product_id"),
        "product_detail_id": row.get("product_detail_id"),  # 🔥 추가
        "product_no": _format_product_no(row.get("product_detail_id"), row.get("product_id")),  # 🔥 추가
        "brand": row.get("brand") or "-",
        "product_name": row.get("product_name") or "-",
        "weight": _to_int(row.get("weight")),
        "weight_text": _format_weight(row.get("weight")),
        "quantity": _to_int(row.get("quantity")),
        "quantity_text": _format_quantity(row.get("quantity")),
        "unit_price": _to_int(row.get("unit_price")),
        "unit_price_text": _format_money(row.get("unit_price")),
        "amount": _to_int(row.get("amount")),
        "amount_text": _format_money(row.get("amount")),
        "event_date": _format_date(row.get("event_date")),
        "status": row.get("status") or "-",
    }


def get_stock_inout_list(
    search_type="all",
    keyword="",
    inout_type="all",
    page=1,
    size=50,
    start_date=None,
    end_date=None,
):
    page = max(int(page or 1), 1)
    size = max(int(size or 50), 1)
    offset = (page - 1) * size

    total_count = count_stock_inout_rows(
        search_type=search_type,
        keyword=keyword,
        inout_type=inout_type,
        start_date=start_date,
        end_date=end_date,
    )

    rows = fetch_stock_inout_rows(
        search_type=search_type,
        keyword=keyword,
        inout_type=inout_type,
        start_date=start_date,
        end_date=end_date,
        limit=size,
        offset=offset,
    )

    total_pages = max(math.ceil(total_count / size), 1)

    return {
        "items": [_format_item(row) for row in rows],
        "pagination": {
            "page": page,
            "size": size,
            "total_count": total_count,
            "total_pages": total_pages,
        },
    }


__all__ = ["get_stock_inout_list"]
