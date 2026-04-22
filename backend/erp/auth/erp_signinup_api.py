from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.db import SessionLocal
from erp.auth.erp_signinup_service import AuthService

router = APIRouter(prefix="/auth", tags=["로그인 인증"])

# Swagger에 보일 입력 양식 정의
class LoginRequest(BaseModel):
    account_id: str = Field(..., example="account1")
    email: str = Field(..., example="emp1@test.com")
    password: str = Field(..., example="hashed_pw")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login")
def login_employee(request: LoginRequest, db: Session = Depends(get_db)):
    """Swagger에서 3가지 정보를 입력받아 검증합니다."""
    service = AuthService(db)
    
    # 서비스로부터 (결과 코드, 메시지) 튜플을 받습니다.
    status_code, error_code ,message = service.verify_login(
        request.account_id, request.email, request.password
    )
    
    if status_code != 200:
        return JSONResponse(
            status_code=status_code, # 401, 404 등 숫자로 된 에러 번호
            content={                # 실제 화면에 찍힐 JSON 내용
                "success": False,
                "code": error_code, # 예: FAIL_EMAIL
                "msg": message            # 예: 등록된 이메일이 아닙니다
            }
        )
    
    # 모든 검증 통과 시 (200 OK)
    return {"success": True, "code":status_code ,"msg": message}