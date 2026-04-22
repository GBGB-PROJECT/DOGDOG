from backend.erp.customer.repository import count_customers, fetch_customers


# =========================================================
# ☑️ 고객관리 Service
# - 현재는 조회 전용이라 repository 함수를 그대로 제공
# - 추후 고객 상태 표시값 가공/등록/수정 로직은 이 파일에서 확장
# =========================================================

__all__ = ["count_customers", "fetch_customers"]
