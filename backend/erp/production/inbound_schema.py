from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpProductionInboundItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    inbound_id: Any = None
    purchase_order_id: Any = None
    supplier_id: Any = None
    supplier_name: Any = None
    inbound_status: Any = None
    inbound_scheduled_date: Any = None
    inbound_start: Any = None
    inbound_complete: Any = None
    employee_id: Any = None
    last_update: Any = None


class ErpProductionInboundPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpProductionInboundSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpProductionInboundData(BaseModel):
    items: list[ErpProductionInboundItem]
    pagination: ErpProductionInboundPagination
    search: ErpProductionInboundSearch


class ErpProductionInboundListResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionInboundData
