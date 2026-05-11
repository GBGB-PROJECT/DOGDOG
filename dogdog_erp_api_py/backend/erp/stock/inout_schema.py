from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpStockInoutItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    inout_type: Any = None
    base_id: Any = None
    inbound_id: Any = None
    sales_order_id: Any = None
    product_id: Any = None
    product_detail_id: Any = None
    product_no: Any = None
    brand: Any = None
    product_name: Any = None
    weight: Any = None
    weight_text: Any = None
    quantity: Any = None
    quantity_text: Any = None
    unit_price: Any = None
    unit_price_text: Any = None
    amount: Any = None
    amount_text: Any = None
    event_date: Any = None
    status: Any = None


class ErpStockInoutPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpStockInoutData(BaseModel):
    model_config = ConfigDict(extra="allow")

    items: list[ErpStockInoutItem]
    pagination: ErpStockInoutPagination


class ErpStockInoutListResponse(BaseModel):
    success: bool
    message: str
    data: ErpStockInoutData
