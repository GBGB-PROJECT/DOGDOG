from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import logging

from db.db import get_db

from dependencies import check_pet_owner, get_current_user
from app.logs.service.pet_log_service import PetLogService
from app.logs.repository.pet_log_repository import PetLogRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/logs/weight_bcs", tags=["Weight & BCS Logs"])


# Schemas
class WeightBcsCreateRequest(BaseModel):
    weight: Optional[float] = Field(None, gt=0, lt=200, description="체중")
    bcs: Optional[float] = Field(None, ge=1, le=9, description="BCS 점수 (1~9)")
    log_date: datetime = Field(..., description="기록 일시")
    memo: Optional[str] = Field(None, max_length=200)


class WeightBcsUpdateRequest(BaseModel):
    log_status: float = Field(..., description="수정할 수치")
    log_date: Optional[datetime] = Field(None, description="기록 일시")


class WeightBcsResponseData(BaseModel):
    pet_log_numeric_id: int
    pet_id: int
    category: str
    log_status: float
    log_date: datetime
    memo: Optional[str]
    last_update: datetime


class WeightBcsResponse(BaseModel):
    status: str = "success"
    message: str
    data: List[WeightBcsResponseData]


@router.post(
    "/{pet_id}", response_model=WeightBcsResponse, status_code=status.HTTP_201_CREATED
)
def create_weight_bcs(
    pet_id: int,
    request: WeightBcsCreateRequest,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """반려견의 체중 및 BCS 수치를 기록합니다."""
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    service = PetLogService(PetLogRepository(db))
    try:
        inserted_logs = service.register_weight_bcs(
            customer_id=customer_id, pet_id=pet_id, request_data=request.model_dump()
        )
        return {
            "status": "success",
            "message": "체중 및 bcs 기록이 등록되었습니다.",
            "data": inserted_logs,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"체중/BCS 기록 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 에러가 발생했습니다.",
        )


@router.put("/{log_id}", response_model=WeightBcsResponse)
def update_weight_bcs(
    log_id: int,
    request: WeightBcsUpdateRequest,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """단일 기록의 수치 또는 날짜를 수정합니다."""
    service = PetLogService(PetLogRepository(db))
    log = service.repo.get_log_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청하신 기록을 찾을 수 없습니다.",
        )
    if log.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    try:
        updated_log = service.update_weight_bcs(
            log_id, request.model_dump(exclude_unset=True)
        )
        return {
            "status": "success",
            "message": "기록이 성공적으로 수정되었습니다.",
            "data": updated_log,
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{log_id}")
def delete_weight_bcs(
    log_id: int,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """단일 기록을 삭제하고 안전하게 롤백합니다."""
    service = PetLogService(PetLogRepository(db))
    log = service.repo.get_log_by_id(log_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="요청하신 기록을 찾을 수 없습니다.",
        )
    if log.customer_id != customer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="접근 권한이 없습니다."
        )

    try:
        service.delete_weight_bcs(log_id)
        return {
            "status": "success",
            "message": "기록이 삭제되고 최근 정보로 수정되었습니다.",
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
