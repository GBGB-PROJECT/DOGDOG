from sqlalchemy import select
from sqlalchemy.orm import Session

from database.models import CompanionPet, CompanionCustomerFood, CompanionPetProductFeeding, OpdProduct, OpdProductDetail

from sqlalchemy.orm import Session
from backend.dependency.dependencies import get_pet_by_id

def get_current_pet_food_detail(db: Session, pet_id: int):
    # pet 존재 확인
    pet = get_pet_by_id(db=db, pet_id=pet_id)
    if pet is None:
        raise ValueError("PET_NOT_FOUND")

    """
    현재 급여 중인 사료 상세 조회
    - pet_product_feeding.is_feeding_check = True 인 데이터만 조회
    - product, pet, customer_food 조인
    """
    return (
        db.execute(
            select(
                CompanionPetProductFeeding.product_id.label("product_id"),
                CompanionPetProductFeeding.is_feeding_check.label("is_feeding_check"),
                OpdProductDetail.product_name.label("product_name"),
                OpdProduct.weight.label("product_weight"),
                CompanionPet.feeding_count.label("feeding_count"),
                CompanionCustomerFood.pet_id.label("pet_id"),
                CompanionCustomerFood.total_weight.label("total_weight"),
                CompanionCustomerFood.total_intake.label("total_intake"),
                CompanionCustomerFood.left_food_count.label("left_food_count")
            )
            .join(
            CompanionPet,
            CompanionPet.pet_id == CompanionPetProductFeeding.pet_id
            )
            .join(
                CompanionCustomerFood,
                CompanionCustomerFood.pet_id == CompanionPet.pet_id
            )
            .join(
                OpdProduct,
                OpdProduct.product_id == CompanionPetProductFeeding.product_id
            )
            .join(
                OpdProductDetail,
                OpdProductDetail.product_detail_id == OpdProduct.product_detail_id
            )
            .where(
                CompanionPetProductFeeding.pet_id == pet_id,
                # CompanionPet.pet_id == pet_id,
                # CompanionCustomerFood.pet_id == pet_id,
                CompanionPetProductFeeding.is_feeding_check == True,
                # OpdProduct.product_id == CompanionPetProductFeeding.product_id,
                # OpdProductDetail.product_detail_id == OpdProductDetail.product_detail_id,
            )
        )
    ).first()

# def get_current_pet_food_detail(db: Session, pet_id: int):
#     """
#     현재 급여 중인 사료 상세 조회
#     - pet_product_feeding.is_feeding_check = True 인 데이터만 조회
#     - product, pet, customer_food 조인
#     """
#     return (
#         db.query(
#             CompanionPetProductFeeding.pet_id,
#             CompanionPetProductFeeding.product_id,
#             CompanionPetProductFeeding.is_feeding_check,

#             OpdProduct.name.label("product_name"),
#             OpdProduct.weight.label("product_weight"),

#             CompanionPet.feeding_count.label("feeding_count"),

#             CompanionCustomerFood.total_weight.label("total_weight"),
#             CompanionCustomerFood.total_intake.label("total_intake"),
#             CompanionCustomerFood.left_food_count.label("left_food_count"),
#         )
#         .join(
#             OpdProduct,
#             CompanionPetProductFeeding.product_id == OpdProduct.product_id
#         )
#         .join(
#             CompanionPet,
#             CompanionPetProductFeeding.pet_id == CompanionPet.pet_id
#         )
#         .join(
#             CompanionCustomerFood,
#             CompanionPetProductFeeding.pet_id == CompanionCustomerFood.pet_id
#         )
#         .filter(
#             CompanionPetProductFeeding.pet_id == pet_id,
#             CompanionPetProductFeeding.is_feeding_check.is_(True)
#         )
#         .first()
#     )