from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionCustomerNotiSettings


def get_notification_settings_by_customer_id(db: Session, customer_id: int):
    query = (
        select(CompanionCustomerNotiSettings)
        .where(CompanionCustomerNotiSettings.customer_id == customer_id)
        .order_by(CompanionCustomerNotiSettings.customer_noti_settings_id)
    )

    result = db.execute(query)

    return result.scalars().all()