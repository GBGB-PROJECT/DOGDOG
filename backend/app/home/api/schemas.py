"""홈 대시보드 API 응답 스키마 (Pydantic V2)"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class PetInfoResponse(BaseModel):
    """반려동물 프로필 정보"""
    nickname: str
    profile_image: str


class FeedingStatsResponse(BaseModel):
    """일일 급여 통계"""
    current_kcal: float = 0
    target_kcal: float = 0
    current_amount: float = 0
    target_amount: float = 0
    progress_rate: float = 0


class FoodInventoryResponse(BaseModel):
    """사료 재고 현황"""
    left_percent: float = 0
    left_intake: float = 0
    total_weight: float = 0
    left_food_count: float = 0
    expected_exdate: Optional[str] = None


class ActivityStatsResponse(BaseModel):
    """오늘자 활동량 통계 (물, 산책)"""
    water_total: float = 0
    walk_total: float = 0


class DashboardDataResponse(BaseModel):
    """대시보드 종합 데이터"""
    query_date: str
    pet_info: PetInfoResponse
    feeding_stats: FeedingStatsResponse
    food_inventory: FoodInventoryResponse
    activity_stats: ActivityStatsResponse
    current_food_info: Optional[Dict[str, Any]] = None


class DashboardResponse(BaseModel):
    """대시보드 API 최상위 응답"""
    status: str
    data: DashboardDataResponse
