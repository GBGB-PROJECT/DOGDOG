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


class ErpProductionPurchaseOrderDetail(BaseModel):
    model_config = ConfigDict(extra="allow")

    purchase_order_id: Any = None
    supplier_id: Any = None
    supplier_name: Any = None
    supplier_brn: Any = None
    supplier_phone: Any = None
    supplier_manager: Any = None
    contract_date: Any = None
    inbound_scheduled_date: Any = None
    pay_status: Any = None
    adjustment_date: Any = None
    is_purchase_order_cancel: Any = None
    employee_id: Any = None
    order_form_file_path: Any = None
    last_update: Any = None


class ErpProductionPurchaseOrderLineItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    purchase_order_id: Any = None
    product_id: Any = None
    storage_method: Any = None
    quantity: Any = None
    purchase_price: Any = None
    total_amount: Any = None
    defective: Any = None
    final_amount: Any = None
    memo: Any = None
    last_update: Any = None
    weight: Any = None
    product_quantity: Any = None
    product_name: Any = None
    product_type: Any = None
    brand: Any = None


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


class ErpProductionPurchaseOrderDetailData(BaseModel):
    item: ErpProductionPurchaseOrderDetail | None = None


class ErpProductionPurchaseOrderDetailResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionPurchaseOrderDetailData


class ErpProductionPurchaseOrderItemsData(BaseModel):
    items: list[ErpProductionPurchaseOrderLineItem]


class ErpProductionPurchaseOrderItemsResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionPurchaseOrderItemsData
