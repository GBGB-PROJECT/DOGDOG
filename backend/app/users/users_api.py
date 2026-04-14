from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from db.database import get_db
from domains.id.repository import (
    get_customer_by_id,
    get_pet_by_customer_id,
)
from utils.auth import get_current_customer_id


router = APIRouter(
    prefix="/api/v1/id",
    tags=["ID"]
)


@router.get("")
def read_my_id_info(
    customer_id: int = Depends(get_current_customer_id),
    db: Session = Depends(get_db),
):
    """
    로그인한 사용자의 customer_id, pet_id 조회
    """

    try:
        # 1. customer 존재 확인
        customer = get_customer_by_id(db=db, customer_id=customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "message": "존재하지 않는 사용자입니다."
                }
            )

        # 2. pet 조회
        pet = get_pet_by_customer_id(db=db, customer_id=customer_id)
        if pet is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error_code": "PET_NOT_FOUND",
                    "message": "등록된 반려견 정보가 없습니다."
                }
            )

        # 3. 응답 반환
        return {
            "success": True,
            "message": "ID 정보를 조회했습니다.",
            "data": {
                "customer_id": customer.customer_id,
                "pet_id": pet.pet_id
            }
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "error_code": "ID_READ_FAILED",
                "message": "ID 정보 조회에 실패했습니다."
            }
        )