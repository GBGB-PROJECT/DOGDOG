from backend.erp.customer.service import count_customers, fetch_customers
from backend.erp.employee.service import count_employees, fetch_employees
from backend.erp.product.service import count_product_details, fetch_product_details
from backend.erp.supplier.service import count_suppliers, fetch_suppliers


# =========================================================
# ☑️ ERP 조회 Service 호환용 파일
# - 기존 화면/코드가 backend.erp.service.erp_query_service 를 import해도 깨지지 않게 유지
# - 실제 기능은 도메인별 service 로 분리됨
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
