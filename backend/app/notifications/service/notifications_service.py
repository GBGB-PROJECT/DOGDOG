from sqlalchemy.orm import Session

from app.notifications.repository.notifications_repository import (
    get_notification_settings_by_customer_id,
    get_notification_setting_by_category,
    update_notification_setting,
    is_active_subscriber
)

# 조회 ----------------------------------------------------

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

# 수정 -----------------------------------------------------------
# ["subs_delivery", "subs_payment", "left_feeding_day"]
VALID_CATEGORIES = ["subs_delivery", "left_feeding_day"]

CATEGORY_NAME_MAP = {
    "subs_delivery": "구독 배송",
    "left_feeding_day": "사료 소진일",
}

def modify_notification_setting(
    db: Session,
    customer_id: int,
    category: str,
    noti_option1: bool,
    noti_option2: bool,
):
    if category not in VALID_CATEGORIES:
        return "INVALID_CATEGORY"
    
    if category == "left_feeding_day":
        if noti_option1 != noti_option2:
            return "INVALID_FOOD_DEPLETION_OPTION"
        
    if category == "subs_delivery":
        if not is_active_subscriber(db=db, customer_id=customer_id) is True:
            return "SUBSCRIPTION_REQUIRED"

    setting = get_notification_setting_by_category(
        db=db,
        customer_id=customer_id,
        category=category,
    )

    if setting is None:
        return None

    updated_setting = update_notification_setting(
        db=db,
        setting=setting,
        noti_option1=noti_option1,
        noti_option2=noti_option2,
    )

    return {
        "category": updated_setting.category,
        "category_name": CATEGORY_NAME_MAP.get(updated_setting.category),
        "noti_before_3days": updated_setting.noti_option1,
        "noti_before_7days": updated_setting.noti_option2,
    }