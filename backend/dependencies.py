from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionPet, CompanionButler, OpdProduct


# 존재하는 펫인지 확인
# 펫아이디 가져오기
def get_pet_by_id(db: Session, pet_id: int):
    query = select(CompanionPet).where(CompanionPet.pet_id == pet_id)
    result = db.execute(query)

    return result.scalar_one_or_none()


# 로그인 사용자가 해당 반려견의 보호자인지 확인
# Butler row 존재 여부 가져오기
def check_pet_owner(db: Session, pet_id: int, customer_id: int) -> bool:
    query = select(CompanionButler).where(
        CompanionButler.pet_id == pet_id,
        CompanionButler.customer_id == customer_id,
        CompanionButler.active == True,
    )
    result = db.execute(query)
    butler = result.scalar_one_or_none()
    return butler is not None  # T/F


# 존재하는 사료인지 확인
def get_product_by_id(db: Session, product_id: int):
    query = select(OpdProduct).where(OpdProduct.product_id == product_id)
    result = db.execute(query)
    return result.scalar_one_or_none()


from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    현재 요청에 포함된 Access Token을 검증하고 customer_id를 반환합니다.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        customer_id_str: str = payload.get("sub")
        if customer_id_str is None:
            raise credentials_exception

        # Access 토큰인지 확인 (Refresh 토큰으로 인증하는 것 방지)
        token_type = payload.get("type", "access")
        if token_type == "refresh":
            raise credentials_exception

        return int(customer_id_str)
    except getattr(jwt, "JWTError", Exception):
        raise credentials_exception
