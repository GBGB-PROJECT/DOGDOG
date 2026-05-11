from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from db.db import get_db
from backend.dependencies import check_pet_owner, get_current_user, verify_pet_owner
from backend.app.logs.service.logs_service import LogsService
from backend.app.logs.repository.logs_repository import LogsRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])

@router.get("/{pet_id}")
def get_unified_timeline_logs(
    pet_id: int = Depends(verify_pet_owner),
    query_date: Optional[date] = Query(None, alias="date", description="조회할 날짜 (단일)"),
    start_date: Optional[date] = Query(None, description="조회 시작 날짜"),
    end_date: Optional[date] = Query(None, description="조회 종료 날짜"),
    category: Optional[str] = Query(None, description="분류별 조회용 ('all', 'feeding', 'poop', 'water' 등)"),
    db: Session = Depends(get_db),
):
    """[조회] 타임라인 방식의 상세 기록 리스트를 통합하여 제공합니다. (단일 날짜 또는 기간 조회 가능)"""
    repo = LogsRepository(db)

    service = LogsService(repo)

    try:
        # [해결] 기간 정보가 있으면 기간 검색, 없으면 단일 날짜(기본값: 오늘) 검색
        if start_date and end_date:
            result = service.get_unified_logs(pet_id, category=category, start_date=start_date, end_date=end_date)
        else:
            if not query_date:
                query_date = date.today()
            result = service.get_unified_logs(pet_id, target_date=query_date, category=category)
            
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"통합 로그 타임라인 조회 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
