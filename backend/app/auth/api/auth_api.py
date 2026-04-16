from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

from db.db import get_db
from app.auth.schemas import EmailSignupRequest, SignupResponse
from app.auth.service.auth_service import AuthService
from app.auth.repository.auth_repository import AuthRepository

logger = logging.getLogger(__name__)

# 라우터 내부에 prefix와 tags 선언
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post(
    "/signup/local", status_code=status.HTTP_201_CREATED, response_model=SignupResponse
)
def email_signup(request: EmailSignupRequest, db: Session = Depends(get_db)):
    """[가입] 이메일 기반 신규 회원 가입 처리 및 JWT 토큰을 발급합니다."""
    repo = AuthRepository(db)
    service = AuthService(repo)

    try:
        result = service.register_user(request)

        detail = result["customer"]
        return SignupResponse(
            status="success",
            message="사용자 정보가 등록되었습니다.",
            data={
                "customer_id": detail.customer_id,
                "email": detail.email,
                "nickname": detail.nickname,
            },
            authorization={
                "access_token": result["access_token"],
                "refresh_token": result["refresh_token"],
                "token_type": "bearer",
                "expires_in": result["expires_in"],
            },
        )
    except ValueError as val_e:
        if str(val_e) == "EMAIL_ALREADY_EXISTS":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="이미 가입된 이메일입니다."
            )
        # 패스워드 정규식 오류 등 Pydantic에서 에러를 던지지만(비정상 케이스 대비)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(val_e))
    except Exception as e:
        logger.error(f"회원 가입 중 오류 발생: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버 통신 중 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
        )
