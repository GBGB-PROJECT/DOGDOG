# =========================================================
# 🔥 불량현황 Repository
# - ERP.inbound + ERP.inbound_status JOIN
# - ERP.purchase_order + ERP.purchase_order_item + OPD.product + OPD.product_detail JOIN
# - 생산관리 메인 대시보드의 불량 내역과 동일하게 defective 기준 조회
# - 검색어, 날짜 범위, 50개 단위 페이지네이션 처리
# =========================================================

import datetime

from sqlalchemy import cast, func, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import (
    ErpInbound,
    ErpInboundStatus,
    ErpPurchaseOrder,
    ErpPurchaseOrderItem,
    ErpSupplier,
    OpdProduct,
    OpdProductDetail,
)
from ..common.query_utils import like_keyword, to_plain_value


# =========================================================
# 🔥 Row 변환 공통 함수
# =========================================================
def _row_to_dict(row):
    if row is None:
        return None

    if hasattr(row, "_mapping"):
        return {key: to_plain_value(value) for key, value in row._mapping.items()}

    if hasattr(row, "_asdict"):
        return {key: to_plain_value(value) for key, value in row._asdict().items()}

    return row


# =========================================================
# 🔥 숫자 검색 보정
# =========================================================
def _is_int_text(value):
    return str(value or "").strip().isdigit()


# =========================================================
# 🔥 날짜 필터 보정
# - Swagger/Flet DatePicker에서 넘어오는 date, datetime, str 모두 처리
# - 시작일은 00:00:00, 종료일은 23:59:59로 처리
# =========================================================
def _normalize_start_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return value.replace(hour=0, minute=0, second=0, microsecond=0)

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
        return value.replace(hour=23, minute=59, second=59, microsecond=999999)

    if isinstance(value, datetime.date):
        return datetime.datetime.combine(value, datetime.time.max)

    try:
        parsed = datetime.datetime.strptime(str(value)[:10], "%Y-%m-%d")
        return datetime.datetime.combine(parsed.date(), datetime.time.max)
    except ValueError:
        return None


# =========================================================
# 🔥 불량 기본 JOIN 쿼리
# - 불량수량: ERP.purchase_order_item.defective
# - 불량금액: defective * purchase_price
# - 생산관리 대시보드 불량 카드와 기준을 맞춤
# =========================================================
def _base_query(db):
    defective_amount_expr = func.coalesce(
        ErpPurchaseOrderItem.defective * ErpPurchaseOrderItem.purchase_price,
        0,
    )

    return (
        db.query(
            ErpInbound.inbound_id.label("inbound_id"),
            ErpInbound.purchase_order_id.label("purchase_order_id"),
            ErpPurchaseOrder.supplier_id.label("supplier_id"),
            ErpSupplier.supplier_name.label("supplier_name"),
            ErpInboundStatus.status.label("inbound_status"),
            ErpPurchaseOrderItem.product_id.label("product_id"),
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.product_name.label("product_name"),
            ErpPurchaseOrderItem.defective.label("defective"),
            ErpPurchaseOrderItem.purchase_price.label("purchase_price"),
            defective_amount_expr.label("defective_amount"),
            ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
            ErpInbound.inbound_start.label("inbound_start"),
            ErpInbound.inbound_complete.label("inbound_complete"),
            ErpInbound.employee_id.label("employee_id"),
            ErpInbound.last_update.label("last_update"),
        )
        .select_from(ErpInbound)
        .join(
            ErpPurchaseOrder,
            ErpInbound.purchase_order_id == ErpPurchaseOrder.purchase_order_id,
        )
        .join(
            ErpPurchaseOrderItem,
            ErpPurchaseOrder.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id,
        )
        .outerjoin(
            ErpInboundStatus,
            ErpInbound.inbound_status_id == ErpInboundStatus.inbound_status_id,
        )
        .outerjoin(
            ErpSupplier,
            ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id,
        )
        .outerjoin(
            OpdProduct,
            ErpPurchaseOrderItem.product_id == OpdProduct.product_id,
        )
        .outerjoin(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
        )
        # 🔥 취소된 발주건은 제외
        .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
        # 🔥 대시보드 불량 내역과 동일하게 입고완료 상태 기준
        .filter(ErpInbound.inbound_status_id == 103)
        # 🔥 불량수량이 있는 행만 조회
        .filter(ErpPurchaseOrderItem.defective > 0)
    )


