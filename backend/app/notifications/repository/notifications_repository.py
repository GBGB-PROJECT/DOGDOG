from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionCustomerNotiSettings, OpdSubs


def get_notification_settings_by_customer_id(db: Session, customer_id: int):
    query = (
        select(CompanionCustomerNotiSettings)
        .where(CompanionCustomerNotiSettings.customer_id == customer_id)
        .order_by(CompanionCustomerNotiSettings.customer_noti_settings_id)
    )

    result = db.execute(query)

    return result.scalars().all()

# 수정 ------------------------------------------------------------------
# 구독자인지 확인
def is_active_subscriber(db: Session, customer_id: int) -> bool:
    query = (
        select(OpdSubs)
        .where(OpdSubs.customer_id == customer_id)
        .where(OpdSubs.is_subs_status == True)
    )

    result = db.execute(query)

    return result.scalar_one_or_none() is not None


# 해당 고객과 카테고리에 대응하는 rows 반환
def get_notification_setting_by_category(
    db: Session,
    customer_id: int,
    category: str
):
    query = (
        select(CompanionCustomerNotiSettings)
        .where(CompanionCustomerNotiSettings.customer_id == customer_id)
        .where(CompanionCustomerNotiSettings.category == category)
    )

    result = db.execute(query)

    return result.scalar_one_or_none()


# 수정
def update_notification_setting(
    db: Session,
    setting: CompanionCustomerNotiSettings,
    noti_option1: bool,
    noti_option2: bool
):
    setting.noti_option1 = noti_option1
    setting.noti_option2 = noti_option2

    db.add(setting)

    return setting