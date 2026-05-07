# =========================================================
# 🔥 재고 입고/출고 관리 Repository
# - 입고: ERP.stock + ERP.inbound + ERP.purchase_order_item
# - 출고: OPD.sales_order + OPD.sales_order_item
# - 한 화면에서 입고/출고 내역을 통합 조회
# =========================================================

from datetime import date, datetime, time

from sqlalchemy import String, cast, func, literal, or_, union_all, select, desc

from db.db import SessionLocal
from db.models import (
    ErpInbound,
    ErpInboundStatus,
    ErpPurchaseOrder,
    ErpPurchaseOrderItem,
    ErpStock,
    OpdProduct,
    OpdProductDetail,
    OpdSalesOrder,
    OpdSalesOrderItem,
)
from ..common.query_utils import to_plain_value


# =========================================================
# 🔥 Row -> dict 변환
# =========================================================
def _row_to_dict(row):
    if row is None:
        return None

    if hasattr(row, "_mapping"):
        return {key: to_plain_value(value) for key, value in row._mapping.items()}

    if hasattr(row, "_asdict"):
        return {key: to_plain_value(value) for key, value in row._asdict().items()}

    return row


def _normalize_start_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    clean = str(value).strip()[:10]
    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return datetime.combine(parsed.date(), time.min)
    except ValueError:
        try:
            parsed = datetime.strptime(clean.replace(".", "-"), "%Y-%m-%d")
            return datetime.combine(parsed.date(), time.min)
        except ValueError:
            return None


def _normalize_end_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.max)

    clean = str(value).strip()[:10]
    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return datetime.combine(parsed.date(), time.max)
    except ValueError:
        try:
            parsed = datetime.strptime(clean.replace(".", "-"), "%Y-%m-%d")
            return datetime.combine(parsed.date(), time.max)
        except ValueError:
            return None


def _inbound_date_expr():
    return func.coalesce(
        ErpInbound.inbound_complete,
        ErpInbound.inbound_start,
    )


def _apply_date_filter(query, date_expr, start_date=None, end_date=None):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if start_dt:
        query = query.filter(date_expr >= start_dt)

    if end_dt:
        query = query.filter(date_expr <= end_dt)

    return query


def _keyword_pattern(keyword):
    keyword = str(keyword or "").strip()
    if not keyword:
        return None
    return f"%{keyword.lower()}%"


# =========================================================
# 🔥 입고 조회 기본 쿼리
# =========================================================
def _base_inbound_query():
    event_date = _inbound_date_expr()
    amount_expr = func.coalesce(
        ErpStock.save_stock * ErpPurchaseOrderItem.purchase_price,
        0,
    )

    return (
        select(
            literal("입고").label("inout_type"),
            ErpInbound.inbound_id.label("inbound_id"),
            literal(None).label("sales_order_id"),
            ErpStock.product_id.label("product_id"),
            OpdProduct.product_detail_id.label("product_detail_id"),
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),
            ErpStock.save_stock.label("quantity"),
            ErpPurchaseOrderItem.purchase_price.label("unit_price"),
            amount_expr.label("amount"),
            ErpInboundStatus.status.label("status"),
            event_date.label("event_date"),
        )
        .select_from(ErpStock)
        .join(
            ErpInbound,
            ErpStock.inbound_id == ErpInbound.inbound_id,
        )
        .outerjoin(
            ErpInboundStatus,
            ErpInbound.inbound_status_id == ErpInboundStatus.inbound_status_id,
        )
        .join(
            ErpPurchaseOrder,
            ErpInbound.purchase_order_id == ErpPurchaseOrder.purchase_order_id,
        )
        .join(
            ErpPurchaseOrderItem,
            (ErpPurchaseOrder.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id)
            & (ErpStock.product_id == ErpPurchaseOrderItem.product_id),
        )
        .outerjoin(
            OpdProduct,
            ErpStock.product_id == OpdProduct.product_id,
        )
        .outerjoin(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
        )
        .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
        .filter(ErpInbound.inbound_status_id == 103)
    )


# =========================================================
# 🔥 출고 조회 기본 쿼리
# =========================================================
def _base_outbound_query():
    return (
        select(
            literal("출고").label("inout_type"),
            OpdSalesOrderItem.inbound_id.label("inbound_id"),
            OpdSalesOrder.sales_order_id.label("sales_order_id"),
            OpdSalesOrderItem.product_id.label("product_id"),
            OpdProduct.product_detail_id.label("product_detail_id"),
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),
            OpdSalesOrderItem.quantity.label("quantity"),
            OpdSalesOrderItem.retail_price.label("unit_price"),
            OpdSalesOrderItem.total_amount.label("amount"),
            literal("출고 완료").label("status"),
            OpdSalesOrder.order_date.label("event_date"),
        )
        .select_from(OpdSalesOrder)
        .join(
            OpdSalesOrderItem,
            OpdSalesOrder.sales_order_id == OpdSalesOrderItem.sales_order_id,
        )
        .outerjoin(
            OpdProduct,
            OpdSalesOrderItem.product_id == OpdProduct.product_id,
        )
        .outerjoin(
            OpdProductDetail,
            OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
        )
    )


