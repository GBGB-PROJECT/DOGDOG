from pydantic import BaseModel
from typing import Optional


class SubscriptionCreateRequest(BaseModel):
    product_id: int
    quantity: int
    delivery_cycle: Optional[int] = None
    is_auto_delivery: bool
    payment_option: str

    recipient_name: str
    recipient_phone: str
    address: str
    detail_address: str
    postal_code: str
    memo: Optional[str] = None

    used_point: Optional[int] = 0
    # coupon_id: Optional[int] = None