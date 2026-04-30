from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import Optional

# 실제 프로젝트 경로에 맞게 임포트 수정
from db.db import get_db  # DB 세션을 가져오는 함수 
from erp.home.service.erp_home_chart_service import DashboardService

# 라우터 설정
router = APIRouter(
    prefix="/erp/home",
    tags=["home_view"]
)

@router.get("/chart_dashboard_summary")
def get_dashboard_summary(
    db: Session = Depends(get_db)
):
    """
    개밥개밥 ERP 대시보드 상단의 요약 지표(매출, 판매량, 성장률)를 반환합니다.
    """
    service = DashboardService(db)

    # 데이터 수집
    status_code, text_code, message, data = service.get_summary_metrics()

    # 에러 발생 시 포장
    if status_code != 200:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": text_code,
                "msg": message,
                "data": None
            }
        )
    return {
        "success": True,
        "code": text_code, 
        "msg": message,
        "data": data
    }

@router.get("/chart_dashboard_sale")
def get_dashboard_chart(
    period: str = Query("1주일", description="조회 기간 (1주일, 1개월, 1년)중 택 1"),
    db: Session = Depends(get_db)
):
    """
    [매출 차트 통계 API]
    요청받은 기간에 맞춰 차트 렌더링을 위한 매출액 및 판매량 데이터를 반환합니다.
    """
    service = DashboardService(db)
    
    status_code, text_code, message, data = service.get_chart_statistics(period)

    if status_code != 200:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": text_code,
                "msg": message,
                "data": None
            }
        )
    return {
        "success": True,
        "code": text_code, 
        "msg": message,
        "data": data
    }