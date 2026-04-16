from pydantic import BaseModel, Field, field_validator
from typing import Optional
import re


class EmailSignupRequest(BaseModel):
    email: str = Field(..., max_length=255, description="이메일 형식, 255자 이내")
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="최소 8자 이상, 영문/숫자/특수문자 포함",
    )
    nickname: str = Field(
        ..., min_length=2, max_length=10, description="2~10자, 공백 불가"
    )
    phone: Optional[str] = Field(
        None, max_length=13, description="하이픈 포함 최대 13자"
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        # 기본 이메일 정규식 검사
        if not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", v):
            raise ValueError("올바른 이메일 형식이 아닙니다.")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        # 영문, 숫자, 특수문자(!@#$%^&*) 각 1회 이상
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("비밀번호는 영문자를 최소 1회 이상 포함해야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호는 숫자를 최소 1회 이상 포함해야 합니다.")
        if not re.search(r"[\!@#$%^&\*]", v):
            raise ValueError(
                "비밀번호는 특수문자(!@#$%^&*)를 최소 1회 이상 포함해야 합니다."
            )
        return v

    @field_validator("nickname")
    @classmethod
    def validate_nickname(cls, v: str) -> str:
        if " " in v:
            raise ValueError("닉네임에 공백을 포함할 수 없습니다.")
        return v

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\d{2,3}-\d{3,4}-\d{4}$", v):
            raise ValueError("올바른 전화번호 형식이 아닙니다.")
        return v


class SignupDataFormat(BaseModel):
    customer_id: int
    email: str
    nickname: str


class AuthorizationFormat(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class SignupResponse(BaseModel):
    status: str
    message: str
    data: SignupDataFormat
    authorization: AuthorizationFormat

class LoginRequest(BaseModel):
    email: str = Field(..., description="이메일")
    password: str = Field(..., description="비밀번호")

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., description="재발급을 위한 리프레시 토큰")
