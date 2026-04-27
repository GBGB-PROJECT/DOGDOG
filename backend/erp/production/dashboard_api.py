# =========================================================
# 🔥 생산관리 메인 대시보드 API
# - 생산관리 메인 화면의 카드/차트/최근 발주 내역을 한 번에 조회
# =========================================================

from fastapi import APIRouter, HTTPException, Query

from .dashboard_service import fetch_production_dashboard


router = APIRouter(
    prefix="/erp/production/dashboard",
    tags=["production"],
)


@router.get(
    "",
    summary="생산관리 메인 대시보드 조회",
    description=(
        "생산관리 메인 대시보드에서 사용하는 최근 생산 입고 내역, 최근 불량 내역, "
        "월별 생산/불량 실적 차트, 최근 발주 카드 데이터를 반환합니다."
    ),
)
def get_production_dashboard(
    year: int | None = Query(
        default=None,
        description="조회 연도. 비우면 DB의 최신 입고완료 연도를 기준으로 조회합니다.",
        examples=[2026],
    ),
):
    try:
        data = fetch_production_dashboard(year=year)
        return {
            "success": True,
            "message": "생산관리 대시보드 조회에 성공했습니다.",
            "data": data,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "PRODUCTION_DASHBOARD_FAILED",
                "message": f"생산관리 대시보드 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
