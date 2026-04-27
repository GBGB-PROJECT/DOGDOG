from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpProductionSupplierItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    supplier_id: Any = None
    supplier_name: Any = None
    brn: Any = None
    is_contact_status: Any = None
    designated_payment_date: Any = None
    scheduled_payment_date: Any = None
    employee_id: Any = None
    memo: Any = None
    sup_manager: Any = None
    phone: Any = None
    last_update: Any = None


class ErpProductionSupplierPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpProductionSupplierSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpProductionSupplierData(BaseModel):
    items: list[ErpProductionSupplierItem]
    pagination: ErpProductionSupplierPagination
    search: ErpProductionSupplierSearch


class ErpProductionSupplierListResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionSupplierData
