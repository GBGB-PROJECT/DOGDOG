from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from dependencies import get_current_user

from app.subscriptions.subscriptions_schema import SubscriptionCreateRequest
from app.subscriptions.service.subscriptions_service import *

router = APIRouter(prefix="/api/v1/subscriptions", tags=["Subscriptions"])

# 구독 내역 조회 ---------------------------------------------------------------------
@router.get("")
# def read_subscription(
#     customer_id: int,
#     db: Session = Depends(get_db),
# ):
def read_subscription(
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    try:
        result = read_subscription_service(
            db=db,
            customer_id=customer_id,
        )

        if result["is_subscribed"] is False:
            return {
                "success": True,
                "message": "활성 구독 내역이 없습니다.",
                "data": result,
            }

        return {
            "success": True,
            "message": "구독 내역 조회에 성공했습니다.",
            "data": result,
        }

    except Exception as e:
        print("구독 내역 조회 실패:", e)

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "서버 내부 오류가 발생했습니다.",
            },
        )

# 구독 생성 ------------------------------------------------------------------------
@router.post("")
# def create_subscription(
#     customer_id: int,
#     body: SubscriptionCreateRequest,
#     db: Session = Depends(get_db),
# ):
def create_subscription(
    body: SubscriptionCreateRequest,
    db: Session = Depends(get_db),
    customer_id: int = Depends(get_current_user),
):
    return create_subscription_service(db, customer_id, body)