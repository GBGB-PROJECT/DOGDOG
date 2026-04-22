from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from db.models import (
    CompanionPet,
    # CompanionButler,
    # CompanionPetFood,
    CompanionPetLogNumeric,
    CompanionPetProductFeeding,
    CompanionBreed,
    CompanionLifeStage,
    # OpdFood,
    CompanionFeedingGuide,
)

from datetime import date

'''
guide_feeding = predict_recommend_g(
    age = 23,
    neutered = 1,
    weight = 7.5 ,
    bcs = 6,
    activity_level = 2,
    season = 1,  #
    fcs = 3,
    adult_stand_m = 13,  #
    food_kcal = 4.005
)
'''

# 계산을 위한 feature 받기
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from db.models import (
    CompanionPet,
    CompanionPetLogNumeric,
    CompanionPetProductFeeding,
)


# 계산을 위한 feature 받기
def get_cal_features(db: Session, pet_id: int):
    query = (
        select(
            CompanionPet.birth_day,                     # age -> 후처리
            CompanionPet.is_neutered,                  # neutered
            CompanionPet.weight,                       # weight
            CompanionPet.bcs,                          # bcs
            CompanionPet.daily_walks,                  # activity_level
            CompanionPetLogNumeric.log_status.label("fcs"), # fcs
            CompanionPetProductFeeding.one_gram_calories.label("food_kcal")  # food_kcal
        )
        .select_from(CompanionPet)
        .join(
            CompanionPetProductFeeding,
            CompanionPet.pet_id == CompanionPetProductFeeding.pet_id
        )
        .outerjoin(
            CompanionPetLogNumeric,
            (CompanionPet.pet_id == CompanionPetLogNumeric.pet_id)
            & (CompanionPetLogNumeric.category == "poop")
        )
        .where(CompanionPet.pet_id == pet_id)
        .order_by(desc(CompanionPetLogNumeric.log_date))
    )

    row = db.execute(query).first()

    if row is None:
        return None

    return {
        "birth_day": row.birth_day,
        "is_neutered": row.is_neutered,
        "weight": row.weight,
        "bcs": row.bcs,
        "daily_walks": row.daily_walks,
        "fcs": row.fcs,
        "food_kcal": row.food_kcal,
    }

# adult_stand_m 받기
def get_adult_stand_m(db: Session, pet_id: int):
    query = (
        select(CompanionLifeStage.life_start)
        .select_from(CompanionPet)
        .join(
            CompanionBreed,
            CompanionPet.breed_id == CompanionBreed.breed_id
        )
        .join(
            CompanionLifeStage,
            CompanionBreed.breed_size == CompanionLifeStage.breed_size
        )
        .where(
            CompanionPet.pet_id == pet_id,
            CompanionLifeStage.life == "어덜트" 
        )
    )

    result = db.execute(query).scalar_one_or_none()
    return result

# feeding_count
def get_feeding_count(db: Session, pet_id: int):
    query = (
        select(
            CompanionPet.feeding_count
        )
        .where(
            CompanionPet.pet_id == pet_id
        )
    )
    result = db.execute(query).scalar_one_or_none()
    return result

# 등록
def create_feeding_recommendation(
    db: Session,
    pet_id: int,
    base_intake: float,
    guide_intake: float,
):
    recommendation = db.get(CompanionFeedingGuide, pet_id)

    if recommendation is None:
        recommendation = CompanionFeedingGuide(
            pet_id=pet_id,
            base_intake=int(round(base_intake)),
            guide_intake=int(round(guide_intake)),
        )
        db.add(recommendation)
    else:
        recommendation.base_intake = int(round(base_intake))
        recommendation.guide_intake = int(round(guide_intake))
        recommendation.guide_date=date.today()

    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation