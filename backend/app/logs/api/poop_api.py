from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator
import logging

from db.db import get_db
from dependencies import check_pet_owner, get_current_user
from ..service.pet_log_service import PetLogService
from ..repository.pet_log_repository import PetLogRepository

logger = logging.getLogger(__name__)


# --- Pydantic Request/Response Schemas ---


class PoopLogCreate(BaseModel):
    """배변 기록 등록 요청 스키마."""

    log_status: float = Field(
        ..., ge=1.0, le=7.0, description="배변 점수 (1:매우딱딱 ~ 4:이상적 ~ 7:설사)"
    )
    log_date: datetime = Field(
        ..., description="실제 발생 일시 (YYYY-MM-DD HH:mm:ss)"
    )
    memo: Optional[str] = Field(
        None, max_length=200, description="색상, 특이사항 등 (최대 200자)"
    )


class PoopLogUpdate(BaseModel):
    """배변 기록 수정 요청 스키마."""

    log_status: Optional[float] = Field(
        None, ge=1.0, le=7.0, description="배변 점수 (1.0~7.0)"
    )
    log_date: Optional[datetime] = Field(
        None, description="실제 발생 일시 (YYYY-MM-DD HH:mm:ss)"
    )
    memo: Optional[str] = Field(
        None, max_length=200, description="메모 (최대 200자)"
    )


class PoopLogResponse(BaseModel):
    """배변 기록 응답 스키마."""

    pet_log_numeric_id: int
    pet_id: int
    category: str
    log_status: float
    log_date: str
    memo: Optional[str] = None
    last_update: str

    @classmethod
    def from_orm_model(cls, log) -> "PoopLogResponse":
        """SQLAlchemy ORM 모델을 응답 스키마로 변환합니다."""
        return cls(
            pet_log_numeric_id=log.pet_log_numeric_id,
            pet_id=log.pet_id,
            category=log.category,
            log_status=float(log.log_status) if log.log_status else 0.0,
            log_date=log.log_date.strftime("%Y-%m-%d %H:%M:%S") if log.log_date else "",
            memo=log.memo,
            last_update=log.last_update.strftime("%Y-%m-%d %H:%M:%S") if log.last_update else "",
        )


# --- Router ---
router = APIRouter(prefix="/api/v1/logs/poop", tags=["Poop Logs"])


@router.post("/{pet_id}", status_code=status.HTTP_201_CREATED)
def register_poop_log(
    pet_id: int,
    request: PoopLogCreate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[등록] 반려견의 배변 기록을 등록합니다."""

    # 1. 소유권 검증
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"해당 반려동물(ID:{pet_id})에 대한 접근 권한이 없습니다.",
        )

    repo = PetLogRepository(db)
    service = PetLogService(repo)

    try:
        log, is_duplicate = service.register_poop_log(
            customer_id=customer_id,
            pet_id=pet_id,
            log_status=request.log_status,
            log_date=request.log_date,
            memo=request.memo,
        )

        response = {
            "status": "success",
            "message": "배변 기록이 등록되었습니다.",
            "data": PoopLogResponse.from_orm_model(log).model_dump(),
        }

        # 중복 경고 (비차단)
        if is_duplicate:
            response["warning"] = (
                f"동일한 시간({request.log_date.strftime('%Y-%m-%d %H:%M:%S')})에 "
                f"이미 등록된 배변 기록이 있습니다."
            )

        return response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"배변 기록 등록 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )


@router.put("/{pet_log_numeric_id}")
def update_poop_log(
    pet_log_numeric_id: int,
    request: PoopLogUpdate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[수정] 배변 기록의 점수, 발생 일시, 메모를 수정합니다."""

    repo = PetLogRepository(db)
    service = PetLogService(repo)

    # 1. 로그 존재 확인 및 소유권 검증
    log = service.get_poop_log(pet_log_numeric_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 배변 기록을 찾을 수 없습니다.",
        )
    if not check_pet_owner(db, log.pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    try:
        update_data = (
            request.model_dump(exclude_unset=True)
            if hasattr(request, "model_dump")
            else request.dict(exclude_unset=True)
        )

        updated_log = service.update_poop_log(pet_log_numeric_id, update_data)

        return {
            "status": "success",
            "message": "배변 기록이 수정되었습니다.",
            "data": PoopLogResponse.from_orm_model(updated_log).model_dump(),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"배변 기록 수정 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )


@router.delete("/{pet_log_numeric_id}")
def delete_poop_log(
    pet_log_numeric_id: int,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[삭제] 배변 기록을 논리 삭제(Soft Delete)합니다."""

    repo = PetLogRepository(db)
    service = PetLogService(repo)

    # 1. 로그 존재 확인 및 소유권 검증
    log = service.get_poop_log(pet_log_numeric_id)
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 배변 기록을 찾을 수 없습니다.",
        )
    if not check_pet_owner(db, log.pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="접근 권한이 없습니다.",
        )

    try:
        service.delete_poop_log(pet_log_numeric_id)
        return {
            "status": "success",
            "message": "배변 기록이 삭제되었습니다.",
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        logger.error(f"배변 기록 삭제 중 서버 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
