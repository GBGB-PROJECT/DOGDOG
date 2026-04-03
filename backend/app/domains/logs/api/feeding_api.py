from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from db import get_db
from ..service.feeding_service import FeedingService
from ..repository.feeding_repository import FeedingRepository

# 요청 데이터 정의
class FeedingRequest(BaseModel):
    pet_id: int
    amount: int

router = APIRouter(prefix="/api/v1/feeding", tags=["Feeding"])

@router.post("", status_code=status.HTTP_201_CREATED)
def register_feeding(request: FeedingRequest, db: Session = Depends(get_db)):
    # 실제 환경에선 JWT 토큰에서 customer_id를 추출합니다 (여기선 110으로 고정)
    customer_id = 110 

    # 검증 규칙: amount는 양수여야 함
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="급여량은 0보다 커야 합니다.")

    repo = FeedingRepository(db)
    service = FeedingService(repo)
    
    try:
        log, inven = service.execute_registration(
            customer_id=customer_id, 
            pet_id=request.pet_id, 
            amount=request.amount
        )

        return {
            "status": "success",
            "message": "급여 기록이 등록되었습니다.",
            "data": {
                "pet_id": log.pet_id,
                "amount": log.amount,
                "calories": log.calories,
                "inventory_info": {
                    "left_intake": float(inven.left_intake) if inven else 0,
                    "left_food_count": float(inven.left_food_count) if inven else 0,
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))