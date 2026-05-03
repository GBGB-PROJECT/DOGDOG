# =========================================================
# 🔥 고객 구독 관리 Repository
# - OPD.subs + OPD.subs_plan + OPD.subs_detail JOIN
# - OPD.subs_item + OPD.product + OPD.product_detail 직접 JOIN
#   이유: 고객이 구독 중인 상품을 상품별로 따로 확인해야 함
# - 구독ID / 고객ID / 구독자명 / 전화번호 / 배송지 / 구독상태 / 자동배송 / 배송주기 / 신청요일 검색
# - 구독플랜ID / 할인율은 화면 검색조건에서 제외
# - 구독시작일(subs_date)은 DatePicker start_date/end_date로만 필터
# =========================================================

import datetime

from sqlalchemy import cast, func, literal, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import OpdProduct, OpdProductDetail, OpdSubs, OpdSubsItem, OpdSubsPlan, OpdSubsDetail
from ..common.query_utils import like_keyword, normalize_bool_keyword


def _base_query(db):
    # =========================================================
    # 🔥 재수정: 구독상품을 집계하지 않고 상품 1개 = 화면 1줄로 조회
    # - 요청사항: x1/x2처럼 한 줄에 우겨넣지 말고 상품을 따로따로 보여준다.
    # - subs_item을 직접 JOIN해서 구독상품별 행을 만든다.
    # - product_detail의 brand/product_name을 가져와 사용자가 상품명을 바로 확인하게 한다.
    # =========================================================
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

            # 🔥 추가: 구독상품 1개 단위 표시용 컬럼
            OpdSubsItem.product_id.label("product_id"),
            OpdSubsItem.quantity.label("item_quantity"),
            OpdSubsItem.final_amount.label("item_final_amount"),
            OpdProductDetail.brand.label("product_brand"),
            OpdProductDetail.product_name.label("product_name"),
        )
        .outerjoin(
            OpdSubsPlan,
            OpdSubs.subs_plan_id == OpdSubsPlan.subs_plan_id,
        )
        .outerjoin(
            OpdSubsDetail,
            OpdSubs.subs_id == OpdSubsDetail.subs_id,
        )
        .outerjoin(
            OpdSubsItem,
            OpdSubs.subs_id == OpdSubsItem.subs_id,
        )
        .outerjoin(
            OpdProduct,
            OpdSubsItem.product_id == OpdProduct.product_id,
        )
        .outerjoin(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
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

        # =========================================================
        # 🔥 재수정: subs_plan.subs_sale은 "결제비율"이 아니라 "할인율" 값이다.
        # - DB 값 0.1  → 화면 10%
        # - DB 값 0.05 → 화면 5%
        # - DB 값 10   → 화면 10%
        # 기존처럼 (1 - subs_sale) * 100 으로 계산하면 0.1이 90%로 잘못 표시된다.
        # =========================================================
        if 0 <= sale_rate <= 1:
            discount_rate = sale_rate * 100
            return f"{discount_rate:g}%"

        # 🔥 DB에 5, 10처럼 이미 퍼센트 숫자로 들어온 경우 그대로 표시
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



def _subs_status_search_values(keyword):
    # 🔥 추가: 구독상태 표시값(구독중/해지) 기준 부분검색 처리
    # - DB는 boolean 값이라서 "독중", "해", "지" 같은 화면 표시 텍스트 부분검색이 바로 안 된다.
    # - 검색어가 표시 텍스트의 일부이면 True/False 조건으로 변환해서 조회한다.
    clean = str(keyword or "").strip()
    lowered = clean.lower()

    if not clean:
        return []

    status_words = {
        True: {
            "구독중", "구독", "구", "독", "중", "독중",
            "활성", "y", "yes", "true", "1",
        },
        False: {
            "해지", "해", "지",
            "중지", "비활성", "n", "no", "false", "0",
        },
    }

    matched_values = []

    for bool_value, words in status_words.items():
        for word in words:
            word_text = str(word).strip()
            word_lower = word_text.lower()

            if (
                clean == word_text
                or lowered == word_lower
                or clean in word_text
                or lowered in word_lower
            ):
                matched_values.append(bool_value)
                break

    return matched_values

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
        status_values = _subs_status_search_values(clean)

        if len(status_values) == 1:
            return query.filter(OpdSubs.is_subs_status.is_(status_values[0]))

        if len(status_values) > 1:
            return query.filter(
                or_(
                    *[OpdSubs.is_subs_status.is_(status_value) for status_value in status_values]
                )
            )

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

    if search_type == "subscription_product":
        # =========================================================
        # 🔥 추가/확인: 구독상품 부분검색
        # - 상품ID 숫자 일부, 브랜드 일부, 상품명 일부 모두 검색 가능
        # - 예: "크런치", "닭고기", "더리얼", "105"
        # =========================================================
        return query.filter(
            or_(
                cast(OpdSubsItem.product_id, String).ilike(like_keyword(clean)),
                cast(OpdProductDetail.brand, String).ilike(like_keyword(clean)),
                cast(OpdProductDetail.product_name, String).ilike(like_keyword(clean)),
                func.concat(
                    func.coalesce(cast(OpdProductDetail.brand, String), ""),
                    " ",
                    func.coalesce(cast(OpdProductDetail.product_name, String), ""),
                ).ilike(like_keyword(clean)),
            )
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


def _format_number(value):
    if value is None:
        return ""

    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def _format_product_name(brand, product_name, product_id):
    brand_text = str(brand or "").strip()
    name_text = str(product_name or "").strip()

    if brand_text and name_text:
        return f"{brand_text} {name_text}"

    if name_text:
        return name_text

    if product_id:
        return f"상품ID {product_id}"

    return ""

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
        # 🔥 재수정: 상품을 집계하지 않고 구독상품 1개 단위로 내려준다.
        "product_id": row.product_id or "",
        "product_ids": row.product_id or "",  # 🔥 기존 프론트 호환용
        "product_brand": row.product_brand or "",
        "product_name": row.product_name or "",
        "subscription_product": _format_product_name(row.product_brand, row.product_name, row.product_id),
        "subscription_products": _format_product_name(row.product_brand, row.product_name, row.product_id),  # 🔥 기존 프론트 호환용
        "item_quantity": _format_number(row.item_quantity),
        "total_quantity": _format_number(row.item_quantity),  # 🔥 기존 프론트 호환용
        "item_final_amount": _format_number(row.item_final_amount),
        "total_final_amount": _format_number(row.item_final_amount),  # 🔥 기존 프론트 호환용
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
                OpdSubsItem.product_id.asc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()
