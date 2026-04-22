from backend.erp.customer.repository import count_customers, fetch_customers
from backend.erp.employee.repository import count_employees, fetch_employees
from backend.erp.product.repository import count_product_details, fetch_product_details
from backend.erp.supplier.repository import count_suppliers, fetch_suppliers


# =========================================================
# ☑️ ERP 조회 Repository 호환용 파일
# - 기존 코드가 backend.erp.repository.erp_query_repository 를 import해도 깨지지 않게 유지
# - 실제 DB 조회 로직은 도메인별 repository 로 분리됨
# =========================================================

__all__ = [
    "count_customers",
    "fetch_customers",
    "count_employees",
    "fetch_employees",
    "count_product_details",
    "fetch_product_details",
    "count_suppliers",
    "fetch_suppliers",
]
