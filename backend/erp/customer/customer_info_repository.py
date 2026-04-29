from sqlalchemy import cast, false
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import CompanionCustomer, CompanionCustomerDetail, OpdSubs
from ..common.query_utils import (
    like_keyword,
    normalize_bool_keyword,
)
from ..common.mutation_utils import (
    require_int,
    require_bool,
)

# =========================================================
# ☑️ 고객관리 Repository
# - Companion.customer + Companion.customer_detail JOIN 기반 조회
# - 구독여부는 Companion.customer.is_subscribed 원본값만 믿지 않고
#   OPD.subs에 활성 구독(is_subs_status=True)이 있는지 기준으로 계산
# - Swagger UI에서 생성한 구독은 subs_plan_id가 비어 있어도
#   is_subs_status=True면 실제 구독중으로 인정한다.
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


def _active_subscription_exists_expr(db):
    # 🔥 수정: 구독여부 판단 기준
    # - subs_plan_id 유무로 걸러내지 않는다.
    # - Swagger UI에서 만든 구독 데이터도 is_subs_status=True면 구독중으로 인정한다.
    return (
        db.query(OpdSubs.subs_id)
        .filter(
            OpdSubs.customer_id == CompanionCustomer.customer_id,
            OpdSubs.is_subs_status.is_(True),
        )
        .exists()
    )


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
    active_subscription_exists = _active_subscription_exists_expr(db)

    return (
        db.query(
            CompanionCustomer.customer_id.label("customer_id"),
            CompanionCustomerDetail.email.label("email"),
            CompanionCustomerDetail.oauth_type.label("oauth_type"),
            CompanionCustomerDetail.nickname.label("nickname"),
            CompanionCustomerDetail.phone.label("phone"),

            # 🔥 수정: 화면 구독여부는 OPD.subs의 활성 구독 존재 여부로 계산
            active_subscription_exists.label("is_subscribed"),

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
                active_subscription_exists = _active_subscription_exists_expr(db)

                if bool_value is True:
                    query = query.filter(active_subscription_exists)
                else:
                    query = query.filter(~active_subscription_exists)
            else:
                # 🔥 수정: 애매한 검색어는 원본 customer.is_subscribed로 fallback하지 않는다.
                # - 화면 표시 기준과 검색 기준이 갈라지는 문제 방지
                query = query.filter(false())

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
