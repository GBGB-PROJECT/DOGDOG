# =========================================================
# 🔥 고객 구독 관리 Repository
# - OPD.subs + OPD.subs_plan + OPD.subs_detail JOIN
# - subs_item은 제외
#   이유: subs_item은 구독 상품 단위라서 JOIN하면 구독 1건이 여러 행으로 뻥튀기됨
# - 구독ID / 고객ID / 구독플랜ID / 자동배송여부 / 구독상태 / 배송신청요일
# - 배송주기 / 할인율 / 배송지 / 이름 / 전화번호 검색
# - 구독시작일(subs_date)은 DatePicker start_date/end_date로만 필터
# =========================================================

import datetime

from sqlalchemy import cast, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import OpdSubs, OpdSubsPlan, OpdSubsDetail
from ..common.query_utils import like_keyword, normalize_bool_keyword


def _base_query(db):
    return (
        db.query(
            OpdSubs.subs_id.label("subs_id"),
            OpdSubs.customer_id.label("customer_id"),
            OpdSubs.subs_date.label("subs_date"),
            OpdSubs.subs_plan_id.label("subs_plan_id"),
            OpdSubs.is_auto_delivery.label("is_auto_delivery"),
            OpdSubs.is_subs_status.label("is_subs_status"),
            OpdSubs.subs_day.label("subs_day"),

            OpdSubsPlan.delivery_cycle.label("delivery_cycle"),
            OpdSubsPlan.subs_sale.label("subs_sale"),

            OpdSubsDetail.address.label("address"),
            OpdSubsDetail.detail_address.label("detail_address"),
            OpdSubsDetail.name.label("name"),
            OpdSubsDetail.phone.label("phone"),
        )
        .outerjoin(
            OpdSubsPlan,
            OpdSubs.subs_plan_id == OpdSubsPlan.subs_plan_id,
        )
        .outerjoin(
            OpdSubsDetail,
            OpdSubs.subs_id == OpdSubsDetail.subs_id,
        )
    )


def _normalize_start_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value

    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.min)

    try:
        parsed = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
        return datetime.datetime.combine(parsed.date(), datetime.time.min)
    except ValueError:
        return None


def _normalize_end_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value

    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.max)

    try:
        parsed = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
        return datetime.datetime.combine(parsed.date(), datetime.time.max)
    except ValueError:
        return None


def _is_int_text(value):
    return str(value or "").strip().isdigit()


def _format_bool_yn(value):
    if value is None:
        return ""
    return "Y" if value else "N"


def _format_subs_status(value):
    # 🔥 재수정: Swagger UI에서 생성된 구독은 subs_plan_id가 비어 있어도
    # is_subs_status=True면 정상적으로 구독중으로 표시한다.
    if value is None:
        return ""
    return "구독중" if value else "해지"


def _format_delivery_cycle(value):
    if value is None:
        return ""

    try:
        value_int = int(value)
    except Exception:
        return str(value)

    if value_int == 2:
        return "2주"

    if value_int == 4:
        return "4주"

    return f"{value_int}주"


def _format_subs_sale(value):
    if value is None:
        return ""

    try:
        sale_rate = float(value)

        # 🔥 수정: subs_sale이 결제비율이면 할인율은 1 - subs_sale
        # 예: 0.95 = 정가의 95% 결제 = 5% 할인
        if 0 <= sale_rate <= 1:
            discount_rate = (1 - sale_rate) * 100
            return f"{discount_rate:g}%"

        # 🔥 혹시 DB에 5, 10처럼 이미 할인율 숫자로 들어오면 그대로 표시
        return f"{sale_rate:g}%"

    except Exception:
        return str(value)


def _format_subs_day(value):
    if value is None:
        return ""

    day = str(value).strip().lower()

    mapping = {
        "monday": "월요일",
        "tuesday": "화요일",
        "wednesday": "수요일",
        "thursday": "목요일",
        "friday": "금요일",
        "saturday": "토요일",
        "sunday": "일요일",
        "mon": "월요일",
        "tue": "화요일",
        "tues": "화요일",
        "wed": "수요일",
        "thu": "목요일",
        "thur": "목요일",
        "thurs": "목요일",
        "fri": "금요일",
        "sat": "토요일",
        "sun": "일요일",
        "월": "월요일",
        "화": "화요일",
        "수": "수요일",
        "목": "목요일",
        "금": "금요일",
        "토": "토요일",
        "일": "일요일",
    }

    return mapping.get(day, str(value))


# =========================================================
# 🔥 추가: 요일 검색어 정규화
# - DB에는 monday/tuesday처럼 영문으로 들어있는데
# - 화면/Swagger에서는 월, 화, 화요일처럼 한글로 검색하기 때문에
# - subs_day 검색 시 한글/영문/약어를 모두 OR 조건으로 검색한다.
# =========================================================
def _subs_day_search_values(keyword):
    clean = str(keyword or "").strip()
    lowered = clean.lower()

    day_groups = {
        "monday": ["월", "월요일", "mon", "monday"],
        "tuesday": ["화", "화요일", "tue", "tues", "tuesday"],
        "wednesday": ["수", "수요일", "wed", "wednesday"],
        "thursday": ["목", "목요일", "thu", "thur", "thurs", "thursday"],
        "friday": ["금", "금요일", "fri", "friday"],
        "saturday": ["토", "토요일", "sat", "saturday"],
        "sunday": ["일", "일요일", "sun", "sunday"],
    }

    for values in day_groups.values():
        if clean in values or lowered in values:
            return values

    return [clean]


