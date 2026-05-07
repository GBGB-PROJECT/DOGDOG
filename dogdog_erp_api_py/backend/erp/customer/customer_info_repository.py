from sqlalchemy import cast
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import CompanionCustomer, CompanionCustomerDetail
from ..common.query_utils import (
    like_keyword,
    normalize_bool_keyword,
)

# =========================================================
# ☑️ 고객관리 Repository
# - Companion.customer + Companion.customer_detail JOIN 기반 조회
# - 구독여부/구독횟수는 DB 원본값에 충실하게 표시한다.
# - 구독여부: Companion.customer.is_subscribed
# - 구독횟수: Companion.customer.subs_count
# - 화면에서 임의로 subs_count > 0 계산을 하거나 OPD.subs와 섞지 않는다.
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


def _is_subscribed_expr():
    # 🔥 재수정: DB 원본값에 충실하게 Companion.customer.is_subscribed를 그대로 사용
    # - subs_count > 0 이면 Y로 강제 계산하지 않는다.
    # - OPD.subs 기준으로 재계산하지 않는다.
    # - customer 테이블에 저장된 is_subscribed 값이 곧 고객정보관리 화면의 구독여부다.
    return CompanionCustomer.is_subscribed


def _normalize_subscription_keyword(value):
    # 🔥 추가: 구독여부 검색어 전용 정규화
    # - t / true / y / 구독 => 구독함
    # - f / false / n / 미구독 => 미구독
    clean = str(value or "").strip().lower()

    true_words = {
        "t",
        "true",
        "y",
        "yes",
        "1",
        "구독",
        "구독함",
        "구독중",
        "활성",
        "사용",
    }

    false_words = {
        "f",
        "false",
        "n",
        "no",
        "0",
        "미구독",
        "비구독",
        "구독안함",
        "해지",
        "비활성",
        "미사용",
    }

    if clean in true_words:
        return True

    if clean in false_words:
        return False

    return None


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
    is_subscribed = _is_subscribed_expr()

    return (
        db.query(
            CompanionCustomer.customer_id.label("customer_id"),
            CompanionCustomerDetail.email.label("email"),
            CompanionCustomerDetail.oauth_type.label("oauth_type"),
            CompanionCustomerDetail.nickname.label("nickname"),
            CompanionCustomerDetail.phone.label("phone"),

            # 🔥 재수정: 구독여부는 DB 원본 is_subscribed 그대로 사용
            is_subscribed.label("is_subscribed"),

            # 🔥 재수정: 구독횟수도 DB 원본 subs_count 그대로 사용
            CompanionCustomer.subs_count.label("subs_count"),
            CompanionCustomer.active.label("active"),
            CompanionCustomerDetail.create_date.label("create_date"),
        )
        .outerjoin(
            CompanionCustomerDetail,
            CompanionCustomer.customer_id == CompanionCustomerDetail.customer_id,
        )
    )


def _apply_customer_filter(db, query, search_type: str, keyword: str, start_date=None, end_date=None):
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
            bool_value = _normalize_subscription_keyword(clean)

            if bool_value is not None:
                is_subscribed = _is_subscribed_expr()

                if bool_value is True:
                    query = query.filter(CompanionCustomer.is_subscribed.is_(True))
                else:
                    query = query.filter(CompanionCustomer.is_subscribed.is_(False))
            else:
                # 🔥 수정: 애매한 검색어는 DB 원본 boolean 문자열에 대한 부분검색으로만 처리
                query = query.filter(
                    cast(CompanionCustomer.is_subscribed, String).ilike(like_keyword(clean))
                )

        elif search_type == "subs_count":
            # 🔥 재수정: 구독횟수 검색도 DB 원본 Companion.customer.subs_count 기준
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


    # =========================================================
    # ☑️ 가입일 날짜 범위 필터
    # - 가입일은 검색조건 드롭다운에서 제외하고 DatePicker로만 조회한다.
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
            db,
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
            db,
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
