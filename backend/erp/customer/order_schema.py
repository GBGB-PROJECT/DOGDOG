from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpCustomerOrderItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    order_number: Any = None
    order_date: Any = None
    sales_order_id: Any = None
    customer_id: Any = None
    recipient: Any = None
    phone: Any = None
    address: Any = None
    product_id: Any = None
    product_detail_id: Any = None
    product_brand: Any = None
    product_name: Any = None
    product_weight: Any = None
    product_unit_quantity: Any = None
    quantity: Any = None
    retail_price: Any = None
    total_amount: Any = None
    payment_billing_id: Any = None


class ErpCustomerOrderPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpCustomerOrderSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpCustomerOrderData(BaseModel):
    items: list[ErpCustomerOrderItem]
    pagination: ErpCustomerOrderPagination
    search: ErpCustomerOrderSearch


class ErpCustomerOrderListResponse(BaseModel):
    success: bool
    message: str
    data: ErpCustomerOrderData
