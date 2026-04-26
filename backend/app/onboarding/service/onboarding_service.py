from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Any
import logging

from app.onboarding.api.schemas import OnboardingRequest
from app.auth.service.auth_service import AuthService
from app.auth.repository.auth_repository import AuthRepository
from app.auth.schemas import EmailSignupRequest
from app.pets.service.pet_service import PetService
from app.pets.schemas import PetRegisterRequest
from app.pets.service.petFood_service import create_pet_food
from db.models import CompanionCustomer, CompanionPet

logger = logging.getLogger(__name__)

class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(AuthRepository(db))
        self.pet_service = PetService(db)

    def complete_onboarding(self, request: OnboardingRequest) -> dict:
        """
        유저, 반려견, 사료 등록을 순차적으로 수행하는 통합 온보딩 로직.
        실패 시 이전 단계에서 생성된 데이터를 삭제(보상 트랜잭션)합니다.
        """
        customer_id = None
        pet_id = None

        # 1. 유저 생성 (AuthService)
        try:
            # UserCreate -> EmailSignupRequest 매핑
            auth_req = EmailSignupRequest(
                email=request.user.email,
                password=request.user.password or "", # password가 None일 경우 대비
                nickname=request.user.nickname,
                phone=request.user.phone
            )
            auth_result = self.auth_service.register_user(auth_req)
            customer_id = auth_result["customer"].customer_id
            logger.info(f"Onboarding Step 1 Success: Customer ID {customer_id}")

            # 1.5. 알림 설정 초기화 (Notification Settings)
            from db.models import CompanionCustomerNotiSettings
            noti_categories = ["subs_delivery", "subs_payment", "food_exdate"]
            noti_settings = [
                CompanionCustomerNotiSettings(
                    customer_id=customer_id,
                    category=cat,
                    noti_option1=False,
                    noti_option2=False
                ) for cat in noti_categories
            ]
            self.db.add_all(noti_settings)
            # 이후 Step 2, 3의 commit() 시점에 함께 저장됨
            logger.info(f"Onboarding Step 1.5 Success: Notification settings initialized")
        except Exception as e:
            logger.error(f"Onboarding Step 1 Failed: {str(e)}")
            raise e # AuthService 내부에서 이미 예외 처리가 되어 있음

        # 2. 반려견 생성 (PetService)
        try:
            # PetCreate -> PetRegisterRequest 매핑
            # sex (1,2) + is_neutered (bool) -> sex_and_neuter (1,2,3,4)
            # 1: 남아/안함, 2: 남아/함, 3: 여아/안함, 4: 여아/함
            sex_and_neuter = (request.pet.sex - 1) * 2 + (2 if request.pet.is_neutered else 1)
            
            pet_req = PetRegisterRequest(
                nickname=request.pet.nickname,
                birth_day=request.pet.birth_day.strftime("%Y-%m-%d") if request.pet.birth_day else None,
                breed_id=request.pet.breed_id,
                sex_and_neuter=sex_and_neuter,
                weight=request.pet.weight,
                bcs=request.pet.bcs,
                daily_walks=request.pet.daily_walks,
                feeding_count=[""] * request.pet.feeding_count # 숫자만큼 빈 문자열 배열 생성
            )
            pet_result = self.pet_service.register_pet(customer_id, pet_req)
            pet_id = pet_result["data"]["pet_id"]
            logger.info(f"Onboarding Step 2 Success: Pet ID {pet_id}")
        except Exception as e:
            logger.error(f"Onboarding Step 2 Failed: {str(e)}. Rolling back customer {customer_id}")
            self._rollback_customer(customer_id)
            raise e

        # 3. 사료 생성 (create_pet_food)
        try:
            food_result = create_pet_food(
                db=self.db,
                customer_id=customer_id,
                pet_id=pet_id,
                product_id=request.food.product_id,
                total_weight=request.food.total_weight
            )
            logger.info(f"Onboarding Step 3 Success: Food Registered")
        except Exception as e:
            logger.error(f"Onboarding Step 3 Failed: {str(e)}. Rolling back pet {pet_id} and customer {customer_id}")
            self._rollback_pet(pet_id)
            self._rollback_customer(customer_id)
            # create_pet_food는 ValueError를 던질 수 있으므로 HTTPException으로 변환 검토
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            raise e

        return {
            "success": True,
            "message": "통합 온보딩이 완료되었습니다.",
            "data": {
                "customer_id": customer_id,
                "pet_id": pet_id,
                "auth": auth_result.get("authorization") # 토큰 정보 포함
            }
        }

    def _rollback_customer(self, customer_id: int):
        """회원 가입 보상 트랜잭션 (삭제)"""
        if customer_id:
            try:
                # detail부터 삭제 시도 (PK 제약 조건 고려)
                from db.models import CompanionCustomerDetail
                self.db.query(CompanionCustomerDetail).filter_by(customer_id=customer_id).delete()
                self.db.query(CompanionCustomer).filter_by(customer_id=customer_id).delete()
                self.db.commit()
                logger.info(f"Rollback: Customer {customer_id} deleted.")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Rollback failed for customer {customer_id}: {str(e)}")

    def _rollback_pet(self, pet_id: int):
        """반려견 가입 보상 트랜잭션 (삭제)"""
        if pet_id:
            try:
                # butler부터 삭제 시도 (FK 제약 조건 고려)
                from db.models import CompanionButler
                self.db.query(CompanionButler).filter_by(pet_id=pet_id).delete()
                self.db.query(CompanionPet).filter_by(pet_id=pet_id).delete()
                self.db.commit()
                logger.info(f"Rollback: Pet {pet_id} deleted.")
            except Exception as e:
                self.db.rollback()
                logger.error(f"Rollback failed for pet {pet_id}: {str(e)}")
