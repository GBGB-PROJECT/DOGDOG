from pydantic import BaseModel, Field
from typing import Optional
from datetime import date

class UserCreate(BaseModel):
    email: str
    password: Optional[str] = None
    nickname: str = Field(..., max_length=10)
    phone: Optional[str] = Field(None, max_length=13)
    oauth_type: Optional[str] = Field("local", max_length=6)

class PetCreate(BaseModel):
    nickname: str = Field(..., max_length=10)
    birth_day: Optional[date] = None
    breed_id: int
    sex: int = Field(..., description="1: 남아, 2: 여아")
    is_neutered: bool
    weight: float
    bcs: int
    daily_walks: int
    feeding_count: int

class FoodCreate(BaseModel):
    product_id: int
    total_weight: int = Field(..., description="사료 총 용량(g)")
    #one_gram_calories: Optional[float] = Field(None, description="1g당 칼로리")

class OnboardingRequest(BaseModel):
    user: UserCreate
    pet: PetCreate
    food: FoodCreate
