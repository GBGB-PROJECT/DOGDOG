from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from db.db import get_db
from dependencies import check_pet_owner, get_current_user
from ..service.pet_log_service import PetLogService
from ..repository.pet_log_repository import PetLogRepository
from .schemas import NumericLogCreate, NumericLogUpdate, NumericLogResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/logs/numeric", tags=["Numeric Logs"])

@router.post("/{category}/{pet_id}", status_code=status.HTTP_201_CREATED)
def register_numeric_log(
    category: str,
    pet_id: int,
    request: NumericLogCreate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[등록] 통합 수치형 기록 등록 (weight_bcs 특수 처리 포함)"""
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(status_code=403, detail="접근 권한이 없습니다.")

    repo = PetLogRepository(db)
    service = PetLogService(repo)

    try:
        # 1. weight_bcs 복합 데이터 처리
        if category == "weight_bcs":
            logs = service.register_weight_bcs_bulk(
                customer_id=customer_id,
                pet_id=pet_id,
                weight=request.weight,
                bcs=request.bcs,
                log_date=request.log_date,
                memo=request.memo
            )
            return {
                "status": "success",
                "message": "✅ 체중 및 BCS 기록이 등록되었습니다.",
                "data": [NumericLogResponse.from_orm_model(l).model_dump() for l in logs]
            }

        # 2. 단일 카테고리 처리 (walk, poop 등)
        else:
            if request.log_status is None:
                raise HTTPException(status_code=400, detail="log_status 값이 필요합니다.")
            
            log, is_duplicate = service.register_numeric_log(
                customer_id=customer_id,
                pet_id=pet_id,
                category=category,
                log_status=request.log_status,
                log_date=request.log_date,
                memo=request.memo
            )
            return {
                "status": "success",
                "message": f"{category} 기록이 등록되었습니다.",
                "data": NumericLogResponse.from_orm_model(log).model_dump(),
                "warning": "중복된 기록이 존재합니다." if is_duplicate else None
            }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{pet_log_numeric_id}")
def update_numeric_log(
    pet_log_numeric_id: int,
    request: NumericLogUpdate,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[수정] 수치형 기록 수정"""
    repo = PetLogRepository(db)
    service = PetLogService(repo)
    
    log = service.get_numeric_log(pet_log_numeric_id)
    if not log or not check_pet_owner(db, log.pet_id, customer_id):
        raise HTTPException(status_code=403, detail="접근 권한이 없거나 기록을 찾을 수 없습니다.")

    try:
        updated_log = service.update_numeric_log(pet_log_numeric_id, request.model_dump(exclude_unset=True))
        return {
            "status": "success",
            "message": "기록이 수정되었습니다.",
            "data": NumericLogResponse.from_orm_model(updated_log).model_dump()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{pet_log_numeric_id}")
def delete_numeric_log(
    pet_log_numeric_id: int,
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """[삭제] 수치형 기록 소프트 딜리트 (active=False)"""
    repo = PetLogRepository(db)
    service = PetLogService(repo)
    
    log = service.get_numeric_log(pet_log_numeric_id)
    if not log or not check_pet_owner(db, log.pet_id, customer_id):
        raise HTTPException(status_code=403, detail="접근 권한이 없거나 기록을 찾을 수 없습니다.")

    service.delete_numeric_log(pet_log_numeric_id)
    return {"status": "success", "message": "기록이 삭제되었습니다."}
