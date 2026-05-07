from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.app.products.repository.productDetail_repository import (
    get_active_product_by_id,
    get_product_detail_by_id,
)
from backend.app.products.repository.productsList_repository import (
    get_product_list, 
    VALID_SORTS
)

# 상품 상세 조회 ----------------------------------------------------------------
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
    
    product_name = f"{product_detail.product_name} {product.weight}g X{product.quantity}"

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

def read_product_list(
    db: Session,
    keyword: str | None = None,
    sort: str | None = None,
    limit: int = 9,
    offset: int = 0,
):
    """
    상품 목록 조회 서비스
    - product 목록 조회
    - sort, search에 맞는 결과만
    """
    # sort 유효성 검사
    if sort and sort not in VALID_SORTS:
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error_code": "INVALID_SORT",
                "message": "유효하지 않은 정렬 조건입니다.",
            },
        )

    rows = get_product_list(
        db=db,
        keyword=keyword,
        sort=sort,
        limit=limit,
        offset=offset,
    )

    data = [
        {
            "product_id": row.product_id,
            "product_detail_id": row.product_detail_id,
            "thumbnail": row.thumbnail,
            "product_name": f"{row.product_name} {row.weight}g X{row.quantity}",
            "brand": row.brand,
            "type": row.type,
            "function": row.function,
            "quantity":row.quantity,
            "weight": float(row.weight) if row.weight is not None else None,
            "is_sample": row.is_sample,
            "retail_price": float(row.retail_price) if row.retail_price is not None else 0,
        }
        for row in rows
    ]

    if not data:
        return {
            "success": True,
            "message": "검색 결과가 없습니다.",
            "data": [],
        }

    return {
        "success": True,
        "message": "상품 목록 조회에 성공했습니다.",
        "data": data,
    }