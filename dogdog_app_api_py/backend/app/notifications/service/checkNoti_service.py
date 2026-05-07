from datetime import date
from sqlalchemy.orm import Session

from backend.app.notifications.repository.checkNoti_repository import (
    get_notification_settings,
    get_customer_pet_ids,
    get_expected_exdate,
    get_active_subscription_items,
)
from backend.app.notifications.repository.notifications_repository import is_active_subscriber

def _days_until(target_date):
    if target_date is None:
        return None

    if hasattr(target_date, "date"):
        target_date = target_date.date()

    return (target_date - date.today()).days


def _is_option_on(setting, days_before: int):
    if days_before == 3:
        return setting.noti_option1 is True

    if days_before == 7:
        return setting.noti_option2 is True

    return False


def check_notifications(db: Session, customer_id: int):
    notifications = []

    settings = get_notification_settings(db=db, customer_id=customer_id)
    subscribe_user = is_active_subscriber(db=db, customer_id=customer_id)

    setting_map = {
        setting.category: setting
        for setting in settings
    }

    # 1. 사료 소진 알림
    food_setting = setting_map.get("left_feeding_day")

    # 2. 구독 배송/결제 알림
    subs_d_setting = setting_map.get("subs_delivery")
    subs_p_setting = setting_map.get("subs_payment")

    # 구독자가 아닐 때 -------------------------------------------------------------
    if subscribe_user == False:
        if food_setting:
            pet_ids = get_customer_pet_ids(db=db, customer_id=customer_id)

            for pet_id in pet_ids:
                pet_food_info = get_expected_exdate(db=db, pet_id=pet_id)

                if pet_food_info is None:
                    continue
                # 해당 반려견의 급여중인 사료가 있을 때

                left_exdate = _days_until(pet_food_info.expected_exdate)

                if left_exdate in [3, 7] and _is_option_on(food_setting, left_exdate):
                    notifications.append({
                        "category": "FOOD_DEPLETION",
                        "notification_type": "FOOD_DEPLETION",
                        "title": "사료 소진 알림",
                        "message": f'🍚 "{pet_food_info.nickname}"의 급여 중인 사료가 {left_exdate}일치 남았습니다.\n 지금 바로 사료를 구매하세요.',
                        "days_before": left_exdate,
                    })
                    


    # 구독자일 때 --------------------------------------------------------------------
    else:
        if food_setting:
            pet_ids = get_customer_pet_ids(db=db, customer_id=customer_id)

            for pet_id in pet_ids:
                pet_food_info = get_expected_exdate(db=db, pet_id=pet_id)

                if pet_food_info is None:
                    continue
                # 해당 반려견의 급여중인 사료가 있을 때

                left_exdate = _days_until(pet_food_info.expected_exdate)

                if left_exdate in [3, 7] and _is_option_on(food_setting, left_exdate):
                    notifications.append({
                        "category": "FOOD_DEPLETION",
                        "notification_type": "FOOD_DEPLETION",
                        "title": "사료 소진 알림",
                        "message": f'🍚 "{pet_food_info.nickname}"의 급여 중인 사료가 {left_exdate}일치 남았습니다.',
                        "days_before": left_exdate,
                    })
                    # print(notifications[0]["message"])


        # 구독중인 사용자의 상품 준비시작일, 상품 출고일
        subs_items = get_active_subscription_items( 
            db=db,
            customer_id=customer_id,
        )

        for item in subs_items:
            product_text = f"{item.product_name} {item.weight}g"

            # 배송 예정일 기준 알림 ------------------------------------------------
            # 오늘로부터 배송 예정일까지 남은 날
            delivery_days = _days_until(item.delivery_date)

            if delivery_days in [3, 7] and _is_option_on(subs_d_setting, delivery_days):
                notifications.append({
                    "category": "SUBSCRIPTION_DELIVERY",
                    "notification_type": "DELIVERY",
                    "title": "구독 배송 알림",
                    "message": f"📦{delivery_days}일 뒤 \"{product_text}\"이 배송됩니다.",
                    "days_before": delivery_days,
                })

            # 자동 결제 예정일 기준 알림 -------------------------------------------
            # 오늘로부터 자동 결제 예정일까지 남은 날
            payment_days = _days_until(item.order_start_date)

            if payment_days in [3, 7] and _is_option_on(subs_p_setting, payment_days):
                notifications.append({
                    "category": "SUBSCRIPTION_DELIVERY",
                    "notification_type": "PAYMENT",
                    "title": "구독 결제 알림",
                    "message": f"💰{payment_days}일 뒤 \"{product_text}\"이 자동 결제됩니다.",
                    "days_before": payment_days,
                })

    return notifications