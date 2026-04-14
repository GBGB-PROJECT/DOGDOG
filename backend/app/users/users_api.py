from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import EmailStr

from db.db import get_db

from backend.app.users.id_repository import get_customer_by_id, get_pet_id  # 가정: 토큰에서 customer_id 추출

router = APIRouter(tags=["users"])

@router.get("/users/id")
def read_my_id_info(
    email: EmailStr = Query(
            default=None,
            # max_length=50,
            description="이메일"
        ),
    db: Session = Depends(get_db),
):
    """
    로그인한 사용자의 customer_id, pet_id 조회
    """

    try:
        # 1. customer 존재 확인
        customer_id = get_customer_by_id(db=db, email=email)
        if customer_id is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "success": False,
                    "error_code": "CUSTOMER_NOT_FOUND",
                    "message": "존재하지 않는 사용자입니다."
                }
            )

        # 2. pet 조회
        pet_ids = get_pet_id(db=db, customer_id=customer_id)
        pets = [{"pet_id": pet_id} for pet_id in pet_ids]

        # 3. 응답 반환
        return {
            "success": True,
            "message": "ID 정보를 조회했습니다.",
            "data": {
                "customer_id": customer_id,
                "pets": pets
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ID 정보 조회 실패:", e)

        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "ID_READ_FAILED",
                "message": "ID 정보 조회에 실패했습니다."
            }
        )