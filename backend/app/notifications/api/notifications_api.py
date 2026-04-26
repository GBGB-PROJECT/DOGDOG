from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from dependencies import get_current_user
from app.notifications.service.notifications_service import read_notification_settings


router = APIRouter(prefix="/api/v2/notifications",tags=["notifications"])


# @router.get("/settings/{customer_id}")
@router.get("/settings")
def get_notification_settings(
    # customer_id: int,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    """
    로그인한 사용자의 알림 설정 정보를 조회한다.
    """
    try:
        settings = read_notification_settings(
            db=db,
            customer_id=customer_id,
        )

        if settings is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "NOTIFICATION_SETTING_NOT_FOUND",
                    "message": "알림 설정 정보가 존재하지 않습니다.",
                },
            )

        return {
            "success": True,
            "message": "알림 설정 조회에 성공했습니다.",
            "data": settings,
        }

    except Exception as e:
        print("알림 설정 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )