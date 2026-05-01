from datetime import date
from sqlalchemy.orm import Session

from app.pets.repository.petFood_repository import (
    get_active_pet_food,
    insert_customer_food,
    insert_pet_product_feeding,
    get_product_detail_by_product_id,
    get_recommended_foods,
    get_recommended_foods_2,

    get_adult_stand_m,
    get_senior_stand_m
)

from dependencies import get_pet_by_id, check_pet_owner, get_product_by_id

# 등록 ---------------------------------------------------
def create_pet_food(
    db: Session,
    customer_id: int,
    pet_id: int,
    product_id: int | None,
    total_weight: int | None,
):
    """
    반려견의 현재 급여 사료를 등록한다.

    처리 순서:
    1. 입력값 검증
    2. pet 존재 확인
    3. 로그인 사용자 권한 확인
    4. product 존재 확인
    5. 기존 활성 사료 종료 처리
    6. 새 급여 사료 row 생성
    """
    # 1. 입력값 검증
    if product_id is None:
        raise ValueError("PRODUCT_ID_REQUIRED")

    if total_weight is None:
        raise ValueError("TOTAL_WEIGHT_REQUIRED")

    # if left_intake is None:
    #     raise ValueError("LEFT_INTAKE_REQUIRED")

    if total_weight <= 0:
        raise ValueError("INVALID_TOTAL_WEIGHT")


    # if left_intake < 0:
    #     raise ValueError("INVALID_LEFT_INTAKE")


    # 2. pet 존재 확인
    pet = get_pet_by_id(db=db, pet_id=pet_id)
    if pet is None:
        raise ValueError("PET_NOT_FOUND")

    # 3. 권한 확인
    has_access = check_pet_owner(
        db=db,
        pet_id=pet_id,
        customer_id=customer_id
    )
    if not has_access:
        raise ValueError("FORBIDDEN_PET_ACCESS")

    # 4. product 존재 확인
    product = get_product_by_id(db=db, product_id=product_id)
    if product is None:
        raise ValueError("PRODUCT_NOT_FOUND")

    if product.product_detail.calories is None:
        raise ValueError("PRODUCT_CALORIES_NOT_FOUND")
    
    # + total_weight <= product_weight 이 아닌 경우 에러처리
    if total_weight > product.weight:
        raise ValueError("HIGH_TOTAL_WEIGHT")
    
    pet_food = get_active_pet_food(db, pet_id)

    # 5. 기존 활성 사료 종료 처리
    # if pet_food is None
    # end_pet_food(db, pet_id)

    # 6. 새 사료 등록
    # 사료 등록
    new_PetProductFeeding = insert_pet_product_feeding(
        db=db,
        pet_id=pet_id,
        product_id=product_id,
        one_gram_calories=product.product_detail.calories
    )

    # 잔여량 등록
    new_CustomerFood = insert_customer_food(
        db=db,
        pet_id=pet_id,
        total_weight=total_weight
    )

    db.commit()
    db.refresh(new_CustomerFood)
    db.refresh(new_PetProductFeeding)

    # left_weight_g = total_weight - left_intake

    return {
        "pet_id": new_PetProductFeeding.pet_id,
        "product_id": new_PetProductFeeding.product_id,
        "product_name": product.product_detail.product_name,
        "total_weight_g": new_CustomerFood.total_weight,
        "one_gram_calories": new_PetProductFeeding.one_gram_calories,
        "is_feeding_check": new_PetProductFeeding.is_feeding_check,
        "record_date": str(new_PetProductFeeding.record_date)
    }

# 추천사료 조회 ----------------------------------------------------------------------
def read_recommended_foods(
    db: Session,
    customer_id: int,
    pet_id: int,
):
    # 1. pet_id 검증
    if pet_id <= 0:
        raise ValueError("INVALID_PET_ID")

    # 2. 반려견 존재 확인
    pet = get_pet_by_id(db=db, pet_id=pet_id)
    if pet is None:
        raise ValueError("PET_NOT_FOUND")

    # 3. 소유자 확인
    is_owner = check_pet_owner(
        db=db,
        pet_id=pet_id,
        customer_id=customer_id,
    )

    if not is_owner:
        raise ValueError("FORBIDDEN")

    # 4. 현재 급여 사료 조회
    current_food = get_active_pet_food(
        db=db,
        pet_id=pet_id,
    )

    if current_food is None:
        raise ValueError("CURRENT_FOOD_NOT_FOUND")

    # 5. 현재 사료 상세 정보 조회
    current_product_row = get_product_detail_by_product_id(
        db=db,
        product_id=current_food.product_id,
    )

    if current_product_row is None:
        raise ValueError("CURRENT_FOOD_NOT_FOUND")

    current_product, current_detail = current_product_row

    brand = current_detail.brand
    main_protein = current_detail.main_protein

    # life_stage 구하기
    # 생일 -> 개월수
    def calculate_age_months(birth_day: date) -> int:
        today = date.today()
        months = (today.year - birth_day.year) * 12 + (today.month - birth_day.month)

        # day 차이까지 반영하고 싶으면 추가 가능
        if today.day < birth_day.day:
            months -= 1

        return max(months, 0)
    
    age_m = calculate_age_months(pet.birth_day)

    adult_m = get_adult_stand_m(db=db, pet_id=pet_id)
    senior_m = get_senior_stand_m(db=db, pet_id=pet_id)

    life_stage = ''
    
    if age_m < adult_m:
        life_stage = "퍼피"
    elif age_m < senior_m:
        life_stage = "어덜트"
    else:
        life_stage = "시니어"

    print("생애주기:", life_stage)


    MAX_RECOMMEND_COUNT = 9

    recommended_foods_1 = get_recommended_foods(
        db=db,
        current_product_id=current_product.product_id,
        brand=brand,
        current_main_protein=main_protein,
        current_weight=current_product.weight,
        current_life_stage=life_stage
    )

    recommended_foods_2 = get_recommended_foods_2(
        db=db,
        current_product_id=current_product.product_id,
        current_main_protein=main_protein,
        current_weight=current_product.weight,
        current_life_stage=life_stage
    )

    merged_foods = []
    seen_product_ids = set()

    for row in recommended_foods_1 + recommended_foods_2:
        if row.product_id in seen_product_ids:
            continue

        # 중복 제거
        seen_product_ids.add(row.product_id)
        merged_foods.append(row)

        if len(merged_foods) >= MAX_RECOMMEND_COUNT:
            break

    return [
        {
            "product_id": row.product_id,
            "product_name": row.product_name,
            "brand": row.brand,
            "main_protein": row.main_protein,
            "life_stage": row.life,
            "weight": row.weight,
            "retail_price": row.retail_price,
            "thumbnail": row.thumbnail,
        }
        for row in merged_foods
    ]