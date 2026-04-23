from math import ceil
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from backend.erp.product.service import count_product_join_rows, fetch_product_join_rows

router = APIRouter(
    prefix="/erp/products",
    tags=["ERP 상품관리"],
)

SEARCH_TYPE_LABELS = {
    "product_name": "상품명",
    "type": "타입",
    "brand": "브랜드",
    "function": "기능",
    "main_protein": "주원료",
    "weight": "중량",
    "retail_price": "판매가",
    "quantity": "수량",
}


@router.get(
    "/details",
    summary="상품 상세 정보 관리 목록 조회",
    description=(
        "상품관리 > 상품 상세 정보 관리 화면에서 사용하는 목록 조회 API입니다. "
        "OPD.product 와 OPD.product_detail 을 product_detail_id 로 JOIN 하여 "
        "검색 조건(search_type), 검색어(keyword), 페이지(page), 페이지 크기(size)를 받아 "
        "페이지네이션된 목록을 반환합니다."
    ),
)
def get_product_detail_list(
    search_type: Literal[
        "product_name",
        "type",
        "brand",
        "function",
        "main_protein",
        "weight",
        "retail_price",
        "quantity",
    ] = Query(
        default="product_name",
        description="검색 조건",
        examples=["product_name"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["더리얼 독"],
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호",
        examples=[1],
    ),
    size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="페이지당 조회 건수",
        examples=[50],
    ),
):
    try:
        clean_search_type = (search_type or "product_name").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_product_join_rows(
            search_type=clean_search_type,
            keyword=clean_keyword,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_product_join_rows(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
        )

        start_no = ((page - 1) * size) + 1
        result_items = []

        for index, item in enumerate(items, start=start_no):
            row = dict(item)
            row["no"] = index
            result_items.append(row)

        if total_count == 0:
            return {
                "success": True,
                "message": "일치하는 정보가 없습니다.",
                "data": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "size": size,
                        "total_count": 0,
                        "total_pages": 1,
                    },
                    "search": {
                        "search_type": clean_search_type,
                        "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                        "keyword": clean_keyword,
                    },
                },
            }

        return {
            "success": True,
            "message": "상품 상세 정보 목록 조회에 성공했습니다.",
            "data": {
                "items": result_items,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                },
                "search": {
                    "search_type": clean_search_type,
                    "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                    "keyword": clean_keyword,
                },
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": f"상품 상세 정보 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )