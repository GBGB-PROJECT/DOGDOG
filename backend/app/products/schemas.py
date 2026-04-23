from pydantic import BaseModel
from typing import List, Optional

class ProductListItemData(BaseModel):
    product_detail_id: int
    product_name: str
    
class ProductListResponse(BaseModel):
    success: bool
    message: str
    data: List[ProductListItemData]

class ProductWeightItemData(BaseModel):
    product_id: int
    weight: float
    active: bool

class ProductWeightResponse(BaseModel):
    success: bool
    message: str
    data: List[ProductWeightItemData]
