from backend.erp.production.repository import (
    count_suppliers,
    fetch_suppliers,
    count_purchase_orders,
    fetch_purchase_orders,
    fetch_purchase_order_detail,
    fetch_purchase_order_items,
)


# =========================================================
# ☑️ 생산관리 Service
# - 거래처관리: supplier 조회
# - 발주관리: purchase_order + purchase_order_item JOIN 조회
# =========================================================

__all__ = [
    "count_suppliers",
    "fetch_suppliers",
    "count_purchase_orders",
    "fetch_purchase_orders",
    "fetch_purchase_order_detail",
    "fetch_purchase_order_items",
]