def _apply_inbound_search_filter(query, search_type="", keyword=""):
    pattern = _keyword_pattern(keyword)
    if not pattern:
        return query

    search_type = search_type or "all"

    if search_type == "inbound_id":
        return query.filter(cast(ErpInbound.inbound_id, String).ilike(pattern))

    if search_type == "product_no":
        product_no_expr = func.concat(
            cast(OpdProduct.product_detail_id, String),
            "-",
            cast(ErpStock.product_id, String),
        )
        return query.filter(
            or_(
                product_no_expr.like(pattern),
                cast(OpdProduct.product_detail_id, String).ilike(pattern),
                cast(ErpStock.product_id, String).ilike(pattern),
            )
        )

    if search_type in ("product", "product_name", "brand"):
        return query.filter(
            or_(
                func.lower(func.coalesce(OpdProductDetail.brand, "")).like(pattern),
                func.lower(func.coalesce(OpdProductDetail.product_name, "")).like(pattern),
                cast(OpdProduct.weight, String).ilike(pattern),
            )
        )

    if search_type == "status":
        return query.filter(func.lower(func.coalesce(ErpInboundStatus.status, "")).like(pattern))

    if search_type == "inout_type":
        return query.filter(literal("입고").ilike(pattern))

    return query.filter(
        or_(
            cast(ErpInbound.inbound_id, String).ilike(pattern),
            func.concat(cast(OpdProduct.product_detail_id, String), "-", cast(ErpStock.product_id, String)).like(pattern),
            cast(OpdProduct.product_detail_id, String).ilike(pattern),
            cast(ErpStock.product_id, String).ilike(pattern),
            func.lower(func.coalesce(OpdProductDetail.brand, "")).like(pattern),
            func.lower(func.coalesce(OpdProductDetail.product_name, "")).like(pattern),
            cast(OpdProduct.weight, String).ilike(pattern),
            func.lower(func.coalesce(ErpInboundStatus.status, "")).like(pattern),
        )
    )


def _apply_outbound_search_filter(query, search_type="", keyword=""):
    pattern = _keyword_pattern(keyword)
    if not pattern:
        return query

    search_type = search_type or "all"

    if search_type == "sales_order_id":
        return query.filter(cast(OpdSalesOrder.sales_order_id, String).ilike(pattern))

    if search_type == "inbound_id":
        return query.filter(cast(OpdSalesOrderItem.inbound_id, String).ilike(pattern))

    if search_type == "product_no":
        product_no_expr = func.concat(
            cast(OpdProduct.product_detail_id, String),
            "-",
            cast(OpdSalesOrderItem.product_id, String),
        )
        return query.filter(
            or_(
                product_no_expr.like(pattern),
                cast(OpdProduct.product_detail_id, String).ilike(pattern),
                cast(OpdSalesOrderItem.product_id, String).ilike(pattern),
            )
        )

    if search_type in ("product", "product_name", "brand"):
        return query.filter(
            or_(
                func.lower(func.coalesce(OpdProductDetail.brand, "")).like(pattern),
                func.lower(func.coalesce(OpdProductDetail.product_name, "")).like(pattern),
                cast(OpdProduct.weight, String).ilike(pattern),
            )
        )

    if search_type == "status":
        return query.filter(literal("출고 완료").ilike(pattern))

    if search_type == "inout_type":
        return query.filter(literal("출고").ilike(pattern))

    return query.filter(
        or_(
            cast(OpdSalesOrder.sales_order_id, String).ilike(pattern),
            cast(OpdSalesOrderItem.inbound_id, String).ilike(pattern),
            func.concat(cast(OpdProduct.product_detail_id, String), "-", cast(OpdSalesOrderItem.product_id, String)).like(pattern),
            cast(OpdProduct.product_detail_id, String).ilike(pattern),
            cast(OpdSalesOrderItem.product_id, String).ilike(pattern),
            func.lower(func.coalesce(OpdProductDetail.brand, "")).like(pattern),
            func.lower(func.coalesce(OpdProductDetail.product_name, "")).like(pattern),
            cast(OpdProduct.weight, String).ilike(pattern),
        )
    )


def _parse_sort_date(value):
    if not value:
        return datetime.min

    if isinstance(value, datetime):
        return value

    if isinstance(value, date):
        return datetime.combine(value, time.min)

    clean = str(value).strip().replace(".", "-")[:19]
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(clean[:len(fmt)], fmt)
        except ValueError:
            continue

    return datetime.min



