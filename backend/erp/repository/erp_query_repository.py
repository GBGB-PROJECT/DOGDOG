from datetime import datetime, date
from decimal import Decimal

from sqlalchemy import cast, func
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import (
    CompanionCustomer,
    ErpEmployee,
    ErpSupplier,
    OpdProductDetail,
)


# =========================================================
# ☑️ ERP 공통 조회 Repository
# - 팀 공통 DOGDOG/db/db.py 의 SessionLocal 사용
# - 팀 공통 DOGDOG/db/models.py 의 SQLAlchemy ORM 모델 사용
# - ERP 화면에서 필요한 조회/검색/count/limit/offset만 담당
# =========================================================


def _to_plain_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return str(value)

    return value


def _model_to_dict(model, columns):
    return {
        column: _to_plain_value(getattr(model, column, None))
        for column in columns
    }


def _like_keyword(keyword: str):
    return f"%{(keyword or '').strip()}%"


def _normalize_bool_keyword(keyword: str, true_words=None, false_words=None):
    clean = (keyword or '').strip()
    lowered = clean.lower()

    true_set = set(true_words or []) | {'y', 'yes', 'true', '1', '사용', '활성'}
    false_set = set(false_words or []) | {'n', 'no', 'false', '0', '미사용', '비활성'}

    if lowered in true_set or clean in true_set:
        return True

    if lowered in false_set or clean in false_set:
        return False

    return None


# =========================================================
# ☑️ 고객관리 조회
# =========================================================
CUSTOMER_COLUMNS = [
    'customer_id',
    'is_subscribed',
    'subs_count',
    'permission',
    'active',
    'last_update',
]


def _apply_customer_filter(query, search_type: str, keyword: str):
    clean = (keyword or '').strip()

    if not clean:
        return query

    if search_type == 'customer_id':
        return query.filter(cast(CompanionCustomer.customer_id, String).like(_like_keyword(clean)))

    if search_type == 'is_subscribed':
        bool_value = _normalize_bool_keyword(
            clean,
            true_words={'구독'},
            false_words={'미구독', '비구독'},
        )
        if bool_value is not None:
            return query.filter(CompanionCustomer.is_subscribed.is_(bool_value))
        return query.filter(cast(CompanionCustomer.is_subscribed, String).ilike(_like_keyword(clean)))

    if search_type == 'subs_count':
        return query.filter(cast(CompanionCustomer.subs_count, String).like(_like_keyword(clean)))

    if search_type == 'permission':
        return query.filter(cast(CompanionCustomer.permission, String).like(_like_keyword(clean)))

    if search_type == 'active':
        bool_value = _normalize_bool_keyword(clean)
        if bool_value is not None:
            return query.filter(CompanionCustomer.active.is_(bool_value))
        return query.filter(cast(CompanionCustomer.active, String).ilike(_like_keyword(clean)))

    return query


