from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpProductionDashboardStatusBox(BaseModel):
    model_config = ConfigDict(extra="allow")

    title: str
    count_text: str
    count: int
    subtitle: str
    rows: list[Any]


class ErpProductionDashboardPurchaseItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    name: str
    action_text: str
    purchase_order_id: Any = None
    rows: list[Any]


class ErpProductionDashboardPurchaseSection(BaseModel):
    title: str
    items: list[ErpProductionDashboardPurchaseItem]


class ErpProductionDashboardData(BaseModel):
    model_config = ConfigDict(extra="allow")

    current_year: int
    current_month: int
    current_month_text: str
    month_start: str
    month_end: str
    status_box_data: list[ErpProductionDashboardStatusBox]
    chart_data: list[Any]
    top_production_section_data: ErpProductionDashboardPurchaseSection


class ErpProductionDashboardResponse(BaseModel):
    success: bool
    message: str
    data: ErpProductionDashboardData
