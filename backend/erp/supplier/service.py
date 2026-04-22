from backend.erp.supplier.repository import count_suppliers, fetch_suppliers


# =========================================================
# ☑️ 거래처관리 Service
# - 현재는 조회 전용이라 repository 함수를 그대로 제공
# - 추후 거래처 등록/수정/결제일 가공 로직은 이 파일에서 확장
# =========================================================

__all__ = ["count_suppliers", "fetch_suppliers"]
