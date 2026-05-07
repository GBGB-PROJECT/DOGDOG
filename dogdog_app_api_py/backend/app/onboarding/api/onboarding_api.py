from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.onboarding.api.schemas import OnboardingRequest
from backend.app.onboarding.service.onboarding_service import OnboardingService
from db.db import get_db

router = APIRouter(prefix="/api/v1/onboarding", tags=["Onboarding"])

@router.post("")
def post_onboarding(
    request: OnboardingRequest,
    db: Session = Depends(get_db)
):
    """
    [통합 온보딩] 유저 생성 + 반려견 생성 + 사료 등록을 한 번에 처리합니다.
    """
    service = OnboardingService(db)
    result = service.complete_onboarding(request)
    return result
