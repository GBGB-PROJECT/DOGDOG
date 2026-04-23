from fastapi import APIRouter, HTTPException, Query
from backend.erp.product.service import count_product_details, fetch_product_details

router = APIRouter(
    prefix="/erp/products",
    tags=["ERP 상품관리"],
)

ALLOWED_SEARCH_TYPES = {
    "product_name": "상품명",
    "type": "타입",
    "brand": "브랜드",
    "function": "기능",
    "life": "생애주기",
    "main_protein": "주원료",
}


def build_rows_with_no(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, item in enumerate(items, start=start_no):
        row = dict(item)
        row["no"] = index
        rows.append(row)

    return rows


@router.get("/details")
def get_product_detail_list(
    search_type: str = Query(
        default="product_name",
        description="검색 조건",
        examples=["product_name"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["하림"],
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
    search_type = (search_type or "product_name").strip()
    keyword = (keyword or "").strip()

    if search_type not in ALLOWED_SEARCH_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "INVALID_QUERY_PARAMETER",
                "message": f"search_type은 {', '.join(ALLOWED_SEARCH_TYPES.keys())} 중 하나여야 합니다.",
            },
        )

    total_count = count_product_details(
        search_type=search_type,
        keyword=keyword,
    )

    total_pages = max(1, (total_count + size - 1) // size)
    offset = (page - 1) * size

    items = fetch_product_details(
        search_type=search_type,
        keyword=keyword,
        limit=size,
        offset=offset,
    )

    items = build_rows_with_no(items, page, size)

    return {
        "success": True,
        "message": "상품 상세 정보 목록 조회에 성공했습니다.",
        "data": {
            "items": items,
            "pagination": {
                "page": page,
                "size": size,
                "total_count": total_count,
                "total_pages": total_pages,
            },
        },
    }