def count_customers(search_type='customer_id', keyword=''):
    db = SessionLocal()
    try:
        query = db.query(CompanionCustomer)
        query = _apply_customer_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_customers(search_type='customer_id', keyword='', limit=50, offset=0):
    db = SessionLocal()
    try:
        query = db.query(CompanionCustomer)
        query = _apply_customer_filter(query, search_type, keyword)
        rows = (
            query.order_by(CompanionCustomer.customer_id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_model_to_dict(row, CUSTOMER_COLUMNS) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 인사관리 조회
# =========================================================
EMPLOYEE_COLUMNS = [
    'employee_id',
    'account_id',
    'username',
    'hire_date',
    'quit_date',
    'emp_position_id',
    'manager_id',
    'email',
    'phone',
    'address',
    'postal_code',
    'active',
]


def _apply_employee_filter(query, search_type: str, keyword: str):
    clean = (keyword or '').strip()

    if not clean:
        return query

    if search_type == 'username':
        return query.filter(ErpEmployee.username.ilike(_like_keyword(clean)))

    if search_type == 'employee_id':
        return query.filter(cast(ErpEmployee.employee_id, String).like(_like_keyword(clean)))

    if search_type == 'account_id':
        return query.filter(ErpEmployee.account_id.ilike(_like_keyword(clean)))

    if search_type == 'emp_position_id':
        return query.filter(cast(ErpEmployee.emp_position_id, String).like(_like_keyword(clean)))

    if search_type == 'phone':
        return query.filter(ErpEmployee.phone.ilike(_like_keyword(clean)))

    if search_type == 'email':
        return query.filter(ErpEmployee.email.ilike(_like_keyword(clean)))

    return query


def count_employees(search_type='username', keyword=''):
    db = SessionLocal()
    try:
        query = db.query(ErpEmployee)
        query = _apply_employee_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_employees(search_type='username', keyword='', limit=50, offset=0):
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
        return [_model_to_dict(row, EMPLOYEE_COLUMNS) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 상품마스터 / 상품상세 조회
# =========================================================
PRODUCT_DETAIL_COLUMNS = [
    'product_detail_id',
    'type',
    'brand',
    'product_name',
    'function',
    'description',
    'crude_protein',
    'crude_fat',
    'calories',
    'thumbnail',
    'kibble_size',
    'life',
    'protein_type',
    'main_protein',
    'certified',
    'preservative',
    'feedshape',
    'last_update',
]


def _apply_product_detail_filter(query, search_type: str, keyword: str):
    clean = (keyword or '').strip()

    if not clean:
        return query

    if search_type == 'product_name':
        return query.filter(OpdProductDetail.product_name.ilike(_like_keyword(clean)))

    if search_type == 'type':
        return query.filter(OpdProductDetail.type.ilike(_like_keyword(clean)))

    if search_type == 'brand':
        return query.filter(OpdProductDetail.brand.ilike(_like_keyword(clean)))

    if search_type == 'function':
        return query.filter(OpdProductDetail.function.ilike(_like_keyword(clean)))

    if search_type == 'life':
        return query.filter(OpdProductDetail.life.ilike(_like_keyword(clean)))

    if search_type == 'main_protein':
        return query.filter(OpdProductDetail.main_protein.ilike(_like_keyword(clean)))

    return query


def count_product_details(search_type='product_name', keyword=''):
    db = SessionLocal()
    try:
        query = db.query(OpdProductDetail)
        query = _apply_product_detail_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_product_details(search_type='product_name', keyword='', limit=50, offset=0):
    db = SessionLocal()
    try:
        query = db.query(OpdProductDetail)
        query = _apply_product_detail_filter(query, search_type, keyword)
        rows = (
            query.order_by(OpdProductDetail.product_name.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_model_to_dict(row, PRODUCT_DETAIL_COLUMNS) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 거래처관리 조회
# =========================================================
SUPPLIER_COLUMNS = [
    'supplier_id',
    'supplier_name',
    'brn',
    'is_contact_status',
    'designated_payment_date',
    'scheduled_payment_date',
    'employee_id',
    'memo',
    'sup_manager',
    'phone',
    'last_update',
]


def _parse_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value)[:10], '%Y-%m-%d').date()
    except ValueError:
        return None


def _apply_supplier_filter(query, search_type: str, keyword: str, start_date=None, end_date=None):
    clean = (keyword or '').strip()

    if clean:
        if search_type == 'supplier_id':
            query = query.filter(cast(ErpSupplier.supplier_id, String).like(_like_keyword(clean)))

        elif search_type == 'supplier_name':
            query = query.filter(ErpSupplier.supplier_name.ilike(_like_keyword(clean)))

        elif search_type == 'brn':
            query = query.filter(ErpSupplier.brn.ilike(_like_keyword(clean)))

        elif search_type == 'is_contact_status':
            bool_value = _normalize_bool_keyword(
                clean,
                true_words={'가능'},
                false_words={'불가'},
            )
            if bool_value is not None:
                query = query.filter(ErpSupplier.is_contact_status.is_(bool_value))
            else:
                query = query.filter(cast(ErpSupplier.is_contact_status, String).ilike(_like_keyword(clean)))

        elif search_type == 'sup_manager':
            query = query.filter(ErpSupplier.sup_manager.ilike(_like_keyword(clean)))

        elif search_type == 'phone':
            query = query.filter(ErpSupplier.phone.ilike(_like_keyword(clean)))

    parsed_start = _parse_date(start_date)
    parsed_end = _parse_date(end_date)

    if parsed_start:
        query = query.filter(func.date(ErpSupplier.last_update) >= parsed_start)

    if parsed_end:
        query = query.filter(func.date(ErpSupplier.last_update) <= parsed_end)

    return query


def count_suppliers(search_type='supplier_name', keyword='', start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(ErpSupplier)
        query = _apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        return query.count()
    finally:
        db.close()


def fetch_suppliers(search_type='supplier_name', keyword='', limit=50, offset=0, start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(ErpSupplier)
        query = _apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        rows = (
            query.order_by(ErpSupplier.supplier_id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_model_to_dict(row, SUPPLIER_COLUMNS) for row in rows]
    finally:
        db.close()
