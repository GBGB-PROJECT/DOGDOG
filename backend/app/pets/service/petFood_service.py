from datetime import date
from sqlalchemy.orm import Session

from app.pets.repository.petFood_repository import (
    get_active_pet_food,
    insert_customer_food,
    insert_pet_product_feeding,
    get_pet_food_by_effective_date,
    close_pet_food_history,
    deactivate_future_pet_foods,
    update_same_day_pet_food,
    create_pet_food_history,
    upsert_customer_food_for_update,
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

# 수정 --------------------------------------------------
def update_pet_food(
    db: Session,
    customer_id: int,
    pet_id: int,
    effective_date: date,
    product_id: int | None,
    total_weight: int | None,
):
    """
    특정 날짜(effective_date)를 기준으로 급여 사료 정보를 수정한다.

    처리 순서:
    1. 입력값 검증
    2. pet 존재 확인
    3. 권한 확인
    4. product 존재 확인
    5. effective_date 기준 적용 중인 기존 이력 조회
    6. 같은 시작일이면 기존 row 직접 수정
    7. 중간 날짜면 기존 이력 종료 + 이후 이력 비활성화 + 새 row 생성
    8. customer_food 갱신
    """
    # 1. 입력값 검증
    if effective_date is None:
        raise ValueError("INVALID_DATE")

    if product_id is None:
        raise ValueError("PRODUCT_ID_REQUIRED")

    if total_weight is None:
        raise ValueError("TOTAL_WEIGHT_REQUIRED")

    if total_weight <= 0:
        raise ValueError("INVALID_TOTAL_WEIGHT")

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

    if total_weight > product.weight:
        raise ValueError("HIGH_TOTAL_WEIGHT")

    # 5. 기준 날짜에 적용 중인 기존 이력 조회
    target_food = get_pet_food_by_effective_date(
        db=db,
        pet_id=pet_id,
        effective_date=effective_date
    )

    if target_food is None:
        raise ValueError("NO_FEEDING_DATA")

    # 같은 날짜에 같은 상품으로 수정하려는 경우
    if target_food.record_date == effective_date and target_food.product_id == product_id:
        raise ValueError("EXIST_PET_FOOD")

    # 6. 기존 시작일과 동일하면 직접 수정
    if target_food.record_date == effective_date:
        updated_food = update_same_day_pet_food(
            pet_food=target_food,
            product_id=product_id,
            one_gram_calories=product.product_detail.calories
        )

        deactivate_future_pet_foods(
            db=db,
            pet_id=pet_id,
            effective_date=effective_date
        )

        customer_food = upsert_customer_food_for_update(
            db=db,
            pet_id=pet_id,
            total_weight=total_weight,
            effective_date=effective_date
        )

        db.commit()
        db.refresh(updated_food)
        db.refresh(customer_food)

        return {
            "pet_id": updated_food.pet_id,
            "product_id": updated_food.product_id,
            "product_name": product.product_detail.product_name,
            "total_weight_g": customer_food.total_weight,
            "one_gram_calories": updated_food.one_gram_calories,
            "is_feeding_check": updated_food.is_feeding_check,
            "record_date": str(updated_food.record_date),
            "feeding_false_date": (
                str(updated_food.feeding_false_date)
                if updated_food.feeding_false_date else None
            )
        }

    # 7. 중간 날짜 수정이면 기존 이력 종료
    close_pet_food_history(
        pet_food=target_food,
        effective_date=effective_date
    )

    # 8. 기준일 이후 기존 이력 비활성화
    deactivate_future_pet_foods(
        db=db,
        pet_id=pet_id,
        effective_date=effective_date
    )

    # 9. 새 이력 생성
    new_food = create_pet_food_history(
        db=db,
        pet_id=pet_id,
        product_id=product_id,
        one_gram_calories=product.product_detail.calories,
        effective_date=effective_date
    )

    # 10. customer_food 갱신
    customer_food = upsert_customer_food_for_update(
        db=db,
        pet_id=pet_id,
        total_weight=total_weight,
        effective_date=effective_date
    )

    db.commit()
    db.refresh(new_food)
    db.refresh(customer_food)

    return {
        "pet_id": new_food.pet_id,
        "product_id": new_food.product_id,
        "product_name": product.product_detail.product_name,
        "total_weight_g": customer_food.total_weight,
        "one_gram_calories": new_food.one_gram_calories,
        "is_feeding_check": new_food.is_feeding_check,
        "record_date": str(new_food.record_date),
        "feeding_false_date": (
            str(new_food.feeding_false_date)
            if new_food.feeding_false_date else None
        )
    }