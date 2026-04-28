# =========================================================
# 🔥 재고 현황 대시보드 API
# - stock_status_view.py에서 httpx 방식으로 호출
# - URL: GET /erp/stock/dashboard
# =========================================================

from fastapi import APIRouter, HTTPException, Query

from .dashboard_service import fetch_stock_dashboard


router = APIRouter(
    prefix="/erp/stock",
    tags=["stock"],
)


@router.get(
    "/dashboard",
    summary="재고 현황 대시보드 조회",
    description=(
        "재고 현황 화면에서 사용하는 대시보드 조회 API입니다. "
        "선택한 연월 기준으로 입고, 출고, 입출고 차트, 매출 TOP 3 재고 데이터를 반환합니다."
    ),
)
def get_stock_dashboard(
    year: int | None = Query(
        default=None,
        description="조회 연도",
        examples=[2026],
    ),
    month: int | None = Query(
        default=None,
        ge=1,
        le=12,
        description="조회 월",
        examples=[4],
    ),
):
    try:
        dashboard_data = fetch_stock_dashboard(
            year=year,
            month=month,
        )

        return {
            "success": True,
            "message": "재고 현황 대시보드 조회 성공",
            "data": dashboard_data,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"재고 현황 대시보드 조회 실패: {exc}",
        )
