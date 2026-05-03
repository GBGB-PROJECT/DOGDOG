from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import (
    OpdProduct,
    OpdProductDetail,
    OpdSubs,
    OpdSubsItem,
    OpdSubsDetail,
    OpdPayment,
    OpdDelivery,
    OpdSubsPlan,
    OpdPaymentBilling,
    CompanionCustomerNotiSettings
)


def get_product(db: Session, product_id: int):
    query = (
        select(OpdProduct, OpdProductDetail.product_name)
        .join(OpdProductDetail, OpdProduct.product_detail_id == OpdProductDetail.product_detail_id)
        .where(OpdProduct.product_id == product_id, OpdProduct.active == True)
    )
    return db.execute(query).first()


def get_subs_plan(db: Session, delivery_cycle: int):
    return db.execute(
        select(OpdSubsPlan).where(OpdSubsPlan.delivery_cycle == delivery_cycle)
    ).scalar_one_or_none()


def get_payment_billing(db: Session, billing_id: int, customer_id: int):
    return db.execute(
        select(OpdPaymentBilling).where(
            OpdPaymentBilling.payment_billing_id == billing_id,
            OpdPaymentBilling.customer_id == customer_id
        )
    ).scalar_one_or_none()


def check_active_subscription(db: Session, customer_id: int):
    return db.execute(
        select(OpdSubs).where(
            OpdSubs.customer_id == customer_id,
            OpdSubs.is_subs_status == True
        )
    ).scalar_one_or_none()

# 내역 조회 -------------------------------------------------------------------------------------------------
# 이미 구독 중인 사료와 같은지 고려하기 **
def get_active_subscription_by_customer_id(db: Session, customer_id: int):
    query = (
        select(OpdSubs, OpdSubsPlan, OpdSubsDetail, OpdSubsItem)
        .join(
            OpdSubsPlan,
            OpdSubs.subs_plan_id == OpdSubsPlan.subs_plan_id
        )
        .outerjoin(
            OpdSubsDetail,
            OpdSubs.subs_id == OpdSubsDetail.subs_id
        )
        .outerjoin(
            OpdSubsItem,
            OpdSubs.subs_id == OpdSubsItem.subs_id
        )
        .where(
            OpdSubs.customer_id == customer_id,
            OpdSubs.is_subs_status == True
        )
    )

    result = db.execute(query)
    return result.first()



# 등록 ----------------------------------------------------------------------------------------------------------
def create_subs(db: Session, customer_id: int, subs_plan_id: int, is_auto_delivery: bool):
    subs = OpdSubs(
        customer_id=customer_id,
        subs_plan_id=subs_plan_id,
        is_auto_delivery=is_auto_delivery,
        is_subs_status=True
    )
    db.add(subs)
    db.flush()
    print("flush 후 subs_id:", subs.subs_id)
    return subs


def create_subs_detail(db: Session, subs_id: int, billing_id: int, body):
    detail = OpdSubsDetail(
        subs_id=subs_id,
        payment_billing_id=billing_id,
        address=body.address,
        detail_address=body.detail_address,
        postal_code=body.postal_code,
        memo=body.memo,
        name=body.recipient_name,
        phone=body.recipient_phone
    )
    db.add(detail)


def create_subs_item(db: Session, subs_id: int, product_id: int, quantity: int, retail_price: int, final_amount: int):
    item = OpdSubsItem(
        subs_id=subs_id,
        product_id=product_id,
        quantity=quantity,
        retail_price=retail_price,
        total_amount=retail_price * quantity,
        final_amount=final_amount
    )
    db.add(item)


def create_payment(db: Session, subs_id: int, amount: int):
    payment = OpdPayment(
        subs_id=subs_id,
        amount=amount,
        method="billing_key",
        is_cancel=False
    )
    db.add(payment)


def create_delivery(db: Session, subs_id: int):
    delivery = OpdDelivery(
        subs_id=subs_id
    )
    db.add(delivery)

def update_notification(db: Session, customer_id: int):
    """
    구독 생성 시 결제 알림(subs_payment)을 ON으로 변경 - 필수
    """
    setting = db.execute(
        select(CompanionCustomerNotiSettings).where(
            CompanionCustomerNotiSettings.customer_id == customer_id,
            CompanionCustomerNotiSettings.category == "subs_payment"
        )
    ).scalar_one_or_none()

    # 기존 설정 있으면 true로 변경
    if setting:
        setting.noti_option1=True
        setting.noti_option2=True
        return setting

    # 없으면 새로 생성 (선택)
    new_setting = CompanionCustomerNotiSettings(
        customer_id=customer_id,
        category="subs_payment",
        noti_option1=True,
        noti_option2=True
    )
    db.add(new_setting)
    return new_setting