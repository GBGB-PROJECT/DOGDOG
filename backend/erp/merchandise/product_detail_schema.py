from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpMerchandiseDetailItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    product_no: Any = None
    product_detail_id: Any = None
    product_id: Any = None
    type: Any = None
    brand: Any = None
    product_name: Any = None
    function: Any = None
    main_protein: Any = None
    life: Any = None
    weight: Any = None
    retail_price: Any = None
    quantity: Any = None
    active: Any = None


class ErpMerchandiseDetailPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpMerchandiseDetailSearch(BaseModel):
    search_type: str
    search_type_label: str
    keyword: str


class ErpMerchandiseDetailData(BaseModel):
    items: list[ErpMerchandiseDetailItem]
    pagination: ErpMerchandiseDetailPagination
    search: ErpMerchandiseDetailSearch


class ErpMerchandiseDetailListResponse(BaseModel):
    success: bool
    message: str
    data: ErpMerchandiseDetailData
