from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CalcFeedingRecommendationData(BaseModel):
    pet_id: int
    base_intake: float
    guide_intake: float
    guide_date: Optional[str]
    feeding_count: int
    base_per_meal_g: float
    guide_per_meal_g: float
    adjustment_ratio: float
    adjustment_rate: float
    adjustment_reason: str
    recommend_kcal: float
    goal_weight: float
    kcal_per_kg: Optional[float] = None
    daily_total_kcal: Optional[float] = None

class CalcFeedingRecommendationResponse(BaseModel):
    success: bool
    message: str
    data: CalcFeedingRecommendationData

class GuideIntakeData(BaseModel):
    pet_id: int
    base_daily_food_g: float
    adjusted_daily_food_g: float
    adjusted_per_meal_g: str
    feeding_count: int
    recommended_at: datetime
    kcal_per_kg: Optional[float] = None
    daily_total_kcal: Optional[float] = None

class GuideIntakeResponse(BaseModel):
    success: bool
    message: str
    data: GuideIntakeData

class OneTimeFeedingData(BaseModel):
    pet_id: int
    guide_intake: float
    feeding_count: int
    one_time_intake: float

class OneTimeFeedingResponse(BaseModel):
    success: bool
    message: str
    data: OneTimeFeedingData
