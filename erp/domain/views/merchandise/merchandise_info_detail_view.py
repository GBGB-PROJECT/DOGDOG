from components import common as cm
from components.common.product_search_table_common import build_product_search_table_page
from components.common.modals.field_defs import PRODUCT_DETAIL_FIELDS


def erp_merchandise_info_detail_view():
    page_title = "상품 상세 정보 관리"

    dummy_rows = [
        {
            "no": "1",
            "product_code": "P-1001",
            "product_name": "하림 가장 맛있는 시간",
            "product_type": "사료",
            "brand": "하림",
            "manufacturer": "하림펫푸드",
            "consumer_price": "32,000",
            "spec_weight": "1.2kg",
            "barcode": "8801234567890",
            "stock_unit": "ea",
            "sale_status": "판매중",
        },
    ]

    return build_product_search_table_page(
        page_title=page_title,
        page_bg=cm.PAGE_BG,
        rows=dummy_rows,
        # 👊 추가: 등록 버튼 → 상품 상세 모달 연결
        register_button_text="등록",
        register_title="상품 상세 정보 등록",
        edit_title="상품 상세 정보 수정",
        register_fields=PRODUCT_DETAIL_FIELDS,
        session_prefix="product_detail",
    )