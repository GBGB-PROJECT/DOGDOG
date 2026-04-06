from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from db import get_db
from ..service.feeding_service import FeedingService
from ..repository.feeding_repository import FeedingRepository

# --- Request/Response Models ---

class InventoryInfo(BaseModel):
    left_intake: float
    left_food_count: float
    is_feeding_check: bool = True

class FeedingLogBase(BaseModel):
    pet_food_id: Optional[int] = None
    pet_id: int
    customer_id: int
    food_type: str = "건식"
    amount: int
    calories: int
    feeding_date: date
    memo: Optional[str] = None
    last_update: Optional[str] = None

class FeedingCreate(BaseModel):
    pet_id: int
    amount: int = Field(gt=0, description="급여량 (g), 0보다 커야 함")
    feeding_date: Optional[date] = date.today()
    memo: Optional[str] = Field(None, max_length=200)

class FeedingUpdate(BaseModel):
    amount: Optional[int] = Field(None, gt=0)
    memo: Optional[str] = Field(None, max_length=200)
    new_feeding_date: Optional[date] = None

class SimpleSuccessResponse(BaseModel):
    status: str = "success"
    message: str
    data: dict

# --- Router ---

router = APIRouter(prefix="/api/v1/feeding", tags=["Feeding"])

@router.post("", status_code=status.HTTP_201_CREATED)
def register_feeding(request: FeedingCreate, db: Session = Depends(get_db)):
    """급여 기록을 등록하고 재고를 실시간으로 업데이트합니다."""
    # (실제 환경에선 JWT에서 customer_id 추출)
    customer_id = 110
    
    # 1. 미래 날짜 검증
    if request.feeding_date > date.today():
        raise HTTPException(status_code=400, detail="미래 날짜의 기록을 등록할 수 없습니다.")
        
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
            "message": "급여 기록이 등록되었습니다.",
            "data": {
                "pet_food_id": log.pet_food_id,
                "pet_id": log.pet_id,
                "customer_id": log.customer_id,
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
    """특정 기간 내 급여 기록 리스트와 총 합계를 반환합니다."""
    # (소유권 검증 로직 추가 가능)
    
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
        "message": "조회가 완료되었습니다.",
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
    feeding_date: date, # 파티션 식별을 위해 필수
    request: FeedingUpdate, 
    db: Session = Depends(get_db)
):
    """급여 기록을 수정하고 재고 및 칼로리를 재계산합니다."""
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
            "message": "급여 기록이 수정되었습니다.",
            "data": updated_log
        }
    except ValueError as v_err:
        raise HTTPException(status_code=404, detail="수정할 기록을 찾을 수 없습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"수정 실패: {str(e)}")

@router.delete("/{pet_food_id}")
def delete_feeding(
    pet_food_id: int, 
    feeding_date: date = Query(...), 
    db: Session = Depends(get_db)
):
    """특정 급여 기록을 삭제하고 소진된 사료 재고를 복구합니다."""
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
        raise HTTPException(status_code=404, detail="기록이 이미 존재하지 않습니다.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"삭제 실패: {str(e)}")