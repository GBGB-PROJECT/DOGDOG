from sqlalchemy.orm import Session

from backend.app.products.repository.productDetail_repository import (
    get_active_product_by_id,
    get_product_detail_by_id,
)

def get_product_detail_service(db: Session, product_id: int):
    """
    상품 상세 조회 서비스
    - product 1건 조회
    - 연결된 product_detail 1건 조회
    - 상세 응답 조합
    """

    # 1. 활성 상품 조회
    product = get_active_product_by_id(db=db, product_id=product_id)
    if product is None:
        return {
            "success": False,
            "status_code": 404,
            "error_code": "PRODUCT_NOT_FOUND",
            "message": "조회 가능한 상품이 없습니다."
        }

    # 2. 상품 상세 조회
    product_detail = get_product_detail_by_id(
        db=db,
        product_detail_id=product.product_detail_id
    )
    if product_detail is None:
        return {
            "success": False,
            "status_code": 404,
            "error_code": "PRODUCT_DETAIL_NOT_FOUND",
            "message": "상품 상세 정보가 존재하지 않습니다."
        }
    
    product_name = f"{product_detail.product_name} {product.weight}g"

    # 3. 최종 데이터 조합
    data = {
        "product_id": product.product_id,
        "product_detail_id": product_detail.product_detail_id,

        "brand": product_detail.brand,
        "product_name": product_name,

        "type": product_detail.type,
        "life": product_detail.life,
        "function": product_detail.function,
        "description": product_detail.description,
        "calories": float(product_detail.calories) if product_detail.calories is not None else None,
        
        "thumbnail": product_detail.thumbnail,
        "pdi": product_detail.pdi,
        
        "quantity": product.quantity,
        "weight": product.weight,
        "retail_price": float(product.retail_price) if product.retail_price is not None else None,
        "is_sample": product.is_sample
    }

    return {
        "success": True,
        "status_code": 200,
        "message": "상품 상세 조회에 성공했습니다.",
        "data": data
    }