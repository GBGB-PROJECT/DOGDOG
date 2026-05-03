from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpCustomerSubscriptionItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    subs_id: Any = None
    customer_id: Any = None
    subs_date: Any = None
    subs_plan_id: Any = None
    is_auto_delivery: Any = None
    is_subs_status: Any = None
    subs_day: Any = None
    delivery_cycle: Any = None
    subs_sale: Any = None
    address: Any = None
    name: Any = None
    phone: Any = None
    product_id: Any = None
    product_ids: Any = None
    product_brand: Any = None
    product_name: Any = None
    subscription_product: Any = None
    subscription_products: Any = None
    item_quantity: Any = None
    total_quantity: Any = None
    item_final_amount: Any = None
    total_final_amount: Any = None


class ErpCustomerSubscriptionPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpCustomerSubscriptionSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpCustomerSubscriptionData(BaseModel):
    items: list[ErpCustomerSubscriptionItem]
    pagination: ErpCustomerSubscriptionPagination
    search: ErpCustomerSubscriptionSearch


class ErpCustomerSubscriptionListResponse(BaseModel):
    success: bool
    message: str
    data: ErpCustomerSubscriptionData
