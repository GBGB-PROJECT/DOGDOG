from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from db.db import get_db
from dependencies import get_current_user

from app.subscriptions.subscriptions_schema import SubscriptionCreateRequest
from app.subscriptions.service.subscriptions_service import create_subscription_service

router = APIRouter(prefix="/api/v2/subscriptions", tags=["Subscriptions"])

# 구독 생성 ------------------------------------------------------------------------
@router.post("")
def create_subscription(
    customer_id: int,
    body: SubscriptionCreateRequest,
    db: Session = Depends(get_db),
):
# def create_subscription(
#     body: SubscriptionCreateRequest,
#     db: Session = Depends(get_db),
#     customer_id: int = Depends(get_current_user),
# ):
    return create_subscription_service(db, customer_id, body)