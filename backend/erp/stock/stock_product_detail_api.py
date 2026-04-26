# =========================================================
# 🔥 상품별 재고 상세 API
# - ERP.stock 중심 조회
# - 중량/수량/판매가/샘플/활성/상세ID/발주ID 제외
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .stock_product_detail_service import count_stocks, fetch_stocks

router = APIRouter(
    prefix="/erp/stock",
    tags=["stock"],
)

SEARCH_TYPE_LABELS = {
    "product_id": "상품ID",
    "brand": "브랜드",
    "product_name": "상품명",
    "inbound_id": "입고ID",
    "inbound_status": "입고상태",
    "save_stock": "보관재고",
    "sale_stock": "판매재고",
    "scrap_stock": "폐기재고",
    "stock_available": "가용재고",
    "expiration_date": "유통기한",
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


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "product_id": row.get("product_id", ""),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "expiration_date": row.get("expiration_date", ""),
                "inbound_id": row.get("inbound_id", ""),
                "inbound_status": row.get("inbound_status", ""),
                "save_stock": _format_number(row.get("save_stock", "")),
                "sale_stock": _format_number(row.get("sale_stock", "")),
                "stock_available": _format_number(row.get("stock_available", "")),
                "scrap_stock": _format_number(row.get("scrap_stock", "")),
                "last_update": row.get("last_update", ""),
            }
        )

    return rows


@router.get(
    "/product-detail",
    summary="상품별 재고 상세 목록 조회",
    description=(
        "재고관리 > 상품별 재고 상세 화면에서 사용하는 목록 조회 API입니다. "
        "ERP.stock을 중심으로 OPD.product, OPD.product_detail, ERP.inbound, ERP.inbound_status를 조인합니다. "
        "화면에서는 stock 중심 컬럼만 반환하며 중복 ID와 상품 판매 옵션 컬럼은 제외합니다."
    ),
)
def get_stock_product_detail_list(
    search_type: Literal[
        "product_id",
        "brand",
        "product_name",
        "inbound_id",
        "inbound_status",
        "save_stock",
        "sale_stock",
        "scrap_stock",
        "stock_available",
        "expiration_date",
    ] = Query(
        default="product_id",
        description="검색 조건",
        examples=["product_id"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["1"],
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
    start_date: date | None = Query(
        default=None,
        description="유통기한 시작일",
        examples=["2026-04-01"],
    ),
    end_date: date | None = Query(
        default=None,
        description="유통기한 종료일",
        examples=["2026-04-30"],
    ),
):
    try:
        clean_search_type = (search_type or "product_id").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_stocks(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_stocks(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
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
                        "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }

        return {
            "success": True,
            "message": "상품별 재고 상세 목록 조회에 성공했습니다.",
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
                    "start_date": start_date,
                    "end_date": end_date,
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
                "error_code": "STOCK_PRODUCT_DETAIL_LIST_FAILED",
                "message": f"상품별 재고 상세 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
