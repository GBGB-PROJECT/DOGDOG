from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class NumericLogBase(BaseModel):
    """수치형 기록의 기본 필드 정의"""
    log_status: Optional[float] = Field(None, description="단일 수치값 (배변점수, 산책시간 등)")
    weight: Optional[float] = Field(None, ge=0.1, le=200.0, description="체중 (kg)")
    bcs: Optional[int] = Field(None, ge=1, le=9, description="BCS 점수 (1~9)")
    log_date: datetime = Field(..., description="기록 발생 일시")
    memo: Optional[str] = Field(None, max_length=200, description="메모")

class NumericLogCreate(NumericLogBase):
    """등록 요청용 스키마"""
    pass

class NumericLogUpdate(BaseModel):
    """수정 요청용 스키마"""
    log_status: Optional[float] = None
    log_date: Optional[datetime] = None
    memo: Optional[str] = None

class NumericLogResponse(BaseModel):
    """응답용 스키마"""
    pet_log_numeric_id: int
    pet_id: int
    customer_id: int
    category: str
    log_status: float
    log_date: str
    memo: Optional[str] = None
    active: bool = True
    last_update: str

    @classmethod
    def from_orm_model(cls, log) -> "NumericLogResponse":
        return cls(
            pet_log_numeric_id=log.pet_log_numeric_id,
            pet_id=log.pet_id,
            customer_id=log.customer_id,
            category=log.category,
            log_status=float(log.log_status) if log.log_status else 0.0,
            log_date=log.log_date.strftime("%Y-%m-%d %H:%M:%S") if log.log_date else "",
            memo=log.memo,
            active=log.active,
            last_update=log.last_update.strftime("%Y-%m-%d %H:%M:%S") if log.last_update else "",
        )
