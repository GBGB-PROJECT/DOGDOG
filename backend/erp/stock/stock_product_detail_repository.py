# =========================================================
# 🔥 상품별 재고 상세 Repository
# - ERP.stock 이 주인공인 조회 화면
# - ERP.stock + OPD.product + OPD.product_detail + ERP.inbound + ERP.inbound_status JOIN
# - 중량/수량/판매가/샘플/활성/상세ID/발주ID는 화면에서 제외
# - stock 관련 컬럼을 브랜드 뒤에 배치할 수 있도록 동일 key로 반환
# =========================================================

import datetime

from sqlalchemy import cast, func
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import (
    ErpInbound,
    ErpInboundStatus,
    ErpStock,
    OpdProduct,
    OpdProductDetail,
)
from ..common.query_utils import like_keyword, to_plain_value


SEARCH_TYPE_DEFAULT = "product"


def _base_query(db):
    return (
        db.query(
            # 🔥 stock 중심 컬럼
            ErpStock.product_id.label("product_id"),
            ErpStock.inbound_id.label("inbound_id"),
            ErpStock.save_stock.label("save_stock"),
            ErpStock.sale_stock.label("sale_stock"),
            ErpStock.scrap_stock.label("scrap_stock"),
            ErpStock.stock_available.label("stock_available"),
            ErpStock.expiration_date.label("expiration_date"),
            ErpStock.last_update.label("last_update"),

            # 🔥 총 재고량 카드 월 필터 근거 표시용
            # - 입고완료일 우선
            # - 없으면 입고시작일 사용
            func.coalesce(
                ErpInbound.inbound_complete,
                ErpInbound.inbound_start,
            ).label("inbound_date"),

            # 🔥 상품 식별용 보조 컬럼
            OpdProduct.product_detail_id.label("product_detail_id"),
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),

            # 🔥 입고 상태는 숫자 대신 글자(status)로 반환
            ErpInboundStatus.status.label("inbound_status"),
        )
        .select_from(ErpStock)
        .outerjoin(
            OpdProduct,
            ErpStock.product_id == OpdProduct.product_id,
        )
        .outerjoin(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
        )
        .outerjoin(
            ErpInbound,
            ErpStock.inbound_id == ErpInbound.inbound_id,
        )
        .outerjoin(
            ErpInboundStatus,
            ErpInbound.inbound_status_id == ErpInboundStatus.inbound_status_id,
        )
    )


def _normalize_start_date(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    try:
        return datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _normalize_end_date(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value.date()

    if isinstance(value, datetime.date):
        return value

    try:
        return datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _is_int_text(value):
    return str(value or "").strip().isdigit()


def _apply_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()

    if not clean:
        return query

    # 🔥 수정: 상품 검색은 상품번(상품상세ID-상품ID) / 상품ID / 상품상세ID / 브랜드 / 상품명 / 중량을 모두 부분검색한다.
    if search_type in {"product", "product_id", "brand", "product_name"}:
        product_no_expr = func.concat(
            cast(OpdProduct.product_detail_id, String),
            "-",
            cast(ErpStock.product_id, String),
        )

        return query.filter(
            product_no_expr.like(like_keyword(clean))
            | cast(OpdProduct.product_detail_id, String).like(like_keyword(clean))
            | cast(ErpStock.product_id, String).like(like_keyword(clean))
            | cast(OpdProductDetail.brand, String).ilike(like_keyword(clean))
            | cast(OpdProductDetail.product_name, String).ilike(like_keyword(clean))
            | cast(OpdProduct.weight, String).like(like_keyword(clean))
        )

    if search_type == "inbound_id":
        return query.filter(cast(ErpStock.inbound_id, String).like(like_keyword(clean)))

    # 🔥 입고 상태 검색
    if search_type == "inbound_status":
        return query.filter(cast(ErpInboundStatus.status, String).ilike(like_keyword(clean)))

    return query


def _stock_detail_base_date_expr():
    return func.coalesce(
        ErpInbound.inbound_complete,
        ErpInbound.inbound_start,
    )


def _apply_date_filter(query, start_date=None, end_date=None, date_filter_type="expiration_date"):
    start = _normalize_start_date(start_date)
    end = _normalize_end_date(end_date)

    # 🔥 대시보드 총 재고량 카드에서 넘어온 경우
    # - 선택 월 기준과 맞추기 위해 입고완료일 우선, 없으면 입고시작일 기준으로 필터링
    # - 일반 상품별 재고 상세 화면에서는 기존처럼 유통기한 기준으로 필터링
    if date_filter_type == "inbound_date":
        date_expr = _stock_detail_base_date_expr()
    else:
        date_expr = ErpStock.expiration_date

    if start:
        query = query.filter(func.date(date_expr) >= start)

    if end:
        query = query.filter(func.date(date_expr) <= end)

    return query


def _row_to_dict(row):
    return {
        "product_id": to_plain_value(row.product_id),
        "product_detail_id": to_plain_value(row.product_detail_id),
        "brand": to_plain_value(row.brand),
        "inbound_id": to_plain_value(row.inbound_id),
        "inbound_status": to_plain_value(row.inbound_status),
        "save_stock": to_plain_value(row.save_stock),
        "sale_stock": to_plain_value(row.sale_stock),
        "scrap_stock": to_plain_value(row.scrap_stock),
        "stock_available": to_plain_value(row.stock_available),
        "expiration_date": to_plain_value(row.expiration_date),
        "inbound_date": to_plain_value(row.inbound_date),
        "product_name": to_plain_value(row.product_name),
        "weight": to_plain_value(row.weight),
        "last_update": to_plain_value(row.last_update),
    }


def count_stocks(
    search_type=SEARCH_TYPE_DEFAULT,
    keyword="",
    start_date=None,
    end_date=None,
    date_filter_type="expiration_date",
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(
            query,
            start_date=start_date,
            end_date=end_date,
            date_filter_type=date_filter_type,
        )
        return query.count()
    finally:
        db.close()


def fetch_stocks(
    search_type=SEARCH_TYPE_DEFAULT,
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_filter_type="expiration_date",
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(
            query,
            start_date=start_date,
            end_date=end_date,
            date_filter_type=date_filter_type,
        )

        rows = (
            query.order_by(
                ErpStock.product_id.asc(),
                ErpStock.inbound_id.asc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()
