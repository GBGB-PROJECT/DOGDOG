from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.pets.schemas import PetRegisterRequest
from app.pets.repository.pet_repository import PetRepository
from datetime import datetime

class PetService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PetRepository(db)

    def register_pet(self, customer_id: int, request: PetRegisterRequest) -> dict:
        # 1. 폼 데이터
        pet_data = request.model_dump()
        
        # 2. 품종 확인
        if not self.repo.check_breed_exists(pet_data["breed_id"]):
            raise HTTPException(status_code=400, detail="존재하지 않는 품종입니다.")
        
        # 3. 중복 등록 방지 (Idempotency)
        if self.repo.get_duplicate_pet_count(customer_id, pet_data["nickname"], pet_data["birth_day"]) > 0:
            raise HTTPException(
                status_code=409,
                detail={"success": False, "error_code": "DUPLICATE_PET", "message": "이미 동일한 정보로 등록된 반려견이 존재합니다."}
            )
        
        # 4. 저장 (Transaction)
        try:
            pet = self.repo.create_pet_and_butler(customer_id, pet_data)
        except Exception as e:
            error_msg = str(e)
            if "DATABASE_ERROR" in error_msg:
                raise HTTPException(
                    status_code=500,
                    detail={"success": False, "error_code": "DATABASE_ERROR", "message": "데이터베이스 저장 중 오류가 발생했습니다."}
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail={"success": False, "error_code": "MAPPING_ERROR", "message": "소유자 관계 매핑 중 오류가 발생했습니다."}
                )

        # 5. 응답 구성 (HATEOAS)
        return {
            "success": True,
            "message": "반려동물 등록이 완료되었습니다.",
            "data": {
                "pet_id": pet.pet_id,
                "nickname": pet.nickname,
                "breed_id": pet.breed_id,
                "create_date": pet.last_update.strftime("%Y-%m-%dT%H:%M:%S") if pet.last_update else datetime.now().isoformat(),
                "self": f"/pets/{pet.pet_id}"
            }
        }
