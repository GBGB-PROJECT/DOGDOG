from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionCustomerFood, CompanionPetProductFeeding

from datetime import date, timedelta

# 현재 반려견이 먹고 있는 active=true 사료 조회 - PetProductFeeding 반환
def get_active_pet_food(db: Session, pet_id: int):
    query = (
        # select(CompanionPetProductFeeding.product_id)
        select(CompanionPetProductFeeding)
        .where(
            CompanionPetProductFeeding.pet_id == pet_id,
            CompanionPetProductFeeding.is_feeding_check == True
        )
    )
    result = db.execute(query)
    feeding_product = result.scalar_one_or_none() 
    return feeding_product

# 첫 사료 등록인지 확인을 위함
# 급여사료를 등록한적이 있는 = 기존 급여이력이 있는 반려견인지 조회
def get_pet_food(db: Session, pet_id: int):
    query = (
        select(CompanionPetProductFeeding)
        .where(CompanionPetProductFeeding.pet_id == pet_id)
    )
    result = db.execute(query)
    exist_pet_food = result.scalar_one_or_none()
    return exist_pet_food

# 기존 customer_food 등록자인지 확인
def get_customer_food_id(
    db: Session,
    pet_id: int,
):
    query = (
        select(CompanionCustomerFood)
        .where(CompanionCustomerFood.pet_id == pet_id)
    )

    result = db.execute(query)
    return result.scalar_one_or_none()

# ------------------------------ 삭제 ------------------------------
# 기존 활성 사료 종료 = 삭제
def deactivate_pet_food(db: Session, pet_food: CompanionPetProductFeeding, feeding_false_date):
    pet_food.is_feeding_check = False
    pet_food.feeding_false_date = feeding_false_date

    return pet_food

def end_pet_food(db: Session, pet_id: int):
    active_food = get_active_pet_food(db=db, pet_id=pet_id)
    if active_food is not None: # 급여중인 사료가 있다면
        deactive_food = deactivate_pet_food(
            db=db,
            pet_food=active_food,
            feeding_false_date=date.today()
        )
        return deactive_food
    
# 삭제 시 customer_food 테이블 비활성화? 잔여량 0으로 수정??? **************************************
    

# ------------------------------ 등록 ------------------------------
def insert_customer_food(
    db: Session,
    pet_id: int,
    total_weight: int
):
    customer_food = get_customer_food_id(db=db, pet_id=pet_id)
    if customer_food is None:
        customer_food = CompanionCustomerFood(
            pet_id=pet_id,
            total_weight=total_weight
            # feeding_start=f"{date.today()}"
        )
        db.add(customer_food)

    # 이미 급여한적이 있는 사용자의 경우 update total_weight
    else:
        customer_food.total_weight = total_weight
        customer_food.feeding_start = date.today()
        # customer_food.total_intake = 0
        # customer_food.left_intake = total_weight
    return customer_food

def insert_pet_product_feeding(
    db: Session,
    pet_id: int,
    product_id: int,
    one_gram_calories: float
):
    new_pet_food = get_pet_food(db=db, pet_id=pet_id) # 1: 신규 판별
    active_pet_food = get_active_pet_food(db=db, pet_id=pet_id)# 2: 활성사료 판별
    
    # 첫 사료등록인 경우 = pet_id에 대한 row가 존재 하지 않는 경우
    if new_pet_food is None:
        new_pet_food = CompanionPetProductFeeding(
            pet_id=pet_id,
            product_id=product_id,
            one_gram_calories=one_gram_calories,
        )
        db.add(new_pet_food)
        return new_pet_food
    
    # 존재하지만 비활성화인 경우
    elif new_pet_food.is_feeding_check == False:
        new_pet_food.is_feeding_check = True
        new_pet_food.product_id = product_id
        new_pet_food.one_gram_calories = one_gram_calories
        return new_pet_food
    
    # 이미 존재하는 경우
    else:
        # 변경하려는 사료가 기존 사료와 같은지 비교 --------------> 에러처리 필요
        if active_pet_food.product_id == product_id:
            raise ValueError("EXIST_PET_FOOD") 
        
        # 새 급여 사료 row 생성
        # false 처리 -> json으로 결과 넘기고 update
        deactivate_pet_food(
            db=db,
            pet_food=active_pet_food,
            feeding_false_date=date.today()
        )

        new_pet_food = CompanionPetProductFeeding(
            pet_id=pet_id,
            product_id=product_id,
            one_gram_calories=one_gram_calories,
        )
        db.add(new_pet_food)
        return new_pet_food
    
# ------------------------------ 수정 ------------------------------
# 수정 가능 날짜 조회
def get_pet_food_by_effective_date(
    db: Session,
    pet_id: int,
    effective_date: date
):
    query = (
        select(CompanionPetProductFeeding)
        .where(
            CompanionPetProductFeeding.pet_id == pet_id,
            CompanionPetProductFeeding.record_date <= effective_date,
            (
                (CompanionPetProductFeeding.feeding_false_date.is_(None)) |  # 급여중이거나
                (CompanionPetProductFeeding.feeding_false_date >= effective_date)  # 급여 종료 날짜 전을 수정할 때
            )
        )
        # .order_by(CompanionPetProductFeeding.record_date.desc()) # 내림차순
    )

    result = db.execute(query)
    return result.scalars().first()


def get_pet_foods_after_effective_date(
    db: Session,
    pet_id: int,
    effective_date: date
):
    query = (
        select(CompanionPetProductFeeding)
        .where(
            CompanionPetProductFeeding.pet_id == pet_id,
            CompanionPetProductFeeding.record_date > effective_date
        )
        .order_by(CompanionPetProductFeeding.record_date.asc())
    )

    result = db.execute(query)
    return result.scalars().all()

# 활성화된 급여 사료가 있을때
# 예전 기록 수정


# db 수정 ---------------------------------------------------
def update_pet_product_feeding(
    db: Session,
    pet_food: CompanionPetProductFeeding,
    product_id: int,
    one_gram_calories: float,
    effective_date: date,
):
    # 1) 기존 사료 종료 처리
    pet_food.is_feeding_check = False
    pet_food.feeding_false_date = effective_date

    # 중요: 트리거 로그 남기려면 여기서 DB에 한 번 반영
    db.flush()

    # 2) 같은 row를 새 사료 정보로 갱신
    pet_food.product_id = product_id
    pet_food.one_gram_calories = one_gram_calories
    pet_food.record_date = effective_date
    pet_food.feeding_false_date = None
    pet_food.is_feeding_check = True

    return pet_food


def update_customer_food_for_pet_food_change(
    db: Session,
    pet_id: int,
    total_weight: int,
    effective_date: date,
):
    customer_food = get_customer_food_id(db=db, pet_id=pet_id)

    if customer_food is None:
        customer_food = CompanionCustomerFood(
            pet_id=pet_id,
            total_weight=total_weight,
            feeding_start=effective_date,
            total_intake=0,
            food_count=0,
        )
        db.add(customer_food)
        return customer_food

    customer_food.total_weight = total_weight
    customer_food.feeding_start = effective_date
    customer_food.total_intake = 0
    customer_food.food_count = 0

    return customer_food