from enum import Enum
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from app.products.repository.productsList_repository import get_product_list
from app.products.repository.productsWeight_repository import get_product_weight
from dependencies import get_current_user
from app.products.product_service import get_product_detail_service, read_product_list
from app.products.schemas import ProductListResponse, ProductWeightResponse


router = APIRouter(prefix="/api/v1/products", tags=["Products"])

# 상품 목록 불러오기 ----------------------------------------------------------------------
# 상품 썸네일, 가격, 이름
class ProductSort(str, Enum): 
    price_desc = "price_desc" 
    price_asc = "price_asc" 
    weight_desc = "weight_desc" 
    weight_asc = "weight_asc" 

@router.get("")
def get_products(
    keyword: str | None = Query(default=None, description="검색 키워드"),
    sort: ProductSort | None = Query(default=None, description="정렬 조건"),
    db: Session = Depends(get_db),
):
    """
    상품 목록 조회 API
    - keyword: 상품명, 브랜드명, 기능, 타입, 단백질 관련 검색
    - sort: price_desc, price_asc, weight_desc, weight_asc
    """
    try:
        return read_product_list(
            db=db,
            keyword=keyword,
            sort=sort,
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": f"상품 목록 조회 실패: {str(e)}",
            },
        )
    
# 상품명 - product_detail
#/products
@router.get("/name")
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
@router.get("/weights", response_model=ProductWeightResponse)
def read_products_weights(
        #/api/v1/products/weights?product_detail_id=1
        product_detail_id: int = Query(
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
@router.get("/{product_id}")
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
        print(f"서버 내부 오류 발생: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": f"상품 상세 조회 중 서버 내부 오류가 발생했습니다. {str(e)}"
            }
        )