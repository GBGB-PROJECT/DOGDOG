from sqlalchemy import select
from sqlalchemy.orm import Session
from pydantic import EmailStr

from db.models import CompanionCustomerDetail, CompanionButler


# 이메일로 사용자정보 가져오지만 추후 토큰으로 가져올 예정
def get_customer_by_id(db: Session, email: EmailStr):
    """
    email로 customer_id 조회
    """
    result = db.execute(
        select(CompanionCustomerDetail.customer_id)
        .where(CompanionCustomerDetail.email == email)
    ).first()

    return result[0] if result else None

def get_pet_id(db: Session, customer_id: int):
    """
    customer_id로 반려견 1건 조회
    """
    query = (
        select(CompanionButler.pet_id)
        .where(CompanionButler.customer_id == customer_id)
    )
    result = db.execute(query)
    dogs = result.scalars().all()

    return dogs