from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from db.db import get_db
from backend.dependencies import check_pet_owner, get_current_user
from backend.app.home.service.dashboard_service import DashboardService
from backend.app.home.repository.dashboard_repository import DashboardRepository
from backend.app.home.api.schemas import DashboardResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/home", tags=["Home Dashboard"])

@router.get("/dashboard/{pet_id}", response_model=DashboardResponse)
def get_daily_dashboard_summary(
    pet_id: int,
    query_date: Optional[date] = Query(None, alias="date", description="조회할 날짜 (기본값: 오늘)"),
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[조회] 앱 커스텀 홈 화면 대시보드의 '위젯' 구성을 위한 일일 요약 정보를 조회합니다."""
    repo = DashboardRepository(db)

    # 1. 소유권 검증 (dependencies.py 재사용)
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    # 2. 날짜 처리 (기본값 오늘)
    if not query_date:
        query_date = date.today()

    service = DashboardService(repo)
    
    try:
        # 데이터 조립 및 반환 (BFF 패턴: 합계 데이터에 집중)
        result = service.get_dashboard_summary(pet_id, query_date)
        return {"status": "success", "data": result}
    except ValueError as e:
        error_msg = str(e)
        if "찾을 수 없습니다" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
        )
    except Exception as e:
        logger.error(f"메인 대시보드 요약 조회 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
