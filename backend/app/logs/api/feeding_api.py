from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from db.db import get_db
from ..service.feeding_service import FeedingService
from ..repository.feeding_repository import FeedingRepository

# --- Request/Response Models ---

class FeedingCreate(BaseModel):
    pet_id: int
    amount: int = Field(gt=0, description="급여량 (g)")
    feeding_date: Optional[date] = None # 기본값: 오늘
    memo: Optional[str] = Field(None, max_length=200)

class FeedingUpdate(BaseModel):
    amount: Optional[int] = Field(None, gt=0)
    memo: Optional[str] = Field(None, max_length=200)
    new_feeding_date: Optional[date] = None

class FeedingLogResponse(BaseModel):
    pet_food_id: int
    pet_id: int
    customer_id: int
    food_type: str
    amount: int
    calories: int
    feeding_date: date
    memo: Optional[str]
    last_update: date

# --- Router ---

router = APIRouter(tags=["Feeding"])

@router.post("", status_code=status.HTTP_201_CREATED)
def register_feeding(request: FeedingCreate, db: Session = Depends(get_db)):
    """[등록] 새로운 급여 기록을 등록하며, 운영 DB(public) 권한 없을 시 dog_5 스키마에 자동 저장합니다."""
    # (실제 환경에선 JWT에서 customer_id 추출)
    customer_id = 110
    
    repo = FeedingRepository(db)
    service = FeedingService(repo)
    
    try:
        log, inven = service.register_feeding(
            customer_id=customer_id,
            pet_id=request.pet_id,
            amount=request.amount,
            feeding_date=request.feeding_date,
            memo=request.memo
        )
        
        return {
            "status": "success",
            "message": "급여 기록이 등록되었습니다. (이원화 스키마 전략 적용)",
            "data": {
                "pet_food_id": log.pet_food_id,
                "pet_id": log.pet_id,
                "amount": log.amount,
                "calories": log.calories,
                "feeding_date": log.feeding_date,
                "inventory_info": {
                    "left_intake": float(inven.left_intake) if inven else 0,
                    "left_food_count": float(inven.left_food_count) if inven else 0
                } if inven else None
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"등록 실패: {str(e)}")

@router.get("/{pet_id}")
def get_feeding_logs(
    pet_id: int, 
    start_date: Optional[date] = None, 
    end_date: Optional[date] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """[조회] 운영 DB와 연습장 DB의 모든 급여 데이터를 조회합니다."""
    repo = FeedingRepository(db)
    service = FeedingService(repo)
    
    result = service.get_feeding_logs(
        pet_id=pet_id, 
        start_date=start_date, 
        end_date=end_date, 
        limit=limit, 
        offset=offset
    )
    
    return {
        "status": "success",
        "message": "급여 데이터를 성공적으로 조회했습니다.",
        "data": {
            "pet_id": pet_id,
            "daily_summary": {
                "total_amount": result["total_amount"],
                "total_calories": result["total_calories"]
            },
            "logs": result["logs"]
        }
    }

@router.patch("/{pet_food_id}")
def update_feeding(
    pet_food_id: int, 
    feeding_date: date, # 파티션 키
    request: FeedingUpdate, 
    db: Session = Depends(get_db)
):
    """[수정] 특정 급여 기록을 수정하며 스키마 가변성을 지원합니다."""
    customer_id = 110
    
    repo = FeedingRepository(db)
    service = FeedingService(repo)
    
    try:
        updated_log, inventory = service.update_feeding(
            customer_id=customer_id,
            pet_food_id=pet_food_id,
            old_date=feeding_date,
            new_data=request.dict(exclude_unset=True)
        )
        
        return {
            "status": "success",
            "message": "기록이 수정되었습니다.",
            "data": updated_log
        }
    except ValueError as v_err:
        raise HTTPException(status_code=404, detail="해당 기록을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수정 실패: {str(e)}")

@router.delete("/{pet_food_id}")
def delete_feeding(
    pet_food_id: int, 
    feeding_date: date = Query(...), 
    db: Session = Depends(get_db)
):
    """[삭제] 급여 기록을 삭제하고 소모된 재고를 자동 복구합니다."""
    customer_id = 110
    
    repo = FeedingRepository(db)
    service = FeedingService(repo)
    
    try:
        service.delete_feeding(customer_id, pet_food_id, feeding_date)
        return {
            "status": "success",
            "message": "삭제 및 재고 복구가 완료되었습니다.",
            "data": {"deleted_id": pet_food_id}
        }
    except ValueError:
        raise HTTPException(status_code=404, detail="삭제할 기록이 존재하지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")