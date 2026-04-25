from sqlalchemy.orm import Session
from sqlalchemy import text
from traceback import format_exc

from db.models import CompanionPet, CompanionButler, CompanionBreed
import json

class PetRepository:
    def __init__(self, db: Session):
        self.db = db

    def check_breed_exists(self, breed_id: int) -> bool:
        return self.db.query(CompanionBreed).filter(CompanionBreed.breed_id == breed_id).first() is not None

    def get_duplicate_pet_count(self, customer_id: int, nickname: str, birth_day: str) -> int:
        from datetime import datetime
        # 문자열(YYYY-MM-DD)을 date 객체로 변환
        birth_date = datetime.strptime(birth_day, "%Y-%m-%d").date()
        
        count = (
            self.db.query(CompanionPet)
            .join(CompanionButler, CompanionPet.pet_id == CompanionButler.pet_id)
            .filter(
                CompanionButler.customer_id == customer_id,
                CompanionPet.nickname == nickname,
                CompanionPet.birth_day == birth_date
            )
            .count()
        )
        return count

    def create_pet_and_butler(self, customer_id: int, pet_data: dict) -> CompanionPet:
        try:
            # Parse sex_and_neuter
            sn = pet_data["sex_and_neuter"]
            sex_val = 1 if sn in [1, 2] else 2
            is_neutered_val = True if sn in [2, 4] else False

            # 1. CompanionPet 인스턴스 생성
            pet = CompanionPet(
                nickname=pet_data["nickname"],
                birth_day=pet_data["birth_day"],
                profile_image=pet_data.get("profile_image"),
                breed_id=pet_data["breed_id"],
                sex=sex_val,
                is_neutered=is_neutered_val,
                weight=pet_data["weight"],
                bcs=pet_data["bcs"],
                daily_walks=pet_data["daily_walk"], 
                feeding_count=len(pet_data.get("feeding_count", [])),
                feeding_intake=pet_data.get("feeding_intake"),
                water_intake=pet_data.get("water_intake"),
                supps=",".join(pet_data.get("supps", [])),
                medication=",".join(pet_data.get("medication", [])),
                allergies=",".join(pet_data.get("allergies", [])),
                diseases=",".join(pet_data.get("diseases", [])),
                active=True
            )
            
            self.db.add(pet)
            # 2. flush()를 호출하여 DB에서 pet_id 값을 즉시 할당받음
            self.db.flush()

            # flush 이후 pet_id가 제대로 할당되었는지 검증 (안전 장치)
            if not pet.pet_id:
                raise ValueError("pet_id를 확보하지 못했습니다.")

            # 3. 확보된 pet_id와 전달받은 customer_id를 이용해 CompanionButler 생성 (필수 필드 포함)
            butler = CompanionButler(
                pet_id=pet.pet_id,
                customer_id=customer_id,
                is_main_butler=True,
                active=True
            )
            
            self.db.add(butler)
            
            # 4. 단 한 번의 단일 트랜잭션으로 pet과 butler를 동시에 영구 저장
            self.db.commit()
            
            # commit 후 pet 객체를 서비스 계층에서 안전하게 다루기 위해 refresh 수행
            self.db.refresh(pet)
            
            return pet
            
        except Exception as e:
            # 예외 발생 시 반드시 롤백하여 DB의 부분 저장 원천 차단
            self.db.rollback()
            raise Exception(f"DATABASE_ERROR: {str(e)}")
