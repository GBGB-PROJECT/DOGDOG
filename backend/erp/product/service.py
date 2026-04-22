from backend.erp.product.repository import count_product_details, fetch_product_details


# =========================================================
# ☑️ 상품관리 Service
# - 현재는 조회 전용이라 repository 함수를 그대로 제공
# - 추후 상품 등록/수정/상세 가공 로직은 이 파일에서 확장
# =========================================================

__all__ = ["count_product_details", "fetch_product_details"]
