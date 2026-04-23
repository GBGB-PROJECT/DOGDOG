from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionFeedingGuide, CompanionPet

# 추천 급여량 조회
def get_guide_intake(db: Session, pet_id: int):
    query = (
        select(CompanionFeedingGuide)
        .where(CompanionFeedingGuide.pet_id == pet_id)
    )

    result = db.execute(query).scalar_one_or_none()
    print("result:", result)

    return result

# 하루 급여 횟수 조회
def get_feeding_count(db: Session, pet_id: int):
    query = (
        select(CompanionPet.feeding_count)
        .where(CompanionPet.pet_id == pet_id)
    )

    result = db.execute(query)

    return result.scalar_one_or_none()