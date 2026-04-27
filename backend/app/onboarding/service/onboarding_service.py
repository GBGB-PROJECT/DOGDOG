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
from app.calc_feeding.cal_guideIntake_service import (
    create_feeding_recommendation_service,
)
from db.models import CompanionCustomer, CompanionPet

logger = logging.getLogger(__name__)


class OnboardingService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_service = AuthService(AuthRepository(db))
        self.pet_service = PetService(db)

    def complete_onboarding(self, request: OnboardingRequest) -> dict:
        """
        유저, 반려견, 사료 등록을 단일 트랜잭션으로 통합 수행하는 온보딩 로직.
        Deferred Commit 패턴을 사용하여 모든 단계가 성공해야만 최종 커밋됩니다.
        """
        try:
            # 1. 유저 생성 (AuthService)
            auth_req = EmailSignupRequest(
                email=request.user.email,
                password=request.user.password or "",
                nickname=request.user.nickname,
                phone=request.user.phone,
            )
            
            try:
                # commit=False로 호출하여 DB 세션에만 반영하고 확정은 미룸
                auth_result = self.auth_service.register_user(auth_req, commit=False)
            except ValueError as e:
                if str(e) == "EMAIL_ALREADY_EXISTS":
                    raise HTTPException(status_code=409, detail="이미 가입된 이메일입니다.")
                raise e

            customer_id = auth_result["customer"].customer_id
            logger.info(f"Onboarding Step 1 Success: Customer ID {customer_id}")

            # 1.5. 알림 설정 초기화
            from db.models import CompanionCustomerNotiSettings
            noti_categories = ["subs_delivery", "left_feeding_day"]
            noti_settings = [
                CompanionCustomerNotiSettings(
                    customer_id=customer_id,
                    category=cat,
                    noti_option1=False,
                    noti_option2=False,
                )
                for cat in noti_categories
            ]
            self.db.add_all(noti_settings)
            
            # 다음 단계를 위해 세션 반영 (ID 등 확보)
            self.db.flush()
            logger.info(f"Onboarding Step 1.5 Success: Notification settings initialized")

            # 2. 반려견 생성 (PetService)
            sex_and_neuter = (request.pet.sex - 1) * 2 + (2 if request.pet.is_neutered else 1)
            pet_req = PetRegisterRequest(
                nickname=request.pet.nickname,
                birth_day=request.pet.birth_day.strftime("%Y-%m-%d") if request.pet.birth_day else None,
                breed_id=request.pet.breed_id,
                sex_and_neuter=sex_and_neuter,
                weight=request.pet.weight,
                bcs=request.pet.bcs,
                daily_walks=request.pet.daily_walks,
                feeding_count=[""] * request.pet.feeding_count,
            )
            
            # commit=False 전달
            pet_result = self.pet_service.register_pet(customer_id, pet_req, commit=False)
            pet_id = pet_result["data"]["pet_id"]
            
            # 다음 단계를 위해 세션 반영
            self.db.flush()
            logger.info(f"Onboarding Step 2 Success: Pet ID {pet_id}")

            # 3. 사료 생성 (create_pet_food)
            # commit=False 전달
            create_pet_food(
                db=self.db,
                customer_id=customer_id,
                pet_id=pet_id,
                product_id=request.food.product_id,
                total_weight=request.food.total_weight,
                commit=False
            )
            
            # 다음 단계를 위해 세션 반영
            self.db.flush()
            logger.info(f"Onboarding Step 3 Success: Food Registered")

            # 4. AI 급여량 추천 계산 연동
            create_feeding_recommendation_service(db=self.db, pet_id=pet_id)
            logger.info(f"Onboarding Step 4 Success: AI Feeding Recommendation Created")

            # 5. 모든 단계 성공 시 최종 커밋
            self.db.commit()
            logger.info(f"Onboarding Transaction Committed: All steps successful.")

            return {
                "success": True,
                "message": "통합 온보딩이 완료되었습니다.",
                "data": {
                    "customer_id": customer_id,
                    "pet_id": pet_id,
                    "auth": {
                        "access_token": auth_result.get("access_token"),
                        "refresh_token": auth_result.get("refresh_token"),
                        "expires_in": auth_result.get("expires_in")
                    },
                },
            }

        except Exception as e:
            # 예외 발생 시 전체 롤백 (이전의 모든 INSERT/UPDATE 취소)
            self.db.rollback()
            logger.error(f"Onboarding Failed: {str(e)}. Transaction rolled back.")
            
            if isinstance(e, HTTPException):
                raise e
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            raise HTTPException(status_code=500, detail=f"온보딩 처리 중 서버 오류가 발생했습니다: {str(e)}")
