from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db 
from backend.erp.home.service.erp_home_service import DashboardService

router = APIRouter(prefix="/home/{account_id}", tags=['대시보드보기'])

@router.get("/highlight")
# 1. 주소창의 account_id를 받기 위해 파라미터 추가
# 2. 프론트엔드에서 target_year를 다시 입력받기 위해 파라미터 추가
def get_dashboard_highlight_api(account_id: str, target_year: int, db: Session = Depends(get_db)):
    """
    [대시보드 하이라이트 API]
    프론트엔드에서 account_id와 target_year를 넘겨주면, 
    해당 연도의 매출 현황을 돌려줍니다.
    """

    service = DashboardService(db)

    # 매니저(Service)에게 target_year를 다시 넘겨줍니다.
    status_code, text_code, message, data = service.get_dashboard_hightlight(target_year)

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
        "data": data
    }