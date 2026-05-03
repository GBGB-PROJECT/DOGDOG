# =========================================================
# 🔥 재고 입고/출고 관리 API
# - stock_inout_view.py에서 httpx 방식으로 호출
# - URL: GET /erp/stock/inout
# =========================================================

from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from .inout_service import get_stock_inout_list
from .inout_schema import ErpStockInoutListResponse


router = APIRouter(
    prefix="/erp/stock",
    tags=["stock"],
)


@router.get(
    "/inout",
    summary="재고 입고/출고 통합 조회",
    description=(
        "상품 재고 관리의 입고/출고 관리 화면에서 사용하는 API입니다. "
        "입고 내역과 출고 내역을 한 화면에서 조회합니다."
    ),
    response_model=ErpStockInoutListResponse,  # 🔥 추가: 재고 입고/출고 응답 Schema 연결
)
def get_stock_inout(
    search_type: Literal[
        "all",
        "inout_type",
        "inbound_id",
        "sales_order_id",
        "product",
        "status",
    ] = Query(
        default="all",
        description="검색조건. all=전체, inout_type=구분, inbound_id=입고ID, sales_order_id=주문ID, product=상품ID/브랜드/상품명/중량 통합 검색, status=상태",
    ),
    keyword: str = Query(default="", description="검색어"),
    inout_type: Literal["all", "inbound", "outbound", "입고", "출고"] = Query(
        default="all",
        description="입고/출고 구분",
    ),
    page: int = Query(default=1, ge=1, description="페이지 번호"),
    size: int = Query(default=50, ge=1, le=500, description="페이지 크기"),
    start_date: str | None = Query(default=None, description="조회 시작일"),
    end_date: str | None = Query(default=None, description="조회 종료일"),
):
    try:
        data = get_stock_inout_list(
            search_type=search_type,
            keyword=keyword,
            inout_type=inout_type,
            page=page,
            size=size,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "success": True,
            "message": "재고 입고/출고 통합 조회 성공",
            "data": data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"재고 입고/출고 통합 조회 실패: {exc}",
        )
