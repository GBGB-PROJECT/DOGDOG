# =========================================================
# 🔥 고객 주문 관리 Repository
# - OPD.sales_order + OPD.sales_order_item JOIN
# - 주문ID / 고객ID / 상품ID / 결제ID 숫자 검색 보강
# - 주문일은 검색조건에서 제외하고 start_date/end_date DatePicker 값으로만 필터링
# - 🔥 address + detail_address를 합쳐 배송지(address)로 반환
# =========================================================

import datetime

from sqlalchemy import cast, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import OpdSalesOrder, OpdSalesOrderItem
from ..common.query_utils import like_keyword


def _base_query(db):
    return (
        db.query(
            OpdSalesOrder.sales_order_id.label("sales_order_id"),
            OpdSalesOrder.order_number.label("order_number"),
            OpdSalesOrder.order_date.label("order_date"),
            OpdSalesOrder.customer_id.label("customer_id"),
            OpdSalesOrder.recipient.label("recipient"),
            OpdSalesOrder.phone.label("phone"),

            # 🔥 추가: 배송지 구성용 컬럼
            OpdSalesOrder.address.label("address"),
            OpdSalesOrder.detail_address.label("detail_address"),

            OpdSalesOrder.payment_billing_id.label("payment_billing_id"),
            OpdSalesOrderItem.product_id.label("product_id"),
            OpdSalesOrderItem.quantity.label("quantity"),
            OpdSalesOrderItem.retail_price.label("retail_price"),
            OpdSalesOrderItem.total_amount.label("total_amount"),
        )
        .outerjoin(
            OpdSalesOrderItem,
            OpdSalesOrder.sales_order_id == OpdSalesOrderItem.sales_order_id,
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


def _apply_filter(query, search_type, keyword):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "sales_order_id":
        if _is_int_text(clean):
            return query.filter(OpdSalesOrder.sales_order_id == int(clean))
        return query.filter(
            cast(OpdSalesOrder.sales_order_id, String).like(like_keyword(clean))
        )

    if search_type == "customer_id":
        if _is_int_text(clean):
            return query.filter(OpdSalesOrder.customer_id == int(clean))
        return query.filter(
            cast(OpdSalesOrder.customer_id, String).like(like_keyword(clean))
        )

    if search_type == "product_id":
        if _is_int_text(clean):
            return query.filter(OpdSalesOrderItem.product_id == int(clean))
        return query.filter(
            cast(OpdSalesOrderItem.product_id, String).like(like_keyword(clean))
        )

    if search_type == "payment_billing_id":
        if _is_int_text(clean):
            return query.filter(OpdSalesOrder.payment_billing_id == int(clean))
        return query.filter(
            cast(OpdSalesOrder.payment_billing_id, String).like(like_keyword(clean))
        )

    if search_type == "order_number":
        return query.filter(
            cast(OpdSalesOrder.order_number, String).like(like_keyword(clean))
        )

    if search_type == "recipient":
        return query.filter(
            cast(OpdSalesOrder.recipient, String).ilike(like_keyword(clean))
        )

    if search_type == "phone":
        return query.filter(
            cast(OpdSalesOrder.phone, String).ilike(like_keyword(clean))
        )

    # 🔥 추가: 배송지 검색
    if search_type == "address":
        return query.filter(
            or_(
                cast(OpdSalesOrder.address, String).ilike(like_keyword(clean)),
                cast(OpdSalesOrder.detail_address, String).ilike(like_keyword(clean)),
            )
        )

    return query


def _apply_date_filter(query, start_date=None, end_date=None):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if start_dt:
        query = query.filter(OpdSalesOrder.order_date >= start_dt)

    if end_dt:
        query = query.filter(OpdSalesOrder.order_date <= end_dt)

    return query


def count_customer_orders(
    search_type="order_number",
    keyword="",
    start_date=None,
    end_date=None,
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(query, start_date=start_date, end_date=end_date)
        return query.count()
    finally:
        db.close()


def fetch_customer_orders(
    search_type="order_number",
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
        query = _apply_date_filter(query, start_date=start_date, end_date=end_date)

        rows = (
            query.order_by(
                OpdSalesOrder.order_date.desc(),
                OpdSalesOrder.sales_order_id.desc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        result = []

        for row in rows:
            # 🔥 추가: address + detail_address 합치기
            address_text = str(row.address or "").strip()
            detail_address_text = str(row.detail_address or "").strip()
            full_address = f"{address_text} {detail_address_text}".strip()

            result.append(
                {
                    "sales_order_id": row.sales_order_id,
                    "order_number": row.order_number,
                    "order_date": row.order_date,
                    "customer_id": row.customer_id,
                    "recipient": row.recipient,
                    "phone": row.phone,
                    "address": full_address,  # 🔥 배송지로 프론트에 전달
                    "product_id": row.product_id,
                    "quantity": row.quantity,
                    "retail_price": row.retail_price,
                    "total_amount": row.total_amount,
                    "payment_billing_id": row.payment_billing_id,
                }
            )

        return result
    finally:
        db.close()