from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from database.db import get_db
from backend.app.domains.products.repository.productsList_repository import get_product_list
from backend.app.domains.products.repository.productsWeight_repository import get_product_weight

router = APIRouter(tags=["products"])

#/products
@router.get("/products")
def read_products(
        keyword: str | None = Query(
            default=None,
            max_length=50,
            description="상품명 검색어"
        ),
        db: Session = Depends(get_db)
    ):
    try:
        products = get_product_list(db=db, keyword=keyword)

        data = [
            {
                "product_detail_id": product.product_detail_id,
                "product_name": product.product_name,
                # "weight": product.weight,
                # "active": product.active
            }
            for product in products
        ]

        return {
            "success": True,
            "message": "상품 목록을 조회했습니다.",
            "data": data
        }

    except Exception as e:
        print("상품 목록 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PRODUCT_LIST_READ_FAILED",
                "message": "상품 목록 조회에 실패했습니다."
            }
        )
    
#/products/weights
@router.get("/products/weights")
def read_products_weights(
        #/products/weights?product_detail_id=1
        product_detail_id: int = Query(
            # default=None,
            # max_length=50,
            description="상품 디테일 ID"
        ),
        db: Session = Depends(get_db)
    ):
    try:
        products = get_product_weight(db=db, product_detail_id=product_detail_id)

        data = [
            {
                "product_id": product.product_id,
                # "product_detail_id": product.product_detail_id,
                "weight": product.weight,
                "active": product.active
            }
            for product in products
        ]

        return {
            "success": True,
            "message": "상품 무게를 조회했습니다.",
            "data": data
        }

    except Exception as e:
        print("상품 무게 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PRODUCT_LIST_READ_FAILED",
                "message": "상품 무게 조회에 실패했습니다."
            }
        )
    