from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from backend.app.products.repository.productsList_repository import get_product_list
from backend.app.products.repository.productsWeight_repository import get_product_weight
from backend.app.products.product_service import get_product_detail_service

router = APIRouter(tags=["products"])

# 상품 목록 불러오기 ----------------------------------------------------------------------
# 상품명
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
    
# 상품 무게
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
    
# 상품 상세정보 불러오기 ---------------------------------------------------------------------
@router.get("/products/{product_id}")
def read_product_detail(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    상품 상세 조회 API
    - product_id 기준으로 상품 상세 조회
    """
    try:
        if product_id <= 0:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_PRODUCT_ID",
                    "message": "유효하지 않은 상품 ID입니다."
                }
            )

        result = get_product_detail_service(db=db, product_id=product_id)

        if not result["success"]:
            return JSONResponse(
                status_code=result["status_code"],
                content={
                    "success": False,
                    "error_code": result["error_code"],
                    "message": result["message"]
                }
            )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": result["message"],
                "data": result["data"]
            }
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": f"상품 상세 조회 중 서버 내부 오류가 발생했습니다. {str(e)}"
            }
        )