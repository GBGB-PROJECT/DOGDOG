from sqlalchemy import cast
from sqlalchemy.types import String

from backend.db.db import SessionLocal
from backend.db.models import CompanionCustomer, CompanionCustomerDetail
from backend.erp.common.query_utils import (
    like_keyword,
    normalize_bool_keyword,
)
from backend.erp.common.mutation_utils import (
    require_int,
    require_bool,
)


# =========================================================
# ☑️ 고객관리 Repository
# - Companion.customer + Companion.customer_detail JOIN 기반 조회
# - 고객ID / 이메일 / oauth유형 / 닉네임 / 전화번호 / 구독여부 / 구독횟수 / 상태 / 가입일 검색 처리
# - count + limit/offset 페이지네이션 처리
# - 가입일(create_date) 날짜 범위 필터를 count/fetch 모두 동일하게 적용
# =========================================================

CUSTOMER_COLUMNS = [
    "customer_id",
    "email",
    "oauth_type",
    "nickname",
    "phone",
    "is_subscribed",
    "subs_count",
    "active",
    "create_date",
]


def _row_to_dict(row):
    return {
        "customer_id": row.customer_id,
        "email": row.email,
        "oauth_type": row.oauth_type,
        "nickname": row.nickname,
        "phone": row.phone,
        "is_subscribed": row.is_subscribed,
        "subs_count": row.subs_count,
        "active": row.active,
        "create_date": row.create_date,
    }


def _base_customer_query(db):
    return (
        db.query(
            CompanionCustomer.customer_id.label("customer_id"),
            CompanionCustomerDetail.email.label("email"),
            CompanionCustomerDetail.oauth_type.label("oauth_type"),
            CompanionCustomerDetail.nickname.label("nickname"),
            CompanionCustomerDetail.phone.label("phone"),
            CompanionCustomer.is_subscribed.label("is_subscribed"),
            CompanionCustomer.subs_count.label("subs_count"),
            CompanionCustomer.active.label("active"),
            CompanionCustomerDetail.create_date.label("create_date"),
        )
        .outerjoin(
            CompanionCustomerDetail,
            CompanionCustomer.customer_id == CompanionCustomerDetail.customer_id,
        )
    )


def _apply_customer_filter(query, search_type: str, keyword: str, start_date=None, end_date=None):
    clean = (keyword or "").strip()

    if clean:
        if search_type == "customer_id":
            query = query.filter(
                cast(CompanionCustomer.customer_id, String).like(like_keyword(clean))
            )

        elif search_type == "email":
            query = query.filter(
                cast(CompanionCustomerDetail.email, String).ilike(like_keyword(clean))
            )

        elif search_type == "oauth_type":
            query = query.filter(
                cast(CompanionCustomerDetail.oauth_type, String).ilike(like_keyword(clean))
            )

        elif search_type == "nickname":
            query = query.filter(
                cast(CompanionCustomerDetail.nickname, String).ilike(like_keyword(clean))
            )

        elif search_type == "phone":
            query = query.filter(
                cast(CompanionCustomerDetail.phone, String).ilike(like_keyword(clean))
            )

        elif search_type == "is_subscribed":
            bool_value = normalize_bool_keyword(
                clean,
                true_words={"구독"},
                false_words={"미구독", "비구독"},
            )
            if bool_value is not None:
                query = query.filter(CompanionCustomer.is_subscribed.is_(bool_value))
            else:
                query = query.filter(
                    cast(CompanionCustomer.is_subscribed, String).ilike(like_keyword(clean))
                )

        elif search_type == "subs_count":
            query = query.filter(
                cast(CompanionCustomer.subs_count, String).like(like_keyword(clean))
            )

        elif search_type == "active":
            bool_value = normalize_bool_keyword(clean)
            if bool_value is not None:
                query = query.filter(CompanionCustomer.active.is_(bool_value))
            else:
                query = query.filter(
                    cast(CompanionCustomer.active, String).ilike(like_keyword(clean))
                )

        elif search_type == "create_date":
            query = query.filter(
                cast(CompanionCustomerDetail.create_date, String).like(like_keyword(clean))
            )

    # =========================================================
    # ☑️ 가입일 날짜 범위 필터
    # - count / fetch 모두 같은 조건을 타야 페이지네이션이 맞는다.
    # =========================================================
    if start_date is not None:
        query = query.filter(CompanionCustomerDetail.create_date >= start_date)

    if end_date is not None:
        query = query.filter(CompanionCustomerDetail.create_date <= end_date)

    return query


def count_customers(search_type="customer_id", keyword="", start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = _base_customer_query(db)
        query = _apply_customer_filter(
            query,
            search_type=search_type,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )
        return query.count()
    finally:
        db.close()


def fetch_customers(search_type="customer_id", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = _base_customer_query(db)
        query = _apply_customer_filter(
            query,
            search_type=search_type,
            keyword=keyword,
            start_date=start_date,
            end_date=end_date,
        )

        rows = (
            query.order_by(CompanionCustomer.customer_id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()


# =========================================================
# ☑️ 고객 등록
# - 기존 등록 기능 최대한 유지
# - 현재 등록 모달은 customer 테이블 필드만 받고 있으므로
#   detail 테이블은 여기서 생성하지 않음
# =========================================================
def create_customer(data: dict):
    db = SessionLocal()
    try:
        customer_id = require_int(data.get("customer_id"), "고객ID")

        exists = (
            db.query(CompanionCustomer)
            .filter(CompanionCustomer.customer_id == customer_id)
            .first()
        )
        if exists:
            raise ValueError(f"이미 존재하는 고객ID입니다: {customer_id}")

        customer = CompanionCustomer(
            customer_id=customer_id,
            is_subscribed=require_bool(data.get("is_subscribed"), "구독여부"),
            subs_count=require_int(data.get("subs_count"), "구독횟수"),
            permission=1,
            active=require_bool(data.get("active"), "상태"),
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)

        return {
            "customer_id": customer.customer_id,
            "email": "",
            "oauth_type": "",
            "nickname": "",
            "phone": "",
            "is_subscribed": customer.is_subscribed,
            "subs_count": customer.subs_count,
            "active": customer.active,
            "create_date": "",
        }
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()