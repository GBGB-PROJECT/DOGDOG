from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from dependencies import get_current_user
from app.notifications.service.notifications_service import read_notification_settings

from app.notifications.notification_schema import NotificationSettingUpdateRequest
from app.notifications.service.notifications_service import modify_notification_setting

from app.notifications.service.checkNoti_service import check_notifications


router = APIRouter(prefix="/api/v1/notifications",tags=["notifications"])

# 알림 체크 --------------------------------------------------------
# @router.get("/check/{customer_id}")
# def get_notification_check(
#     customer_id: int,
#     db: Session = Depends(get_db),
# ): 
@router.get("/check")
def get_notification_check(
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    try:
        data = check_notifications(
            db=db,
            customer_id=customer_id,
        )

        if not data:
            return {
                "success": True,
                "message": "표시할 알림이 없습니다.",
                "data": [],
            }

        return {
            "success": True,
            "message": "알림 체크에 성공했습니다.",
            "data": data,
        }

    except Exception as e:
        print("알림 체크 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )


# 조회 -------------------------------------------------------------
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
    
# 수정 -------------------------------------------------------------
# @router.patch("/settings/{customer_id}")
# def patch_notification_setting(
#     customer_id: int,
#     body: NotificationSettingUpdateRequest,
#     db: Session = Depends(get_db),
# ):
@router.patch("/settings")
def patch_notification_setting(
    body: NotificationSettingUpdateRequest,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    """
    로그인한 사용자의 알림 설정을 수정한다.
    Swagger 테스트용으로 customer_id를 path parameter로 받는다.
    """
    try:
        result = modify_notification_setting(
            db=db,
            customer_id=customer_id,
            category=body.category,
            noti_option1=body.noti_option1,
            noti_option2=body.noti_option2,
        )

        if result == "INVALID_CATEGORY":
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_CATEGORY",
                    "message": "유효하지 않은 알림 카테고리입니다.",
                },
            )
        
        if result == "INVALID_FOOD_DEPLETION_OPTION":
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error_code": "INVALID_FOOD_DEPLETION_OPTION",
                    "message": "사료 소진 알림은 3일/7일 설정이 동일해야 합니다.",
                },
            )
        
        if result == "SUBSCRIPTION_REQUIRED":
            return JSONResponse(
                status_code=403,
                content={
                    "success": False,
                    "error_code": "SUBSCRIPTION_REQUIRED",
                    "message": "구독 중인 사용자만 구독 관련 알림 설정을 수정할 수 있습니다.",
                },
            )

        if result is None:
            return JSONResponse(
                status_code=404,
                content={
                    "success": False,
                    "error_code": "NOTIFICATION_SETTING_NOT_FOUND",
                    "message": "알림 설정 정보가 존재하지 않습니다.",
                },
            )

        db.commit()

        return {
            "success": True,
            "message": "알림 설정이 수정되었습니다.",
            "data": result,
        }

    except Exception as e:
        db.rollback()
        print("알림 설정 수정 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )