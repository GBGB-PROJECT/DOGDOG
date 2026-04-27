from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpProductionPurchaseOrderItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    purchase_order_id: Any = None
    supplier_id: Any = None
    supplier_name: Any = None
    contract_date: Any = None
    inbound_scheduled_date: Any = None
    pay_status: Any = None
    adjustment_date: Any = None
    is_purchase_order_cancel: Any = None
    employee_id: Any = None
    order_form_file_path: Any = None
    item_count: Any = None
    final_amount_sum: Any = None
    last_update: Any = None


class ErpProductionPurchaseOrderPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpProductionPurchaseOrderSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    date_type: str
    date_type_label: str
    start_date: Any = None
    end_date: Any = None


class ErpProductionPurchaseOrderData(BaseModel):
    items: list[ErpProductionPurchaseOrderItem]
    pagination: ErpProductionPurchaseOrderPagination
    search: ErpProductionPurchaseOrderSearch


class ErpProductionPurchaseOrderListResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionPurchaseOrderData


class ErpProductionPurchaseOrderDetailResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


class ErpProductionPurchaseOrderItemsResponse(BaseModel):
    success: bool
    message: str
    data: list[dict[str, Any]]
