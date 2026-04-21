from pydantic import BaseModel, HttpUrl, Field, field_validator
from typing import List, Optional
from datetime import datetime

class PetRegisterRequest(BaseModel):
    nickname: str = Field(..., min_length=1, max_length=10, description="1-10자, 공백만 있는 문자열 차단")
    birth_day: str = Field(..., description="YYYY-MM-DD 또는 YYYY-MM")
    profile_image: Optional[HttpUrl] = Field(None, description="프로필 이미지 URL")
    breed_id: int = Field(..., gt=0, description="1 이상의 양수 품종 아이디")
    sex_and_neuter: int = Field(..., ge=1, le=4, description="1:M/F, 2:M/T, 3:F/F, 4:F/T")
    weight: float = Field(..., gt=0, lt=200, description="0 초과 200 미만 (kg)")
    bcs: int = Field(..., ge=1, le=9, description="1-9 사이의 정수 입력")
    daily_walk: int = Field(..., ge=0, le=2, description="산책 지표 0, 1, 2")
    feeding_count: List[str] = Field(..., description="급여 시점 배열")
    feeding_intake: Optional[int] = Field(None)
    water_intake: Optional[int] = Field(None)
    supps: Optional[List[str]] = Field(default_factory=list)
    medication: Optional[List[str]] = Field(default_factory=list)
    allergies: Optional[List[str]] = Field(default_factory=list)
    diseases: Optional[List[str]] = Field(default_factory=list)

    @field_validator("nickname")
    @classmethod
    def nickname_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("공백만 있는 문자열은 사용할 수 없습니다.")
        return v

    @field_validator("birth_day")
    @classmethod
    def validate_birth_day(cls, v: str) -> str:
        parts = v.split("-")
        if len(parts) == 2:
            return f"{v}-01"
        return v

    @field_validator("supps", "medication", "allergies", "diseases", mode="before")
    @classmethod
    def none_to_empty_list(cls, v):
        if v is None:
            return []
        return v

class PetRegisterData(BaseModel):
    pet_id: int
    nickname: str
    breed_id: int
    create_date: str
    self: str

class PetRegisterResponse(BaseModel):
    success: bool
    message: str
    data: PetRegisterData
