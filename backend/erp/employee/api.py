from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from .service import (
    count_employees,
    fetch_employees,
    fetch_employee_positions,
    create_employee,
)


router = APIRouter(
    prefix="/erp/employee",
    tags=["employee"],
)


class EmployeeCreateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    employee_id: int
    account_id: str
    password: str
    username: str
    hire_date: str
    quit_date: Optional[str] = None
    emp_position_id: Optional[int] = None
    manager_id: Optional[int] = None
    email: str
    phone: str
    address: str
    postal_code: str
    active: bool | str = True


@router.get("")
def get_employees(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=50, ge=1, le=200),
    search_type: str = Query(default="username"),
    keyword: str = Query(default=""),
    start_date: Optional[str] = Query(default=None),
    end_date: Optional[str] = Query(default=None),
):
    offset = (page - 1) * size
    total_count = count_employees(
        search_type=search_type,
        keyword=keyword,
        start_date=start_date,
        end_date=end_date,
    )
    rows = fetch_employees(
        search_type=search_type,
        keyword=keyword,
        limit=size,
        offset=offset,
        start_date=start_date,
        end_date=end_date,
    )

    return {
        "items": rows,
        "total_count": total_count,
        "page": page,
        "size": size,
        "total_pages": (total_count + size - 1) // size if total_count else 1,
    }


@router.get("/positions")
def get_employee_positions():
    return {
        "items": fetch_employee_positions(),
    }


@router.post("")
def post_employee(payload: EmployeeCreateRequest):
    try:
        created = create_employee(payload.model_dump())
        return {
            "message": "사원 정보가 등록되었습니다.",
            "item": created,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
