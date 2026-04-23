from sqlalchemy import cast
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import ErpEmployee, ErpEmpPosition

from backend.erp.common.query_utils import model_to_dict, like_keyword
from backend.erp.common.mutation_utils import (
    clean_text,
    to_int_or_none,
    require_int,
    require_bool,
    require_text,
    require_date,
    to_date_or_none,
)


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


# =========================================================
# ☑️ 사원 등록
# =========================================================
def create_employee(data: dict):
    db = SessionLocal()
    try:
        employee_id = require_int(data.get("employee_id"), "사원ID")
        account_id = require_text(data.get("account_id"), "계정ID")
        email = require_text(data.get("email"), "이메일")
        emp_position_id = to_int_or_none(data.get("emp_position_id"))
        manager_id = to_int_or_none(data.get("manager_id"))

        if db.query(ErpEmployee).filter(ErpEmployee.employee_id == employee_id).first():
            raise ValueError(f"이미 존재하는 사원ID입니다: {employee_id}")
        if db.query(ErpEmployee).filter(ErpEmployee.account_id == account_id).first():
            raise ValueError(f"이미 존재하는 계정ID입니다: {account_id}")
        if db.query(ErpEmployee).filter(ErpEmployee.email == email).first():
            raise ValueError(f"이미 존재하는 이메일입니다: {email}")
        if emp_position_id and not db.query(ErpEmpPosition).filter(ErpEmpPosition.emp_position_id == emp_position_id).first():
            raise ValueError(f"존재하지 않는 직급ID입니다: {emp_position_id}")
        if manager_id and not db.query(ErpEmployee).filter(ErpEmployee.employee_id == manager_id).first():
            raise ValueError(f"존재하지 않는 관리자ID입니다: {manager_id}")

        employee = ErpEmployee(
            employee_id=employee_id,
            account_id=account_id,
            password=require_text(data.get("password"), "비밀번호"),
            username=require_text(data.get("username"), "이름"),
            hire_date=require_date(data.get("hire_date"), "입사일"),
            quit_date=to_date_or_none(data.get("quit_date")),
            emp_position_id=emp_position_id,
            manager_id=manager_id,
            email=email,
            phone=require_text(data.get("phone"), "전화번호"),
            address=require_text(data.get("address"), "주소"),
            postal_code=require_text(data.get("postal_code"), "우편번호"),
            active=require_bool(data.get("active"), "재직여부"),
        )
        db.add(employee)
        db.commit()
        db.refresh(employee)
        return model_to_dict(employee, EMPLOYEE_COLUMNS)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
