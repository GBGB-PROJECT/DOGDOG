from typing import Any
from pydantic import BaseModel, ConfigDict


class ErpHrEmployeeItem(BaseModel):
    model_config = ConfigDict(extra="allow")

    no: int | None = None
    employee_id: Any = None
    account_id: Any = None
    username: Any = None
    position_name: Any = None
    phone: Any = None
    email: Any = None
    hire_date: Any = None
    quit_date: Any = None
    manager_id: Any = None
    address: Any = None
    postal_code: Any = None
    active: Any = None


class ErpHrEmployeePagination(BaseModel):
    page: int
    size: int
    total_count: int
    total_pages: int


class ErpHrEmployeeSearch(BaseModel):
    model_config = ConfigDict(extra="allow")

    search_type: str
    search_type_label: str
    keyword: str
    start_date: Any = None
    end_date: Any = None


class ErpHrEmployeeData(BaseModel):
    items: list[ErpHrEmployeeItem]
    pagination: ErpHrEmployeePagination
    search: ErpHrEmployeeSearch


class ErpHrEmployeeListResponse(BaseModel):
    success: bool
    message: str
    data: ErpHrEmployeeData
