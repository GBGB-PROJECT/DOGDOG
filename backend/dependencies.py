from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import CompanionPet, CompanionButler, OpdProduct

# 존재하는 펫인지 확인
# 펫아이디 가져오기
def get_pet_by_id(db: Session, pet_id: int):
    query = (select(CompanionPet)
             .where(CompanionPet.pet_id == pet_id))
    result = db.execute(query)
    
    return result.scalar_one_or_none()

# 로그인 사용자가 해당 반려견의 보호자인지 확인
# Butler row 존재 여부 가져오기
def check_pet_owner(db: Session, pet_id: int, customer_id: int) -> bool:
    query = (
        select(CompanionButler)
        .where(
            CompanionButler.pet_id == pet_id,
            CompanionButler.customer_id == customer_id,
            CompanionButler.active == True
        )
    )
    result = db.execute(query)
    butler = result.scalar_one_or_none()
    return butler is not None  # T/F

# 존재하는 사료인지 확인
def get_product_by_id(db: Session, product_id: int):
    query = (select(OpdProduct)
             .where(OpdProduct.product_id == product_id))
    result = db.execute(query)
    return result.scalar_one_or_none()
