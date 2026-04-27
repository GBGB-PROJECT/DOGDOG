from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpStockProductDetailItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    product_id: Any = None
    brand: Any = None
    product_name: Any = None
    expiration_date: Any = None
    inbound_id: Any = None
    inbound_status: Any = None
    save_stock: Any = None
    sale_stock: Any = None
    stock_available: Any = None
    scrap_stock: Any = None
    last_update: Any = None


class ErpStockProductDetailPagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpStockProductDetailSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpStockProductDetailData(BaseModel):
    items: list[ErpStockProductDetailItem]
    pagination: ErpStockProductDetailPagination
    search: ErpStockProductDetailSearch


class ErpStockProductDetailListResponse(BaseModel):
    success: bool
    message: str
    data: ErpStockProductDetailData
