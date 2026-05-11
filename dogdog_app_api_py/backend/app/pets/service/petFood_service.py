from datetime import date
from sqlalchemy.orm import Session

from backend.app.pets.repository.petFood_repository import (
    get_active_pet_food,
    insert_customer_food,
    insert_pet_product_feeding,
    get_pet_food_by_effective_date,
    update_pet_product_feeding,
    update_customer_food_for_pet_food_change,
    get_product_detail_by_product_id,
    get_recommended_foods,
    get_recommended_foods_2,

    get_adult_stand_m,
    get_senior_stand_m
)


from backend.dependencies import get_pet_by_id, check_pet_owner, get_product_by_id


# 등록 ---------------------------------------------------
def create_pet_food(
    db: Session,
    customer_id: int,
    pet_id: int,
    product_id: int | None,
    total_weight: int | None,
    commit: bool = True,
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
    has_access = check_pet_owner(db=db, pet_id=pet_id, customer_id=customer_id)
    if not has_access:
        raise ValueError("FORBIDDEN_PET_ACCESS")

    # 4. product 존재 확인
    product = get_product_by_id(db=db, product_id=product_id)
    if product is None:
        raise ValueError(f"존재하지 않는 사료 ID입니다. (ID: {product_id})")

    if not product.product_detail:
        raise ValueError(f"사료 상세 정보(ProductDetail)를 찾을 수 없습니다. (ID: {product_id})")

    if product.product_detail.calories is None:
        raise ValueError(f"사료의 칼로리 정보가 등록되어 있지 않습니다. (ID: {product_id})")

    # + total_weight <= product_weight 이 아닌 경우 에러처리
    if total_weight > product.weight:
        raise ValueError(f"입력하신 용량({total_weight}g)이 제품의 원래 중량({product.weight}g)보다 큽니다.")

    pet_food = get_active_pet_food(db, pet_id)

    # 5. 기존 활성 사료 종료 처리
    # if pet_food is None
    # end_pet_food(db, pet_id)

    # 6. 새 사료 등록 프로세스 (트랜잭션 관리 강화)
    try:
        # 6-1. 사료 영양 정보 등록 (AI 계산을 위한 기초 데이터)
        new_PetProductFeeding = insert_pet_product_feeding(
            db=db,
            pet_id=pet_id,
            product_id=product_id,
            one_gram_calories=product.product_detail.calories,
        )
        
        if new_PetProductFeeding is None:
             raise ValueError("사료 급여 정보(PetProductFeeding) 생성에 실패했습니다.")

        db.flush()  # 영양 정보가 세션에 반영되어야 AI 추천 로직이 정상 작동함

        # 7. AI 권장 급여량 기반 초기 재고 계산
        from backend.app.calc_feeding.cal_guideIntake_service import (
            create_feeding_recommendation_service,
        )
        from datetime import timedelta

        guide_intake = 0
        try:
            # AI 추천 계산 (트랜잭션 유지를 위해 commit=False)
            recommendation = create_feeding_recommendation_service(
                db=db, pet_id=pet_id, commit=False
            )
            if isinstance(recommendation, dict):
                guide_intake = recommendation.get("guide_intake", 0)
        except Exception as ai_err:
            print(f"[WARNING] AI Recommendation calculation failed: {ai_err}")
            guide_intake = 0

        print(f"[DEBUG] 가이드 급여량: {guide_intake}")

        # 초기 계산값 준비
        left_food_count = 0
        expected_exdate = None

        if guide_intake and guide_intake > 0:
            left_food_count = int(total_weight // guide_intake)
            expected_exdate = date.today() + timedelta(days=left_food_count)

        print(f"[DEBUG] 계산된 잔여일: {left_food_count}, 소진일: {expected_exdate}")

        # 6-2. 최종 잔여량 및 계산 필드 등록
        new_CustomerFood = insert_customer_food(
            db=db,
            pet_id=pet_id,
            total_weight=total_weight,
            left_food_count=left_food_count,
            expected_exdate=expected_exdate,
        )
        
        if new_CustomerFood is None:
            raise ValueError("사료 재고 정보(CustomerFood) 생성에 실패했습니다.")

        if commit:
            db.commit()
            print(f"[SUCCESS] 사료 등록 및 트랜잭션 커밋 완료 (Pet ID: {pet_id})")
        else:
            db.flush()

        # commit=True일 때만 리프레시 수행 (commit=False인 온보딩 트랜잭션에서는 생략)
        if commit:
            if new_CustomerFood:
                db.refresh(new_CustomerFood)
            if new_PetProductFeeding:
                db.refresh(new_PetProductFeeding)

        return {
            "pet_id": new_PetProductFeeding.pet_id,
            "product_id": new_PetProductFeeding.product_id,
            "product_name": product.product_detail.product_name,
            "total_weight_g": new_CustomerFood.total_weight,
            "one_gram_calories": new_PetProductFeeding.one_gram_calories,
            "is_feeding_check": new_PetProductFeeding.is_feeding_check,
            "record_date": str(new_PetProductFeeding.record_date),
        }
    except Exception as e:
        db.rollback()
        print(f"[ERROR] 사료 등록 중 치명적 오류 발생: {str(e)}")
        raise e


# 수정 --------------------------------------------------
def update_pet_food(
    db: Session,
    customer_id: int,
    pet_id: int,
    product_id: int | None,
    effective_date: date | None,
    total_weight: int | None,
):
    if pet_id <= 0:
        raise ValueError("INVALID_PET_ID")

    if product_id is None or product_id <= 0:
        raise ValueError("INVALID_PRODUCT_ID")

    if effective_date is None:
        raise ValueError("INVALID_EFFECTIVE_DATE")

    if total_weight is None or total_weight <= 0:
        raise ValueError("INVALID_TOTAL_WEIGHT")

    pet = get_pet_by_id(db=db, pet_id=pet_id)
    if pet is None:
        raise ValueError("PET_NOT_FOUND")

    has_access = check_pet_owner(
        db=db,
        pet_id=pet_id,
        customer_id=customer_id,
    )
    if not has_access:
        raise ValueError("FORBIDDEN")

    product = get_product_by_id(db=db, product_id=product_id)
    if product is None or product.active is False:
        raise ValueError("PRODUCT_NOT_FOUND")

    if total_weight > product.weight:
        raise ValueError("INVALID_TOTAL_WEIGHT")

    if product.product_detail.calories is None:
        raise ValueError("PRODUCT_NOT_FOUND")

    active_pet_food = get_active_pet_food(db=db, pet_id=pet_id)
    if active_pet_food is None:
        raise ValueError("PET_FOOD_NOT_FOUND")

    updated_pet_food = update_pet_product_feeding(
        db=db,
        pet_food=active_pet_food,
        product_id=product_id,
        one_gram_calories=product.product_detail.calories,
        effective_date=effective_date,
    )

    updated_customer_food = update_customer_food_for_pet_food_change(
        db=db,
        pet_id=pet_id,
        total_weight=total_weight,
        effective_date=effective_date,
    )

    return {
        "pet_id": updated_pet_food.pet_id,
        "product_id": updated_pet_food.product_id,
        "record_date": str(updated_pet_food.record_date),
        "feeding_false_date": updated_pet_food.feeding_false_date,
        "is_feeding_check": updated_pet_food.is_feeding_check,
        "total_weight": updated_customer_food.total_weight,
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
            "product_name": f"{row.product_name} {row.weight}g X{row.quantity}",
            "brand": row.brand,
            "main_protein": row.main_protein,
            "life_stage": row.life,
            "weight": row.weight,
            "retail_price": row.retail_price,
            "thumbnail": row.thumbnail,
        }
        for row in merged_foods
    ]
