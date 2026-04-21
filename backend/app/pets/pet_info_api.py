from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.db import get_db

from backend.app.domains.pets.api.pet_info_api import PetService
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/pets/{customer_id}")
async def get_pet_info(customer_id: int, db: Session = Depends(get_db)):
    try:
        # 서비스 계층 호출
        results = PetService.get_pet_list_with_profile(db, customer_id)

        if not results:
            # 데이터가 없을 때는 404 에러
            raise HTTPException(status_code=404, detail="해당 고객의 반려동물이 없습니다.")
        
        return {
            "status": "success",
            "message": "고객 반려동물 추출 완료",
            "data": results
        }

    except HTTPException as he:
        raise he
    # except Exception as e:
    #     # 그 외 예상치 못한 에러 처리
    #     raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

    except Exception as e:
        print(f"반려견 목록 조회 실패: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error_code": "PET_INFO_READ_FAILED",
                "message": "반려견 목록 조회에 실패했습니다."
            }
        )