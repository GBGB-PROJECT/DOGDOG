from backend.erp.repository.erp_query_repository import (
    count_customers,
    fetch_customers,
    count_employees,
    fetch_employees,
    count_product_details,
    fetch_product_details,
    count_suppliers,
    fetch_suppliers,
)


# =========================================================
# ☑️ ERP 조회 Service
# - ERP 화면에서 import하는 진입점
# - 실제 DB 접근은 repository에서 처리
# - 현재는 조회 전용 기능만 제공
# =========================================================

__all__ = [
    'count_customers',
    'fetch_customers',
    'count_employees',
    'fetch_employees',
    'count_product_details',
    'fetch_product_details',
    'count_suppliers',
    'fetch_suppliers',
]