def _apply_filter(query, search_type, keyword):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "subs_id":
        if _is_int_text(clean):
            return query.filter(OpdSubs.subs_id == int(clean))

        return query.filter(
            cast(OpdSubs.subs_id, String).like(like_keyword(clean))
        )

    if search_type == "customer_id":
        if _is_int_text(clean):
            return query.filter(OpdSubs.customer_id == int(clean))

        return query.filter(
            cast(OpdSubs.customer_id, String).like(like_keyword(clean))
        )

    if search_type == "subs_plan_id":
        if _is_int_text(clean):
            return query.filter(OpdSubs.subs_plan_id == int(clean))

        return query.filter(
            cast(OpdSubs.subs_plan_id, String).like(like_keyword(clean))
        )

    if search_type == "is_auto_delivery":
        bool_value = normalize_bool_keyword(
            clean,
            true_words={
                "자동",
                "자동배송",
                "Y",
                "y",
                "yes",
                "YES",
                "true",
                "TRUE",
                "1",
            },
            false_words={
                "수동",
                "비자동",
                "N",
                "n",
                "no",
                "NO",
                "false",
                "FALSE",
                "0",
            },
        )

        if bool_value is not None:
            return query.filter(OpdSubs.is_auto_delivery.is_(bool_value))

        return query.filter(
            cast(OpdSubs.is_auto_delivery, String).ilike(like_keyword(clean))
        )

    if search_type == "is_subs_status":
        bool_value = normalize_bool_keyword(
            clean,
            true_words={
                "구독중",
                "구독",
                "활성",
                "Y",
                "y",
                "yes",
                "YES",
                "true",
                "TRUE",
                "1",
            },
            false_words={
                "해지",
                "중지",
                "비활성",
                "N",
                "n",
                "no",
                "NO",
                "false",
                "FALSE",
                "0",
            },
        )

        if bool_value is not None:
            return query.filter(OpdSubs.is_subs_status.is_(bool_value))

        return query.filter(
            cast(OpdSubs.is_subs_status, String).ilike(like_keyword(clean))
        )

    if search_type == "subs_day":
        day_values = _subs_day_search_values(clean)

        return query.filter(
            or_(
                *[
                    cast(OpdSubs.subs_day, String).ilike(like_keyword(day_value))
                    for day_value in day_values
                    if day_value
                ]
            )
        )

    if search_type == "delivery_cycle":
        if clean in ["2주", "2"]:
            return query.filter(OpdSubsPlan.delivery_cycle == 2)

        if clean in ["4주", "4"]:
            return query.filter(OpdSubsPlan.delivery_cycle == 4)

        return query.filter(
            cast(OpdSubsPlan.delivery_cycle, String).like(like_keyword(clean))
        )

    if search_type == "subs_sale":
        return query.filter(
            cast(OpdSubsPlan.subs_sale, String).like(like_keyword(clean))
        )

    if search_type == "address":
        return query.filter(
            or_(
                cast(OpdSubsDetail.address, String).ilike(like_keyword(clean)),
                cast(OpdSubsDetail.detail_address, String).ilike(like_keyword(clean)),
            )
        )

    if search_type == "name":
        return query.filter(
            cast(OpdSubsDetail.name, String).ilike(like_keyword(clean))
        )

    if search_type == "phone":
        return query.filter(
            cast(OpdSubsDetail.phone, String).ilike(like_keyword(clean))
        )

    return query


def _apply_date_filter(query, start_date=None, end_date=None):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if start_dt:
        query = query.filter(OpdSubs.subs_date >= start_dt)

    if end_dt:
        query = query.filter(OpdSubs.subs_date <= end_dt)

    return query


def _row_to_dict(row):
    address_text = str(row.address or "").strip()
    detail_address_text = str(row.detail_address or "").strip()
    full_address = f"{address_text} {detail_address_text}".strip()

    return {
        "subs_id": row.subs_id,
        "customer_id": row.customer_id,
        "subs_date": row.subs_date,
        "subs_plan_id": row.subs_plan_id,
        "is_auto_delivery": _format_bool_yn(row.is_auto_delivery),
        "is_subs_status": _format_subs_status(row.is_subs_status),
        "subs_day": _format_subs_day(row.subs_day),
        "delivery_cycle": _format_delivery_cycle(row.delivery_cycle),
        "subs_sale": _format_subs_sale(row.subs_sale),
        "address": full_address,
        "name": row.name,
        "phone": row.phone,
    }


def count_customer_subscriptions(
    search_type="subs_id",
    keyword="",
    start_date=None,
    end_date=None,
):
    db = SessionLocal()

    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(
            query,
            start_date=start_date,
            end_date=end_date,
        )

        return query.count()

    finally:
        db.close()


def fetch_customer_subscriptions(
    search_type="subs_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
):
    db = SessionLocal()

    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(
            query,
            start_date=start_date,
            end_date=end_date,
        )

        rows = (
            query.order_by(
                OpdSubs.subs_date.desc(),
                OpdSubs.subs_id.desc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()
