# =========================================================
# 🔥 고객 주문 관리 Repository
# - OPD.sales_order + OPD.sales_order_item JOIN
# - 🔥 상품명 표시용 OPD.product + OPD.product_detail LEFT JOIN 추가
# - 🔥 고객명은 별도 고객 테이블 JOIN 없이 sales_order.recipient 값을 사용
# - 🔥 최종 검색조건은 주문번호 / 고객ID / 전화번호 / 배송지 / 상품만 사용
# - 🔥 기존 주문상품 행 수가 줄어들지 않도록 모든 추가 JOIN은 LEFT OUTER JOIN만 사용
# =========================================================

import datetime

from sqlalchemy import cast, func, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import (
    OpdProduct,
    OpdProductDetail,
    OpdPayment,
    OpdSalesOrder,
    OpdSalesOrderItem,
)
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
            OpdSalesOrder.address.label("address"),
            OpdSalesOrder.detail_address.label("detail_address"),
            OpdSalesOrder.payment_billing_id.label("payment_billing_id"),
            # 🔥 추가: 화면 상세창의 결제ID 대신 OPD.payment.pay_number(결제번호)를 내려준다.
            OpdPayment.pay_number.label("pay_number"),
            OpdSalesOrderItem.product_id.label("product_id"),
            OpdSalesOrderItem.quantity.label("quantity"),
            OpdSalesOrderItem.retail_price.label("retail_price"),
            OpdSalesOrderItem.total_amount.label("total_amount"),
            # 🔥 추가: product_id 숫자만 보이지 않게 상품 기본 정보를 같이 내려준다.
            OpdProduct.product_detail_id.label("product_detail_id"),
            OpdProduct.weight.label("product_weight"),
            OpdProduct.quantity.label("product_unit_quantity"),
            OpdProductDetail.brand.label("product_brand"),
            OpdProductDetail.product_name.label("product_name"),
        )
        .outerjoin(
            OpdSalesOrderItem,
            OpdSalesOrder.sales_order_id == OpdSalesOrderItem.sales_order_id,
        )
        # 🔥 추가: OPD.payment.sales_order_id 기준으로 결제번호(pay_number)를 연결한다.
        .outerjoin(
            OpdPayment,
            OpdSalesOrder.sales_order_id == OpdPayment.sales_order_id,
        )
        # 🔥 중요: 여기서 INNER JOIN을 쓰면 기존 주문상품 행이 사라질 수 있으므로 LEFT JOIN만 사용한다.
        .outerjoin(
            OpdProduct,
            OpdSalesOrderItem.product_id == OpdProduct.product_id,
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

    # 🔥 추가: 고객 검색은 별도 고객 테이블 JOIN 없이 현재 주문의 고객ID/수령인 기준으로 검색한다.
    if search_type == "customer":
        return query.filter(
            or_(
                cast(OpdSalesOrder.customer_id, String).like(like_keyword(clean)),
                cast(OpdSalesOrder.recipient, String).ilike(like_keyword(clean)),
            )
        )

    if search_type == "customer_id":
        if _is_int_text(clean):
            return query.filter(OpdSalesOrder.customer_id == int(clean))
        return query.filter(
            cast(OpdSalesOrder.customer_id, String).like(like_keyword(clean))
        )

    # 🔥 수정: 상품 검색은 상품번(상품상세ID-상품ID) / 상품ID / 상품상세ID / 브랜드 / 상품명을 모두 부분검색한다.
    if search_type == "product":
        product_no_expr = func.concat(
            cast(OpdProduct.product_detail_id, String),
            "-",
            cast(OpdSalesOrderItem.product_id, String),
        )

        return query.filter(
            or_(
                product_no_expr.like(like_keyword(clean)),
                cast(OpdProduct.product_detail_id, String).like(like_keyword(clean)),
                cast(OpdSalesOrderItem.product_id, String).like(like_keyword(clean)),
                cast(OpdProductDetail.brand, String).ilike(like_keyword(clean)),
                cast(OpdProductDetail.product_name, String).ilike(like_keyword(clean)),
            )
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
                    "address": full_address,
                    "product_id": row.product_id,
                    "product_detail_id": row.product_detail_id,
                    "product_brand": row.product_brand,
                    "product_name": row.product_name,
                    "product_weight": row.product_weight,
                    "product_unit_quantity": row.product_unit_quantity,
                    "quantity": row.quantity,
                    "retail_price": row.retail_price,
                    "total_amount": row.total_amount,
                    "payment_billing_id": row.payment_billing_id,
                    "pay_number": row.pay_number,
                }
            )

        return result
    finally:
        db.close()
