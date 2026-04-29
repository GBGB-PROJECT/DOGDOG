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
        데이터 무결성을 위해 각 단계의 결과값을 엄격히 검증합니다.
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
                # commit=False로 호출하여 DB 세션에만 반영
                auth_result = self.auth_service.register_user(auth_req, commit=False)
                if not auth_result or "customer" not in auth_result:
                    raise ValueError("유저 정보 생성에 실패했습니다.")
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
            
            # ID 확보를 위해 flush
            self.db.flush()

            # 2. 반려견 생성 (PetService)
            # 성별 및 중성화 코드 계산 (백엔드 도메인 규칙 준수)
            sex_and_neuter = (request.pet.sex - 1) * 2 + (2 if request.pet.is_neutered else 1)
            
            pet_req = PetRegisterRequest(
                nickname=request.pet.nickname,
                birth_day=request.pet.birth_day.strftime("%Y-%m-%d") if request.pet.birth_day else None,
                breed_id=request.pet.breed_id,
                sex_and_neuter=sex_and_neuter,
                weight=request.pet.weight,
                bcs=request.pet.bcs,
                daily_walks=request.pet.daily_walks,
                feeding_count=[""] * request.pet.feeding_count, # feeding_count를 기반으로 빈 리스트 생성
            )
            
            pet_result = self.pet_service.register_pet(customer_id, pet_req, commit=False)
            if not pet_result or "data" not in pet_result:
                raise ValueError("반려견 정보 생성에 실패했습니다.")
                
            pet_id = pet_result["data"].get("pet_id")
            if not pet_id:
                raise ValueError("반려견 ID를 확보할 수 없습니다.")
            
            self.db.flush()
            logger.info(f"Onboarding Step 2 Success: Pet ID {pet_id}")

            # 3. 사료 생성 (create_pet_food)
            # commit=False 전달하여 통합 트랜잭션 유지
            food_result = create_pet_food(
                db=self.db,
                customer_id=customer_id,
                pet_id=pet_id,
                product_id=request.food.product_id,
                total_weight=request.food.total_weight,
                commit=False
            )
            
            if not food_result:
                raise ValueError("사료 정보 등록에 실패했습니다.")
            
            self.db.flush()
            logger.info(f"Onboarding Step 3 Success: Food Registered")

            # 4. 모든 단계 성공 시 최종 커밋
            self.db.commit()
            logger.info(f"Onboarding Transaction Committed: Success (Customer: {customer_id}, Pet: {pet_id})")

            # 5. 안전한 응답 조립 (NoneType 방지)
            access_token = auth_result.get("access_token")
            refresh_token = auth_result.get("refresh_token")
            
            if not access_token:
                logger.warning(f"Warning: Access token is missing for customer {customer_id}")

            return {
                "success": True,
                "message": "통합 온보딩이 완료되었습니다.",
                "auth": {
                    "access_token": access_token,
                    "refresh_token": refresh_token
                },
                "pet_id": pet_id,
                "customer_id": customer_id
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Onboarding Failed: {str(e)}. Transaction rolled back.")
            
            if isinstance(e, HTTPException):
                raise e
            if isinstance(e, ValueError):
                raise HTTPException(status_code=400, detail=str(e))
            raise HTTPException(status_code=500, detail=f"온보딩 처리 중 서버 오류가 발생했습니다: {str(e)}")
