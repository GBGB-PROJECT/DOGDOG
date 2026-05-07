from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpCustomerInfoItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    customer_id: Any = None
    email: Any = None
    oauth_type: Any = None
    nickname: Any = None
    phone: Any = None
    is_subscribed: Any = None
    subs_count: Any = None
    active: Any = None
    create_date: Any = None


class ErpCustomerInfoPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpCustomerInfoSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpCustomerInfoData(BaseModel):
    items: list[ErpCustomerInfoItem]
    pagination: ErpCustomerInfoPagination
    search: ErpCustomerInfoSearch


class ErpCustomerInfoListResponse(BaseModel):
    success: bool
    message: str
    data: ErpCustomerInfoData
