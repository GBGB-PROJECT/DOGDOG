from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db 
from erp.home.service.erp_home_service import DashboardService

router = APIRouter(prefix="/erp/home", tags=['home_view'])

@router.get("/sale_dashboard")
def get_dashboard_highlight_api(db: Session = Depends(get_db)):
    """
    [대시보드 하이라이트 API]
    프론트엔드에서 account_id와 target_year를 넘겨주면, 
    해당 연도의 전체적인 매출 요약 지표 및 월간/주간 달성률을 반환합니다.

    **반환 데이터(data) 상세 내역:**
    - `total_amount` (int): 해당 연도 총 매출액
    - `total_qty` (int): 해당 연도 총 판매 수량
    - `last_year_amount` (int): 전년도 총 매출액
    - `growth_rate` (float): 전년 대비 성장률 (%)
    - `target_achievement_rate` (float): 연간 목표 대비 달성률 (%)
    - `yearly_target_amount` (int): 연간 목표 매출액
    - `monthly_amount` (int): 기준 월(3월) 총 매출액
    - `monthly_target` (int): 월간 목표 매출액
    - `monthly_achievement_rate` (float): 월간 목표 대비 달성률 (%)
    - `weekly_amount` (int): 기준 주차 총 매출액
    - `weekly_target` (int): 주간 목표 매출액
    - `weekly_achievement_rate` (float): 주간 목표 대비 달성률 (%)
    """

    service = DashboardService(db)

    status_code, text_code, message, data = service.get_dashboard_hightlight()

    ## 최종 포장
    if status_code != 200:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": text_code,
                "msg": message
            }
        )

    # 모든 검증 통과 (200 OK)
    return {
        "success": True,
        "code": text_code, 
        "msg": message,
        "data": data # 새롭게 추가된 월/주간 퍼센트 값들이 모두 포함되어 전달됩니다!
    }