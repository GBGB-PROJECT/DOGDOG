from sqlalchemy.orm import Session
from db.models import CompanionButler, CompanionPet # (경로는 본인 환경에 맞게 유지)
from sqlalchemy import func
from datetime import date

## 모델정의 (DB에서 가지고 오는 역할 - 식재료 담당)
class PetRepository:
    @staticmethod
    def find_pets_by_customer_id(db: Session, customer_id: int):
        # 공식 클래스 이름(CompanionButler, CompanionPet)을 사용해 쿼리를 던집니다.
        return db.query(CompanionButler, CompanionPet)\
            .outerjoin(CompanionPet, CompanionButler.pet_id == CompanionPet.pet_id)\
            .filter(CompanionButler.customer_id == customer_id)\
            .all()

## 실질적 Service 역할 (연산처리 역할 - 메인 쉐프)
class PetService:
    @staticmethod
    def get_pet_list_with_profile(db: Session, customer_id: int):
        raw_data = PetRepository.find_pets_by_customer_id(db, customer_id)
        
        if not raw_data:
            return None

        results = []
        # 찾아온 데이터 뭉치(raw_data)를 풀어서 각각 butler, pet이라는 변수(별명)에 담습니다.
        for butler, pet in raw_data:
            
            # 1. pet_profile 조립 (수컷(중성화) 등)
            sex_text = "수컷" if pet.sex == 1 else "암컷"
            neutered_text = "(중성화)" if pet.is_neutered else ""
            profile = f"{sex_text}{neutered_text}"

            # 2. 나이 계산 (생일이 없을 경우를 대비해 COALESCE처럼 처리)
            age_korean = "나이 정보 없음"
            if pet.birth_day:
                today = date.today()
                # 간단한 나이 계산 로직 (연도와 월 차이 계산)
                years = today.year - pet.birth_day.year
                months = today.month - pet.birth_day.month
                if months < 0:
                    years -= 1
                    months += 12
                age_korean = f"{years}년 {months}개월"

            # 3. 최종 결과물 조립 (프론트엔드 HomeController가 기대하는 필드 추가)
            results.append({
                "pet_id": butler.pet_id,
                "nickname": pet.nickname,
                "pet_profile": profile,
                "pet_age": age_korean,
                "birth_day": str(pet.birth_day) if pet.birth_day else None,
                "sex": pet.sex,
                "profile_image": pet.profile_image
            })
        
        return results