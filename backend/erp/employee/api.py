from typing import Optional, Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from .service import (
    count_employees,
    fetch_employees,
    create_employee,
)


router = APIRouter(
    prefix="/erp/employee",
    tags=["employee"],
)


SEARCH_TYPE_LABELS = {
    "username": "이름",
    "employee_id": "사원ID",
    "account_id": "계정ID",
    "position_name": "직책",
    "phone": "전화번호",
    "email": "이메일",
    "hire_date": "입사일",
}


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


@router.get(
    "",
    summary="사원 목록 조회",
    description=(
        "인사관리 화면에서 사용하는 사원 목록 조회 API입니다. "
        "employee와 emp_position을 JOIN하여 직책명을 함께 반환합니다."
    ),
)
def get_employees(
    # 🔥 수정: Swagger에서 검색조건이 맨 위에 오도록 page/size보다 먼저 배치
    search_type: Literal[
        "username",
        "employee_id",
        "account_id",
        "position_name",
        "phone",
        "email",
        "hire_date",
    ] = Query(
        default="username",
        description="검색 조건",
        examples=["username"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["직원1"],
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호",
        examples=[1],
    ),
    size: int = Query(
        default=50,
        ge=1,
        le=200,
        description="페이지당 조회 건수",
        examples=[50],
    ),
    start_date: date | None = Query(
        default=None,
        description="입사일 시작일",
        examples=["2025-01-01"],
    ),
    end_date: date | None = Query(
        default=None,
        description="입사일 종료일",
        examples=["2025-12-31"],
    ),
):
    try:
        clean_search_type = (search_type or "username").strip()
        clean_keyword = (keyword or "").strip()

        offset = (page - 1) * size

        total_count = count_employees(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        rows = fetch_employees(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "success": True,
            "message": "사원 목록 조회에 성공했습니다." if total_count else "일치하는 정보가 없습니다.",
            "data": {
                "items": rows,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total_count": total_count,
                    "total_pages": (total_count + size - 1) // size if total_count else 1,
                },
                "search": {
                    "search_type": clean_search_type,
                    "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                    "keyword": clean_keyword,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "EMPLOYEE_LIST_FAILED",
                "message": f"사원 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )


@router.post(
    "",
    summary="사원 등록",
    description="인사관리 화면의 등록 모달에서 사용하는 사원 등록 API입니다.",
)
def post_employee(payload: EmployeeCreateRequest):
    try:
        created = create_employee(payload.model_dump())
        return {
            "success": True,
            "message": "사원 정보가 등록되었습니다.",
            "data": created,
        }
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "EMPLOYEE_CREATE_FAILED",
                "message": str(exc),
            },
        ) from exc
