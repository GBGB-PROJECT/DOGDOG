from sqlalchemy import cast
from sqlalchemy.types import String

from backend.db.db import SessionLocal
from backend.db.models import CompanionCustomer
from backend.erp.common.query_utils import (
    model_to_dict,
    like_keyword,
    normalize_bool_keyword,
)
from backend.erp.common.mutation_utils import (
    to_int_or_none,
    to_bool_or_none,
    require_int,
    require_bool,
)


# =========================================================
# ☑️ 고객관리 Repository
# - Companion.customer ORM 모델 기반 조회
# - 고객ID / 구독여부 / 구독횟수 / 권한 / 상태 검색 처리
# - count + limit/offset 페이지네이션 처리
# =========================================================

CUSTOMER_COLUMNS = [
    "customer_id",
    "is_subscribed",
    "subs_count",
    "permission",
    "active",
    "last_update",
]


def _apply_customer_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "customer_id":
        return query.filter(cast(CompanionCustomer.customer_id, String).like(like_keyword(clean)))

    if search_type == "is_subscribed":
        bool_value = normalize_bool_keyword(
            clean,
            true_words={"구독"},
            false_words={"미구독", "비구독"},
        )
        if bool_value is not None:
            return query.filter(CompanionCustomer.is_subscribed.is_(bool_value))
        return query.filter(cast(CompanionCustomer.is_subscribed, String).ilike(like_keyword(clean)))

    if search_type == "subs_count":
        return query.filter(cast(CompanionCustomer.subs_count, String).like(like_keyword(clean)))

    if search_type == "permission":
        return query.filter(cast(CompanionCustomer.permission, String).like(like_keyword(clean)))

    if search_type == "active":
        bool_value = normalize_bool_keyword(clean)
        if bool_value is not None:
            return query.filter(CompanionCustomer.active.is_(bool_value))
        return query.filter(cast(CompanionCustomer.active, String).ilike(like_keyword(clean)))

    return query


def count_customers(search_type="customer_id", keyword=""):
    db = SessionLocal()
    try:
        query = db.query(CompanionCustomer)
        query = _apply_customer_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_customers(search_type="customer_id", keyword="", limit=50, offset=0):
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
        return [model_to_dict(row, CUSTOMER_COLUMNS) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 고객 등록
# =========================================================
def create_customer(data: dict):
    db = SessionLocal()
    try:
        customer_id = require_int(data.get("customer_id"), "고객ID")

        if db.query(CompanionCustomer).filter(CompanionCustomer.customer_id == customer_id).first():
            raise ValueError(f"이미 존재하는 고객ID입니다: {customer_id}")

        customer = CompanionCustomer(
            customer_id=customer_id,
            is_subscribed=require_bool(data.get("is_subscribed"), "구독여부"),
            subs_count=require_int(data.get("subs_count"), "구독횟수"),
            permission=require_int(data.get("permission"), "권한"),
            active=require_bool(data.get("active"), "상태"),
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return model_to_dict(customer, CUSTOMER_COLUMNS)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
