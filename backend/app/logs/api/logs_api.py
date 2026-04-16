from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from db.db import get_db
from dependencies import check_pet_owner
from app.logs.service.logs_service import LogsService
from app.logs.repository.logs_repository import LogsRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/logs", tags=["Logs"])

@router.get("/{pet_id}")
def get_unified_timeline_logs(
    pet_id: int,
    query_date: Optional[date] = Query(None, alias="date", description="조회할 날짜 (기본값: 오늘)"),
    category: Optional[str] = Query(None, description="분류별 조회용 ('all', 'feeding', 'poop', 'water' 등)"),
    db: Session = Depends(get_db),
):
    """[조회] 타임라인 방식의 상세 기록 리스트(급여, 배변, 음수 등)를 통합하여 시간 역순으로 제공합니다."""
    customer_id = 1  # TODO: JWT 연동
    repo = LogsRepository(db)

    # 1. 소유권 검증
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    if not query_date:
        query_date = date.today()

    service = LogsService(repo)

    try:
        # 데이터 조립 및 병합
        result = service.get_unified_logs(pet_id, query_date, category)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"통합 로그 타임라인 조회 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
