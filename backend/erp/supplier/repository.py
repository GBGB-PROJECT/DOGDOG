from sqlalchemy import cast, func
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import ErpSupplier
from backend.erp.common.query_utils import (
    model_to_dict,
    like_keyword,
    normalize_bool_keyword,
    parse_date,
)


# =========================================================
# ☑️ 거래처관리 Repository
# - ERP.supplier ORM 모델 기반 조회
# - 거래처ID / 거래처명 / 사업자번호 / 연락상태 / 담당자명 / 전화번호 검색 처리
# - last_update 기준 기간 필터 처리
# - count + limit/offset 페이지네이션 처리
# =========================================================

SUPPLIER_COLUMNS = [
    "supplier_id",
    "supplier_name",
    "brn",
    "is_contact_status",
    "designated_payment_date",
    "scheduled_payment_date",
    "employee_id",
    "memo",
    "sup_manager",
    "phone",
    "last_update",
]


def _apply_supplier_filter(query, search_type: str, keyword: str, start_date=None, end_date=None):
    clean = (keyword or "").strip()

    if clean:
        if search_type == "supplier_id":
            query = query.filter(cast(ErpSupplier.supplier_id, String).like(like_keyword(clean)))

        elif search_type == "supplier_name":
            query = query.filter(ErpSupplier.supplier_name.ilike(like_keyword(clean)))

        elif search_type == "brn":
            query = query.filter(ErpSupplier.brn.ilike(like_keyword(clean)))

        elif search_type == "is_contact_status":
            bool_value = normalize_bool_keyword(
                clean,
                true_words={"가능"},
                false_words={"불가"},
            )
            if bool_value is not None:
                query = query.filter(ErpSupplier.is_contact_status.is_(bool_value))
            else:
                query = query.filter(cast(ErpSupplier.is_contact_status, String).ilike(like_keyword(clean)))

        elif search_type == "sup_manager":
            query = query.filter(ErpSupplier.sup_manager.ilike(like_keyword(clean)))

        elif search_type == "phone":
            query = query.filter(ErpSupplier.phone.ilike(like_keyword(clean)))

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)

    if parsed_start:
        query = query.filter(func.date(ErpSupplier.last_update) >= parsed_start)

    if parsed_end:
        query = query.filter(func.date(ErpSupplier.last_update) <= parsed_end)

    return query


def count_suppliers(search_type="supplier_name", keyword="", start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(ErpSupplier)
        query = _apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        return query.count()
    finally:
        db.close()


def fetch_suppliers(search_type="supplier_name", keyword="", limit=50, offset=0, start_date=None, end_date=None):
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
        return [model_to_dict(row, SUPPLIER_COLUMNS) for row in rows]
    finally:
        db.close()
