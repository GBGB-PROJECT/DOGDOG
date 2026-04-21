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
            # 1: M/False, 2: M/True, 3: F/False, 4: F/True
            # To respect DB constraint `sex in (1,2)` -> 1=Male, 2=Female
            sn = pet_data["sex_and_neuter"]
            sex_val = 1 if sn in [1, 2] else 2
            is_neutered_val = True if sn in [2, 4] else False

            # CompanionPet insert
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
                supps=json.dumps(pet_data.get("supps", []), ensure_ascii=False),
                medication=json.dumps(pet_data.get("medication", []), ensure_ascii=False),
                allergies=json.dumps(pet_data.get("allergies", []), ensure_ascii=False),
                diseases=json.dumps(pet_data.get("diseases", []), ensure_ascii=False),
                active=True
            )
            self.db.add(pet)
            self.db.flush() # get pet_id

            # CompanionButler insert
            butler = CompanionButler(
                pet_id=pet.pet_id,
                customer_id=customer_id,
                is_main_butler=True,
                active=True
            )
            self.db.add(butler)
            self.db.commit()
            
            return pet
        except Exception as e:
            self.db.rollback()
            raise Exception(f"DATABASE_ERROR: {str(e)}")
