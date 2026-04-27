from datetime import date
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db.models import (
    CompanionCustomerNotiSettings,
    CompanionPet,
    CompanionButler,
    CompanionCustomerFood,
    CompanionPetProductFeeding,
    OpdProduct,
    OpdProductDetail,
    OpdSubs,
    OpdSubsItem,
    OpdDelivery,
)

# 한 사용자에 대한 모든 알림설정 내용 - 구독 배달/결제, 소진일 알림
def get_notification_settings(db: Session, customer_id: int):
    query = (
        select(CompanionCustomerNotiSettings)
        .where(CompanionCustomerNotiSettings.customer_id == customer_id)
    )
    return db.execute(query).scalars().all()

# 사용자가 기르는 pet_id
def get_customer_pet_ids(db: Session, customer_id: int):
    query = (
        select(CompanionButler.pet_id)
        .where(CompanionButler.customer_id == customer_id)
    )
    return db.execute(query).scalars().all()

# 반려견과 급여중인 사료의 예상 잔여일
def get_expected_exdate(db: Session, pet_id: int):
    query = (
        select(
            CompanionPet.nickname.label("nickname"),
            CompanionCustomerFood.expected_exdate.label("expected_exdate"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),
        )
        # 기준 테이블: customer_food
        .select_from(CompanionCustomerFood)
        # pet 연결
        .join(
            CompanionPet,
            CompanionCustomerFood.pet_id == CompanionPet.pet_id
        )
        # 현재 급여 중인 사료 연결
        .join(
            CompanionPetProductFeeding,
            CompanionCustomerFood.pet_id == CompanionPetProductFeeding.pet_id
        )
        # 상품 연결
        .join(
            OpdProduct,
            CompanionPetProductFeeding.product_id == OpdProduct.product_id
        )
        # 상품 상세 연결
        .join(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id
        )
        # 조건
        .where(
            CompanionCustomerFood.pet_id == pet_id,
            CompanionPetProductFeeding.is_feeding_check == True,
        )
    )

    return db.execute(query).first()


# 구독중인 사용자의 상품 준비시작일, 상품 출고일
def get_active_subscription_items(db: Session, customer_id: int):
    query = (
        select(
            OpdSubs.subs_id.label("subs_id"),
            OpdDelivery.delivery_date.label("delivery_date"),
            OpdDelivery.order_start_date.label("order_start_date"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),
        )
        .join(
            OpdSubsItem,
            OpdSubs.subs_id == OpdSubsItem.subs_id
        )
        .join(
            OpdProduct,
            OpdSubsItem.product_id == OpdProduct.product_id
        )
        .join(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id
        )
        .join(
            OpdDelivery,
            OpdSubs.subs_id == OpdDelivery.subs_id
        )
        .where(OpdSubs.customer_id == customer_id)
        .where(OpdSubs.is_subs_status == True)
    )

    return db.execute(query).all()