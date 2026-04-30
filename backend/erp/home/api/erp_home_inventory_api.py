from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from erp.home.service.erp_home_inventory_service import InvenDashboardService

# [수정] API() -> APIRouter() 로 변경하고, 주소(prefix)를 설정합니다.
router = APIRouter(prefix="/erp/home", tags=['home_view'])

@router.get("/iventory_dashboard")
def get_inventory_highlight_api(account_id: str, db: Session = Depends(get_db)):
    """
    [생산/재고 하이라이트 API]
    프론트엔드에서 호출하면 세팅된 기간(3월/4월)의 
    입고량, 입고예정량, 총 재고량, 월평균 판매량 지표를 반환합니다.
    - `monthly_stock`: 3월 입고량(이번달을 3월로 기준으로 삼음)
    - `expected_inbound_stock`: 4월 입고예정량(다음달을 4월로 기준으로 삼음, DB에 4월 데이터가 없기 때문에 0을 응답)
    - `montly_available_stock`: 현재 총 재고량
    - `montly_avg_sales`: 월 평균 판매량
    - `feed_type_counts`:사료 타입별 개수
    """
    
    # 1. 매니저(Service) 배정
    service = InvenDashboardService(db)

    # 2. 매니저에게 재고 데이터 수집 지시 (파라미터 없음)
    status_code, text_code, message, data = service.get_invendashboard_highlight()

    # 3. 에러 발생 시 포장
    if status_code != 200:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "code": text_code,
                "msg": message
            }
        )
  
    # 4. 성공 시 정상 응답 포장 (200 OK)
    return {
        "success": True,
        "code": text_code, 
        "msg": message,
        "data": data
    }