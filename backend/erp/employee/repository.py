from sqlalchemy import cast
from sqlalchemy.types import String

from backend.db.db import SessionLocal
from backend.db.models import ErpEmployee
from backend.erp.common.query_utils import model_to_dict, like_keyword


# =========================================================
# ☑️ 인사관리 Repository
# - ERP.employee ORM 모델 기반 조회
# - 이름 / 사원ID / 계정ID / 직급ID / 전화번호 / 이메일 검색 처리
# - count + limit/offset 페이지네이션 처리
# =========================================================

EMPLOYEE_COLUMNS = [
    "employee_id",
    "account_id",
    "username",
    "hire_date",
    "quit_date",
    "emp_position_id",
    "manager_id",
    "email",
    "phone",
    "address",
    "postal_code",
    "active",
]


def _apply_employee_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "username":
        return query.filter(ErpEmployee.username.ilike(like_keyword(clean)))

    if search_type == "employee_id":
        return query.filter(cast(ErpEmployee.employee_id, String).like(like_keyword(clean)))

    if search_type == "account_id":
        return query.filter(ErpEmployee.account_id.ilike(like_keyword(clean)))

    if search_type == "emp_position_id":
        return query.filter(cast(ErpEmployee.emp_position_id, String).like(like_keyword(clean)))

    if search_type == "phone":
        return query.filter(ErpEmployee.phone.ilike(like_keyword(clean)))

    if search_type == "email":
        return query.filter(ErpEmployee.email.ilike(like_keyword(clean)))

    return query


def count_employees(search_type="username", keyword=""):
    db = SessionLocal()
    try:
        query = db.query(ErpEmployee)
        query = _apply_employee_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_employees(search_type="username", keyword="", limit=50, offset=0):
    db = SessionLocal()
    try:
        query = db.query(ErpEmployee)
        query = _apply_employee_filter(query, search_type, keyword)
        rows = (
            query.order_by(ErpEmployee.employee_id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [model_to_dict(row, EMPLOYEE_COLUMNS) for row in rows]
    finally:
        db.close()
