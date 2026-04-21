from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from db.db import get_db
from db.models import CompanionCustomer
from app.config import JWT_SECRET_KEY, JWT_ALGORITHM

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> int:
    """
    HTTP Bearer Token을 추출하여 검증하고 customer_id를 반환합니다.
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

        customer_id = int(customer_id_str)

    except (JWTError, ValueError):
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
