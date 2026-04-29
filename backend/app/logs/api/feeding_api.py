from datetime import date, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from db.db import get_db
from dependencies import check_pet_owner, get_current_user
from ..service.feeding_service import FeedingService
from ..repository.feeding_repository import FeedingRepository

logger = logging.getLogger(__name__)


# --- Request/Response Models ---
class FeedingCreate(BaseModel):
    pet_id: int
    amount: int = Field(gt=0, description="급여량(g)은 0보다 커야 합니다.")
    feeding_date: Optional[date] = None
    feeding_time: Optional[time] = None
    memo: Optional[str] = Field(None, max_length=200)


class FeedingUpdate(BaseModel):
    amount: Optional[int] = Field(None, gt=0)
    memo: Optional[str] = Field(None, max_length=200)
    new_feeding_date: Optional[date] = None
    feeding_time: Optional[time] = None


# --- Router ---
router = APIRouter(prefix="/api/v1/logs/feeding", tags=["Feeding Logs"])


@router.post("", status_code=status.HTTP_201_CREATED)
def register_feeding(
    request: FeedingCreate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[등록] 새로운 급여 기록을 등록하고 사료 재고를 업데이트합니다."""

    repo = FeedingRepository(db)
    service = FeedingService(repo)

    if not check_pet_owner(db, request.pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"해당 반려동물(ID:{request.pet_id})에 대한 접근 권한이 없습니다.",
        )

    if not repo.check_active_feeding_exists(request.pet_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="등록된 사료 정보가 없습니다. 먼저 급여 사료를 설정해주세요.",
        )

    try:
        log, inven = service.register_feeding(
            customer_id=customer_id,
            pet_id=request.pet_id,
            amount=request.amount,
            feeding_date=request.feeding_date,
            feeding_time=request.feeding_time,
            memo=request.memo,
        )

        return {
            "status": "success",
            "message": "급여 기록이 성공적으로 등록되었습니다.",
            "data": {
                "pet_food_id": log.pet_food_id,
                "pet_id": log.pet_id,
                "amount": log.amount,
                "feeding_date": log.feeding_date,
                "feeding_time": log.feeding_time,
                "inventory": {
                    "total_intake": float(inven.total_intake) if inven else 0,
                    "food_count": inven.food_count if inven else 0,
                }
                if inven
                else None,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"급여 기록 등록 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )


@router.get("/{pet_id}")
def get_feeding_logs(
    pet_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = 20,
    offset: int = 0,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[조회] 특정 반려동물의 급여 기록과 통계를 조회합니다."""
    repo = FeedingRepository(db)

    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    service = FeedingService(repo)

    try:
        result = service.get_feeding_logs(pet_id, start_date, end_date, limit, offset)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"급여 기록 조회 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )



@router.patch("/{pet_food_id}")
def update_feeding(
    pet_food_id: int,
    feeding_date: date,
    request: FeedingUpdate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[수정] 급여 기록을 수정하고 재고 데이터를 보정합니다."""
    repo = FeedingRepository(db)
    service = FeedingService(repo)

    try:
        updated_log, inven = service.update_feeding(
            customer_id=customer_id,
            pet_food_id=pet_food_id,
            old_date=feeding_date,
            new_data=request.model_dump(exclude_unset=True)
            if hasattr(request, "model_dump")  # pydantic 버젼 이슈 해결
            else request.dict(exclude_unset=True),  # 세팅된 데이터만 넘김
        )
        return {
            "status": "success",
            "message": "급여 기록이 수정되었습니다.",
            "data": {
                "pet_food_id": updated_log.pet_food_id,
                "customer_id": updated_log.customer_id,
                "food_type": updated_log.food_type,
                "amount": updated_log.amount,
                "calories": updated_log.calories,
                "feeding_date": updated_log.feeding_date,
                "feeding_time": updated_log.feeding_time,
                "memo": updated_log.memo,
                "last_update": updated_log.last_update,
            },
        }
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "요청하신 급여 기록을 찾을 수 없습니다.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 급여 기록을 찾을 수 없습니다.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
            )
    except Exception as e:
        logger.error(f"급여 기록 수정 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )


@router.delete("/{pet_food_id}")
def delete_feeding(
    pet_food_id: int, 
    feeding_date: date = Query(...), 
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """[삭제] 급여 기록을 삭제하고 소모된 재고를 복구합니다."""
    repo = FeedingRepository(db)
    service = FeedingService(repo)

    try:
        service.delete_feeding(customer_id, pet_food_id, feeding_date)
        return {"status": "success", "message": "삭제 및 재고 복구가 완료되었습니다."}
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "요청하신 급여 기록을 찾을 수 없습니다.":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 급여 기록을 찾을 수 없습니다.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
            )
    except Exception as e:
        logger.error(f"급여 기록 삭제 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
