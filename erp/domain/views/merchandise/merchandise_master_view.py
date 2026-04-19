import flet as ft
from components import common as cm
from components.common.product_search_table_common import build_product_search_table_page
from components.common.modals.field_defs import PRODUCT_MASTER_FIELDS


# =========================================================
# 👊 추가: 상품 마스터 모달 저장값 → 테이블 행 변환
# =========================================================
def product_master_row_adapter(saved_data: dict, next_no: int):
    return {
        "no": str(next_no),
        "product_code": saved_data.get("product_code", ""),
        "product_name": saved_data.get("product_name", ""),
        "product_type": saved_data.get("product_type", ""),
        "brand": saved_data.get("brand", ""),
        "manufacturer": saved_data.get("manufacturer", ""),
        "consumer_price": saved_data.get("consumer_price", ""),
        "spec_weight": saved_data.get("spec_weight", ""),
        "barcode": saved_data.get("barcode", ""),
        "stock_unit": saved_data.get("stock_unit", ""),
        "sale_status": saved_data.get("sale_status", ""),
    }


def erp_merchandise_master_view():
    page_title = "상품관리 > 상품마스터정보관리"

    # 👊 화면 전용 데이터만 남김
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
        {
            "no": "2",
            "product_code": "P-1002",
            "product_name": "강아지 건강사료",
            "product_type": "사료",
            "brand": "개밥개밥",
            "manufacturer": "개밥개밥 제조원",
            "consumer_price": "28,000",
            "spec_weight": "2.0kg",
            "barcode": "8809876543210",
            "stock_unit": "ea",
            "sale_status": "판매중",
        },
        {
            "no": "3",
            "product_code": "P-1003",
            "product_name": "츄르 연어맛",
            "product_type": "간식",
            "brand": "개밥개밥",
            "manufacturer": "개밥개밥 공장",
            "consumer_price": "4,500",
            "spec_weight": "80g",
            "barcode": "8805555444433",
            "stock_unit": "pack",
            "sale_status": "판매중지",
        },
    ]

    return build_product_search_table_page(
        page_title=page_title,
        page_bg=cm.PAGE_BG,
        rows=dummy_rows,
        # 👊 추가: 등록 버튼 → 상품 마스터 등록 모달 연결
        register_button_text="등록",
        register_title="상품 마스터 정보 등록",
        edit_title="상품 마스터 정보 수정",
        register_fields=PRODUCT_MASTER_FIELDS,
        session_prefix="product_master",
        register_row_adapter=product_master_row_adapter,
    )