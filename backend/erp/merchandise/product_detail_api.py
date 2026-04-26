from math import ceil
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from .merchandise_detail_service import count_product_join_rows, fetch_product_join_rows

router = APIRouter(
    prefix="/erp/merchandise",
    tags=["merchandise"],
)

SEARCH_TYPE_LABELS = {
    "product_name": "상품명",
    "type": "타입",
    "brand": "브랜드",
    "function": "기능",
    "main_protein": "주원료",
}


def _format_number(value):
    if value in [None, ""]:
        return ""

    try:
        if isinstance(value, bool):
            return str(value)
        return f"{int(value):,}"
    except Exception:
        return str(value)


def _format_sale_status(value):
    if value is True:
        return "판매중"
    if value is False:
        return "판매중지"

    lowered = str(value).lower()
    if lowered == "true":
        return "판매중"
    if lowered == "false":
        return "판매중지"

    return str(value or "")


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        product_detail_id = row.get("product_detail_id", "")
        product_id = row.get("product_id", "")

        rows.append(
            {
                "no": index,
                "product_display_id": (
                    f"{product_detail_id}-{product_id}"
                    if product_detail_id != "" and product_id != ""
                    else ""
                ),
                "type": row.get("type", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "function": row.get("function", ""),
                "main_protein": row.get("main_protein", ""),
                "life": row.get("life", ""),
                "weight": _format_number(row.get("weight", "")),
                "retail_price": _format_number(row.get("retail_price", "")),
                "quantity": _format_number(row.get("quantity", "")),
                "active": _format_sale_status(row.get("active", "")),
            }
        )

    return rows


@router.get(
    "/details",
    summary="상품 상세 정보 관리 목록 조회",
    description=(
        "상품관리 > 상품 상세 정보 관리 화면에서 사용하는 JOIN 기반 목록 조회 API입니다. "
        "OPD.product_detail 과 OPD.product 를 함께 조회하여 "
        "상품ID, 타입, 브랜드, 상품명, 기능, 주원료, 생애주기, 중량, 판매가, 수량, 판매상태를 반환합니다."
    ),
)
def get_product_detail_list(
    search_type: Literal[
        "product_name",
        "type",
        "brand",
        "function",
        "main_protein",
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

        result_items = build_response_rows(items, page, size)

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
                        "search_type_label": SEARCH_TYPE_LABELS.get(
                            clean_search_type, clean_search_type
                        ),
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
                    "search_type_label": SEARCH_TYPE_LABELS.get(
                        clean_search_type, clean_search_type
                    ),
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