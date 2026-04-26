from sqlalchemy.orm import Session

from app.notifications.repository.notifications_repository import (
    get_notification_settings_by_customer_id,
)

# ["subs_delivery", "subs_payment", "food_exdate"]
# CATEGORY_NAME_MAP = {
#     "subs_delivery": "구독 배송",
#     "subs_payment": "구독 결제",
#     "food_exdate": "사료 소진일",
# }

CATEGORY_NAME_MAP = {
    "subs_delivery": "구독 배송",
    "left_feeding_day": "사료 소진일",
}


def read_notification_settings(db: Session, customer_id: int):
    settings = get_notification_settings_by_customer_id( # rows
        db=db,
        customer_id=customer_id,
    )

    if not settings:
        return None

    data = []

    for setting in settings:
        data.append({
            "category": setting.category,
            "category_name": CATEGORY_NAME_MAP.get(setting.category),
            "noti_before_3days": setting.noti_option1,
            "noti_before_7days": setting.noti_option2,
        })

    return data