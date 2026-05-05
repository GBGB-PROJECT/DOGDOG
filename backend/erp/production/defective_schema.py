from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpProductionDefectiveItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int
    inbound_id: Any = None
    purchase_order_id: Any = None
    supplier_id: Any = None
    supplier_name: str = ""
    inbound_status: str = ""
    product_id: Any = None
    product_detail_id: Any = None
    product_no: Any = None
    brand: str = ""
    product_name: str = ""
    weight: Any = None
    weight_text: str = ""
    defective: Any = None
    purchase_price: Any = None
    defective_amount: Any = None
    inbound_scheduled_date: str = ""
    inbound_start: str = ""
    inbound_complete: str = ""
    employee_id: Any = None
    last_update: str = ""


class ErpProductionDefectivePagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpProductionDefectiveSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str = ""
    start_date: Any = None
    end_date: Any = None


class ErpProductionDefectiveData(BaseModel):
    items: list[ErpProductionDefectiveItem]
    pagination: ErpProductionDefectivePagination
    search: ErpProductionDefectiveSearch


class ErpProductionDefectiveListResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionDefectiveData
