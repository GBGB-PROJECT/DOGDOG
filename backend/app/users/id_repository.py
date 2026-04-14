from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionCustomer, CompanionPet


def get_customer_by_id(db: Session, customer_id: int):
    """
    customer_id로 사용자 조회
    """
    return (
        db.excute(
            CompanionCustomer.customer_id
        )
    )


def get_pet_id(db: Session, customer_id: int):
    """
    customer_id로 반려견 1건 조회
    """
    return (
        db.query(Pet)
        .filter(Pet.customer_id == customer_id)
        .first()
    )

# ac: 변수로 저장됌 빨리 만료되기때문
# rf: 쿠키세션에 저장