from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from app.products.repository.productsList_repository import get_product_list
from app.products.repository.productsWeight_repository import get_product_weight
from dependencies import get_current_user
from app.products.schemas import ProductListResponse, ProductWeightResponse

router = APIRouter(prefix="/api/v1/products", tags=["Products"])

# 상품 목록 불러오기 ----------------------------------------------------------------------
# 상품명
@router.get("", response_model=ProductListResponse)
def read_products(
        keyword: str | None = Query(
            default=None,
            max_length=50,
            description="상품명 검색어"
        ),
        customer_id: int = Depends(get_current_user),
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

# 상품 무게
@router.get("/weights", response_model=ProductWeightResponse)
def read_products_weights(
        #/api/v1/products/weights?product_detail_id=1
        product_detail_id: int = Query(
            description="상품 디테일 ID"
        ),
        customer_id: int = Depends(get_current_user),
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