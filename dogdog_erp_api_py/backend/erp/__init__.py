# Erp router
from .auth.api.erp_signinup_api import router as erp_employee_router
from .home.api.erp_home_api import router as erp_home_router
from .home.api.erp_home_inventory_api import router as erp_home_inventory_router
from .home.api.erp_home_chart_api import router as erp_home_chart_router
from .merchandise.product_detail_api import router as erp_merchandise_router
from .customer.customer_info_api import router as erp_customer_router
from .customer.order_api import router as customer_order_router
from .customer.subscription_api import router as customer_subscription_router
from .production.inbound_api import router as erp_inbound_router
from .production.production_supplier_api import router as erp_supplier_router
from .stock.stock_product_detail_api import router as erp_stock_router
from .hr.employee_api import router as erp_hr_router
from .production.dashboard_api import router as erp_production_dashboard_router
from .production.purchase_order_api import router as erp_purchase_order_router  # 🔥 추가: 발주관리 API
from .stock.dashboard_api import router as stock_dashboard_router
from .stock.inout_api import router as stock_inout_router
from .production.defective_api import router as erp_defective_router  # 🔥 추가: 불량현황조회 API