# =========================================================
# 🔥 검색 조건 처리
# =========================================================
def _apply_filter(query, search_type="inbound_id", keyword=""):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "inbound_id":
        if _is_int_text(clean):
            return query.filter(ErpInbound.inbound_id == int(clean))
        return query.filter(cast(ErpInbound.inbound_id, String).like(like_keyword(clean)))

    if search_type == "purchase_order_id":
        if _is_int_text(clean):
            return query.filter(ErpInbound.purchase_order_id == int(clean))
        return query.filter(cast(ErpInbound.purchase_order_id, String).like(like_keyword(clean)))

    if search_type == "supplier_id":
        if _is_int_text(clean):
            return query.filter(ErpPurchaseOrder.supplier_id == int(clean))
        return query.filter(cast(ErpPurchaseOrder.supplier_id, String).like(like_keyword(clean)))

    if search_type == "supplier_name":
        return query.filter(ErpSupplier.supplier_name.ilike(like_keyword(clean)))

    if search_type == "inbound_status":
        return query.filter(ErpInboundStatus.status.ilike(like_keyword(clean)))

    if search_type == "product_id":
        if _is_int_text(clean):
            return query.filter(ErpPurchaseOrderItem.product_id == int(clean))
        return query.filter(cast(ErpPurchaseOrderItem.product_id, String).like(like_keyword(clean)))

    if search_type == "brand":
        return query.filter(OpdProductDetail.brand.ilike(like_keyword(clean)))

    if search_type == "product_name":
        return query.filter(OpdProductDetail.product_name.ilike(like_keyword(clean)))

    if search_type == "employee_id":
        if _is_int_text(clean):
            return query.filter(ErpInbound.employee_id == int(clean))
        return query.filter(cast(ErpInbound.employee_id, String).like(like_keyword(clean)))

    if search_type == "inbound_start":
        return query.filter(cast(ErpInbound.inbound_start, String).like(like_keyword(clean)))

    if search_type == "inbound_complete":
        return query.filter(cast(ErpInbound.inbound_complete, String).like(like_keyword(clean)))

    if search_type == "inbound_scheduled_date":
        return query.filter(cast(ErpPurchaseOrder.inbound_scheduled_date, String).like(like_keyword(clean)))

    return query.filter(
        or_(
            cast(ErpInbound.inbound_id, String).like(like_keyword(clean)),
            cast(ErpInbound.purchase_order_id, String).like(like_keyword(clean)),
            ErpInboundStatus.status.ilike(like_keyword(clean)),
            ErpSupplier.supplier_name.ilike(like_keyword(clean)),
            cast(ErpPurchaseOrderItem.product_id, String).like(like_keyword(clean)),
            OpdProductDetail.brand.ilike(like_keyword(clean)),
            OpdProductDetail.product_name.ilike(like_keyword(clean)),
        )
    )


# =========================================================
# 🔥 날짜 범위 처리
# - DatePicker 기준은 검색조건과 분리해서 date_filter_type으로 받는다.
# - 불량현황조회 화면 기본 기준: 입고완료일(inbound_complete)
# =========================================================
def _apply_date_filter(query, date_filter_type="inbound_complete", start_date=None, end_date=None):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if not start_dt and not end_dt:
        return query

    date_column = ErpInbound.inbound_complete

    if date_filter_type == "inbound_start":
        date_column = ErpInbound.inbound_start
    elif date_filter_type == "inbound_scheduled_date":
        date_column = ErpPurchaseOrder.inbound_scheduled_date
    elif date_filter_type == "inbound_complete":
        date_column = ErpInbound.inbound_complete

    if start_dt:
        query = query.filter(date_column >= start_dt)

    if end_dt:
        query = query.filter(date_column <= end_dt)

    return query


# =========================================================
# 🔥 불량현황 목록 조회
# =========================================================
def fetch_defectives(
    search_type="inbound_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
    date_filter_type="inbound_complete",
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(query, date_filter_type, start_date, end_date)

        rows = (
            query
            .order_by(
                ErpInbound.inbound_complete.desc().nullslast(),
                ErpInbound.inbound_id.desc(),
                ErpPurchaseOrderItem.product_id.asc(),
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()


# =========================================================
# 🔥 불량현황 전체 건수
# =========================================================
def count_defectives(
    search_type="inbound_id",
    keyword="",
    start_date=None,
    end_date=None,
    date_filter_type="inbound_complete",
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type, keyword)
        query = _apply_date_filter(query, date_filter_type, start_date, end_date)
        return query.count()

    finally:
        db.close()
