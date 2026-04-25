from .repository import count_stocks, fetch_stocks


# =========================================================
# 🔥 상품별 재고 상세 Service
# - ERP.stock 중심 조회
# - repository 함수 그대로 제공
# =========================================================

__all__ = [
    "count_stocks",
    "fetch_stocks",
]
