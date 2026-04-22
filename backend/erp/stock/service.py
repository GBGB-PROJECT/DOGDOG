from backend.erp.stock.repository import count_stocks, fetch_stocks


# =========================================================
# ☑️ 재고관리 Service
# - 현재는 조회 전용이라 repository 함수를 그대로 제공
# - 추후 입고/출고/폐기/재고 계산 로직은 이 파일에서 확장
# =========================================================

__all__ = ["count_stocks", "fetch_stocks"]
