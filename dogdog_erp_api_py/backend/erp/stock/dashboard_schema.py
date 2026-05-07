from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpStockDashboardStatusBox(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str
    count_text: str
    count: int
    subtitle: str
    rows: list[Any]


class ErpStockDashboardTopStockItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    action_text: str
    product_id: Any = None
    purchase_price: Any = None
    retail_price: Any = None
    rows: list[Any]


class ErpStockDashboardTopStockSection(BaseModel):
    title: str
    items: list[ErpStockDashboardTopStockItem]


class ErpStockDashboardData(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_year: int
    current_month: int
    current_month_text: str
    month_start: str
    month_end: str
    status_box_data: list[ErpStockDashboardStatusBox]
    chart_data: list[Any]
    total_stock_quantity: int
    total_stock_quantity_text: str
    expiring_stock_count: int = 0
    expiring_stock_count_text: str = "0건"
    expiring_stock_days: int = 30
    top_stock_section_data: ErpStockDashboardTopStockSection


class ErpStockDashboardResponse(BaseModel):
    success: bool
    message: str
    data: ErpStockDashboardData
