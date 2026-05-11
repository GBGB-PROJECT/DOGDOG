from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import CompanionPet, CompanionButler, OpdProduct, CompanionCustomer
from db.db import get_db

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


from fastapi import Depends, HTTPException, status, Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from backend.app.config import JWT_SECRET_KEY, JWT_ALGORITHM

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """
    HTTP Bearer Token을 추출하여 검증하고 DB 활성화 상태를 거쳐 customer_id를 반환합니다.
    (Refresh Token 접근 차단 및 유저 상태 확인 로직 통합)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        customer_id_str: str = payload.get("sub")
        if customer_id_str is None:
            raise credentials_exception

        # Access 토큰인지 확인 (Refresh 토큰으로 인증 방지)
        token_type = payload.get("type", "access")
        if token_type == "refresh":
            raise credentials_exception

        customer_id = int(customer_id_str)

    except (getattr(jwt, "JWTError", Exception), ValueError):
        raise credentials_exception

    user = (
        db.query(CompanionCustomer)
        .filter(
            CompanionCustomer.customer_id == customer_id,
            CompanionCustomer.active == True,
        )
        .first()
    )

    if user is None:
        raise credentials_exception

    return user.customer_id


async def verify_pet_owner(
    pet_id: int = Path(..., description="반려견 고유 ID"),
    customer_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> int:
    """로그인한 유저가 해당 pet_id의 소유주인지 검증하는 의존성 주입 함수"""
    if not check_pet_owner(db, pet_id, customer_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 반려동물에 대한 접근 권한이 없습니다.",
        )
    return pet_id