def _ordered_limited_rows(db, stmt, limit=50, offset=0):
    # 🔥 SQLAlchemy 2.0 스타일로 실행
    stmt = (
        stmt.order_by(
            desc("event_date"),
            desc("inbound_id"),
            desc("sales_order_id"),
        )
        .limit(limit)
        .offset(offset)
        .execution_options(stream_results=True)
    )

    result = db.execute(stmt).yield_per(1000).mappings()
    return [{key: to_plain_value(value) for key, value in row.items()} for row in result]


def _fetch_union_rows(db, inbound_stmt, outbound_stmt, limit=50, offset=0):
    # 🔥 메모리 최적화: SQLAlchemy 2.0 스타일 + Server-side cursor 설정
    # - stream_results=True: PostgreSQL에서 rows를 한 번에 가져오지 않고 스트리밍합니다.
    # - mappings(): ORM 객체화 오버헤드를 줄이기 위해 dict 형태의 RowMapping을 사용합니다.
    
    union_subq = union_all(
        inbound_stmt,
        outbound_stmt,
    ).subquery("stock_inout_union")

    stmt = (
        select(union_subq)
        .order_by(
            union_subq.c.event_date.desc(),
            union_subq.c.inbound_id.desc(),
            union_subq.c.sales_order_id.desc(),
        )
        .limit(limit)
        .offset(offset)
        .execution_options(stream_results=True) # 서버사이드 커서 활성화
    )

    # yield_per를 사용하여 일정 단위로 fetch합니다.
    result = db.execute(stmt).yield_per(1000).mappings()
    
    return [{key: to_plain_value(value) for key, value in row.items()} for row in result]



# =========================================================
# 🔥 입고/출고 통합 조회
# =========================================================
def fetch_stock_inout_rows(
    search_type="all",
    keyword="",
    inout_type="all",
    start_date=None,
    end_date=None,
    limit=50,
    offset=0,
):
    db = SessionLocal()

    try:
        inout_type = inout_type or "all"

        inbound_query = None
        outbound_query = None

        if inout_type in ("all", "inbound", "입고"):
            inbound_stmt = _base_inbound_query()
            inbound_stmt = _apply_date_filter(
                inbound_stmt,
                _inbound_date_expr(),
                start_date,
                end_date,
            )
            inbound_stmt = _apply_inbound_search_filter(
                inbound_stmt,
                search_type=search_type,
                keyword=keyword,
            )

        if inout_type in ("all", "outbound", "출고"):
            outbound_stmt = _base_outbound_query()
            outbound_stmt = _apply_date_filter(
                outbound_stmt,
                OpdSalesOrder.order_date,
                start_date,
                end_date,
            )
            outbound_stmt = _apply_outbound_search_filter(
                outbound_stmt,
                search_type=search_type,
                keyword=keyword,
            )

        if inbound_stmt is not None and outbound_stmt is not None:
            return _fetch_union_rows(
                db,
                inbound_stmt,
                outbound_stmt,
                limit=limit,
                offset=offset,
            )

        if inbound_stmt is not None:
            return _ordered_limited_rows(
                db,
                inbound_stmt,
                limit=limit,
                offset=offset,
            )

        if outbound_stmt is not None:
            return _ordered_limited_rows(
                db,
                outbound_stmt,
                limit=limit,
                offset=offset,
            )

        return []

    finally:
        db.close()


def count_stock_inout_rows(
    search_type="all",
    keyword="",
    inout_type="all",
    start_date=None,
    end_date=None,
):
    db = SessionLocal()

    try:
        inout_type = inout_type or "all"
        total_count = 0

        if inout_type in ("all", "inbound", "입고"):
            inbound_stmt = _base_inbound_query()
            inbound_stmt = _apply_date_filter(
                inbound_stmt,
                _inbound_date_expr(),
                start_date,
                end_date,
            )
            inbound_stmt = _apply_inbound_search_filter(
                inbound_stmt,
                search_type=search_type,
                keyword=keyword,
            )
            # count() 대신 select(func.count()) 사용
            count_stmt = select(func.count()).select_from(inbound_stmt.subquery())
            total_count += db.execute(count_stmt).scalar() or 0

        if inout_type in ("all", "outbound", "출고"):
            outbound_stmt = _base_outbound_query()
            outbound_stmt = _apply_date_filter(
                outbound_stmt,
                OpdSalesOrder.order_date,
                start_date,
                end_date,
            )
            outbound_stmt = _apply_outbound_search_filter(
                outbound_stmt,
                search_type=search_type,
                keyword=keyword,
            )
            count_stmt = select(func.count()).select_from(outbound_stmt.subquery())
            total_count += db.execute(count_stmt).scalar() or 0

        return total_count

    finally:
        db.close()


__all__ = [
    "fetch_stock_inout_rows",
    "count_stock_inout_rows",
]
