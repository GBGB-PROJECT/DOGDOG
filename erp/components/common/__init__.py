# 일반 components
from .color import *
from .erp_ui_boxes import *
from .content_move import *
from .product_search_table_common import *


# 차트 components
from .charts.gauge_chart import *
from .charts.stock_pie_chart_box import *
from .charts.line_chart import *
from .charts.production_status_box import *

# 🔥 화면 전환 속도 개선
# - common import 시 생산지시서/발주서/등록팝업 같은 무거운 모달을 자동 import하지 않는다.
# - 필요한 화면에서 아래처럼 직접 import하는 방식은 그대로 유지한다.
#   from components.common.modals.production_order import ProductionOrderDialog
#   from components.common.modals.purchase_order import PurchaseOrderDialog
#   from components.common.modals.modal import build_modal
from .modals.field_defs import *
from .modals.form_inputs import *
