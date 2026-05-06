# =========================================================
# 🔥 재고 현황 대시보드 Repository
# - ERP.stock / ERP.inbound / ERP.purchase_order / ERP.purchase_order_item
# - OPD.sales_order / OPD.sales_order_item
# - OPD.product / OPD.product_detail JOIN
# =========================================================

from datetime import date, datetime, time, timedelta

from sqlalchemy import func

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
# - Decimal / Date / DateTime이 Flet에서 터지지 않도록 plain value로 변환
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
        return None


# =========================================================
# 🔥 입고 기준일
# - 입고완료일 우선
# - 없으면 입고시작일 사용
# =========================================================
def _inbound_dashboard_date_expr():
    return func.coalesce(
        ErpInbound.inbound_complete,
        ErpInbound.inbound_start,
    )


def _apply_year_month_filter(query, date_expr, year=None, month=None):
    if year:
        query = query.filter(func.extract("year", date_expr) == int(year))

    if month:
        query = query.filter(func.extract("month", date_expr) == int(month))

    return query


def _build_month_range(year: int, month: int):
    month_start = date(year, month, 1)

    if month == 12:
        month_end = date(year, 12, 31)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    return month_start, month_end


# =========================================================
# 🔥 입고 기본 JOIN
# - 수량: ERP.stock.save_stock
# - 금액: ERP.stock.save_stock * ERP.purchase_order_item.purchase_price
# =========================================================
def _base_inbound_query(db):
    dashboard_date = _inbound_dashboard_date_expr()
    inbound_amount_expr = func.coalesce(
        ErpStock.save_stock * ErpPurchaseOrderItem.purchase_price,
        0,
    )

    return (
        db.query(
            ErpInbound.inbound_id.label("inbound_id"),
            ErpInbound.purchase_order_id.label("purchase_order_id"),
            ErpInbound.inbound_status_id.label("inbound_status_id"),
            ErpInboundStatus.status.label("inbound_status"),
            ErpInbound.inbound_start.label("inbound_start"),
            ErpInbound.inbound_complete.label("inbound_complete"),

            ErpStock.product_id.label("product_id"),
            ErpStock.save_stock.label("quantity"),
            ErpStock.stock_available.label("stock_available"),

            OpdProductDetail.product_name.label("product_name"),
            OpdProductDetail.brand.label("brand"),

            ErpPurchaseOrderItem.purchase_price.label("unit_price"),
            inbound_amount_expr.label("amount"),
            dashboard_date.label("dashboard_date"),
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
# 🔥 출고/매출 기본 JOIN
# - 수량: OPD.sales_order_item.quantity
# - 금액: OPD.sales_order_item.total_amount
# - 날짜: OPD.sales_order.order_date
# =========================================================
def _base_outbound_query(db):
    return (
        db.query(
            OpdSalesOrder.sales_order_id.label("sales_order_id"),
            OpdSalesOrder.order_number.label("order_number"),
            OpdSalesOrder.order_date.label("order_date"),

            OpdSalesOrderItem.inbound_id.label("inbound_id"),
            OpdSalesOrderItem.product_id.label("product_id"),
            OpdSalesOrderItem.quantity.label("quantity"),
            OpdSalesOrderItem.retail_price.label("unit_price"),
            OpdSalesOrderItem.total_amount.label("amount"),

            OpdProductDetail.product_name.label("product_name"),
            OpdProductDetail.brand.label("brand"),
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


# =========================================================
# 🔥 대시보드 기본 연월
# - 입고완료일과 주문일 중 더 최신 월 사용
# =========================================================
def fetch_stock_dashboard_base_year_month():
    db = SessionLocal()

    try:
        inbound_date = _inbound_dashboard_date_expr()

        latest_inbound_date = (
            db.query(inbound_date.label("dashboard_date"))
            .select_from(ErpInbound)
            .filter(inbound_date.isnot(None))
            .order_by(inbound_date.desc())
            .limit(1)
            .scalar()
        )

        latest_order_date = (
            db.query(OpdSalesOrder.order_date)
            .filter(OpdSalesOrder.order_date.isnot(None))
            .order_by(OpdSalesOrder.order_date.desc())
            .limit(1)
            .scalar()
        )

        candidates = [
            value for value in [latest_inbound_date, latest_order_date]
            if value is not None
        ]

        if not candidates:
            today = date.today()
            return today.year, today.month

        latest_date = max(candidates)
        return int(latest_date.year), int(latest_date.month)

    finally:
        db.close()


def fetch_stock_dashboard_base_year():
    year, _month = fetch_stock_dashboard_base_year_month()
    return year


# =========================================================
# 🔥 최근 입고 내역
# =========================================================
def fetch_recent_inbound_rows(limit=5, year=None, month=None):
    db = SessionLocal()

    try:
        query = _base_inbound_query(db)
        query = _apply_year_month_filter(
            query,
            _inbound_dashboard_date_expr(),
            year,
            month,
        )

        rows = (
            query
            .order_by(
                _inbound_dashboard_date_expr().desc().nullslast(),
                ErpInbound.inbound_id.desc(),
            )
            .limit(limit)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()


# =========================================================
# 🔥 최근 출고/판매 내역
# =========================================================
def fetch_recent_outbound_rows(limit=5, year=None, month=None):
    db = SessionLocal()

    try:
        query = _base_outbound_query(db)
        query = _apply_year_month_filter(
            query,
            OpdSalesOrder.order_date,
            year,
            month,
        )

        rows = (
            query
            .order_by(
                OpdSalesOrder.order_date.desc().nullslast(),
                OpdSalesOrder.sales_order_id.desc(),
            )
            .limit(limit)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()


# =========================================================
# 🔥 입고/출고 건수
# =========================================================
def count_inbound_rows(year=None, month=None):
    db = SessionLocal()

    try:
        query = _base_inbound_query(db)
        query = _apply_year_month_filter(
            query,
            _inbound_dashboard_date_expr(),
            year,
            month,
        )
        return query.count()

    finally:
        db.close()


def count_outbound_rows(year=None, month=None):
    db = SessionLocal()

    try:
        query = _base_outbound_query(db)
        query = _apply_year_month_filter(
            query,
            OpdSalesOrder.order_date,
            year,
            month,
        )
        return query.count()

    finally:
        db.close()


# =========================================================
# 🔥 월별 입출고 차트
# - 입고: save_stock * purchase_price
# - 출고: sales_order_item.total_amount
# - service에서 K 단위로 변환
# =========================================================
def fetch_monthly_stock_chart(year=None):
    target_year = int(year or fetch_stock_dashboard_base_year())

    db = SessionLocal()

    try:
        inbound_date = _inbound_dashboard_date_expr()
        inbound_month_expr = func.extract("month", inbound_date)
        outbound_month_expr = func.extract("month", OpdSalesOrder.order_date)

        inbound_amount_expr = func.coalesce(
            ErpStock.save_stock * ErpPurchaseOrderItem.purchase_price,
            0,
        )

        inbound_rows = (
            db.query(
                inbound_month_expr.label("month"),
                func.coalesce(func.sum(inbound_amount_expr), 0).label("inbound_amount"),
            )
            .select_from(ErpStock)
            .join(
                ErpInbound,
                ErpStock.inbound_id == ErpInbound.inbound_id,
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
            .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
            .filter(ErpInbound.inbound_status_id == 103)
            .filter(func.extract("year", inbound_date) == target_year)
            .group_by(inbound_month_expr)
            .all()
        )

        outbound_rows = (
            db.query(
                outbound_month_expr.label("month"),
                func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).label("outbound_amount"),
            )
            .select_from(OpdSalesOrder)
            .join(
                OpdSalesOrderItem,
                OpdSalesOrder.sales_order_id == OpdSalesOrderItem.sales_order_id,
            )
            .filter(func.extract("year", OpdSalesOrder.order_date) == target_year)
            .group_by(outbound_month_expr)
            .all()
        )

        return {
            "inbound_rows": [_row_to_dict(row) for row in inbound_rows],
            "outbound_rows": [_row_to_dict(row) for row in outbound_rows],
        }

    finally:
        db.close()


# =========================================================
# 🔥 매출 TOP 재고
# - 해당 월 total_amount 합계 기준 TOP N
# - 현재고는 ERP.stock.stock_available 합계
# =========================================================

# =========================================================
# 🔥 선택 월 총 재고량
# - 기준 월: 입고완료일 우선, 없으면 입고시작일
# - 수량 기준: ERP.stock.stock_available 합계
# =========================================================
def fetch_month_total_stock_quantity(year=None, month=None):
    db = SessionLocal()

    try:
        target_year, target_month = (
            (int(year), int(month))
            if year and month
            else fetch_stock_dashboard_base_year_month()
        )

        dashboard_date = _inbound_dashboard_date_expr()

        total_quantity = (
            db.query(
                func.coalesce(func.sum(ErpStock.stock_available), 0)
            )
            .select_from(ErpStock)
            .join(
                ErpInbound,
                ErpStock.inbound_id == ErpInbound.inbound_id,
            )
            .filter(ErpInbound.inbound_status_id == 103)
            .filter(func.extract("year", dashboard_date) == target_year)
            .filter(func.extract("month", dashboard_date) == target_month)
            .scalar()
        )

        return to_plain_value(total_quantity) or 0

    finally:
        db.close()


# =========================================================
# 🔥 유통기한 임박 재고
# - 오늘 기준 30일 이내 만료 예정인 재고 행 개수
# - 상품별 재고 상세 화면의 유통기한 DatePicker 필터와 같은 기준
# =========================================================
def count_expiring_stock_rows(days=30):
    db = SessionLocal()

    try:
        today = date.today()
        end_date = today + timedelta(days=int(days or 30))

        return (
            db.query(func.count())
            .select_from(ErpStock)
            .join(
                ErpInbound,
                ErpStock.inbound_id == ErpInbound.inbound_id,
            )
            .filter(ErpInbound.inbound_status_id == 103)
            .filter(ErpStock.stock_available > 0)
            .filter(ErpStock.expiration_date >= today)
            .filter(ErpStock.expiration_date <= end_date)
            .scalar()
        ) or 0

    finally:
        db.close()


def fetch_top_sales_stock_rows(limit=3, year=None, month=None):
    db = SessionLocal()

    try:
        target_year, target_month = (
            (int(year), int(month))
            if year and month
            else fetch_stock_dashboard_base_year_month()
        )
        month_start, month_end = _build_month_range(target_year, target_month)
        month_start_dt = datetime.combine(month_start, time.min)
        month_end_dt = datetime.combine(month_end, time.max)

        current_stock_subquery = (
            db.query(
                ErpStock.product_id.label("product_id"),
                func.coalesce(func.sum(ErpStock.stock_available), 0).label("current_stock"),
            )
            .group_by(ErpStock.product_id)
            .subquery()
        )

        # 🔥 추가: 생산지시서 자동 입력용 구매단가
        # - ErpPurchaseOrderItem을 매출 집계 쿼리에 직접 JOIN하면
        #   발주 이력이 여러 건인 상품에서 sales_quantity / sales_amount가 중복 집계될 수 있음
        # - 그래서 product_id별 구매단가를 별도 subquery로 먼저 묶은 뒤 JOIN
        purchase_price_subquery = (
            db.query(
                ErpPurchaseOrderItem.product_id.label("product_id"),
                func.coalesce(func.max(ErpPurchaseOrderItem.purchase_price), 0).label("purchase_price"),
            )
            .join(
                ErpPurchaseOrder,
                ErpPurchaseOrderItem.purchase_order_id == ErpPurchaseOrder.purchase_order_id,
            )
            .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
            .group_by(ErpPurchaseOrderItem.product_id)
            .subquery()
        )

        rows = (
            db.query(
                OpdSalesOrderItem.product_id.label("product_id"),
                OpdProductDetail.product_name.label("product_name"),
                OpdProductDetail.brand.label("brand"),

                func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("sales_quantity"),
                func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).label("sales_amount"),
                func.coalesce(current_stock_subquery.c.current_stock, 0).label("current_stock"),

                # 🔥 추가: stock_status_view.py → 생산지시서 자동 입력용 단가
                # - 구매단가: ERP.purchase_order_item.purchase_price
                # - 판매가: OPD.sales_order_item.retail_price 기준
                func.coalesce(purchase_price_subquery.c.purchase_price, 0).label("purchase_price"),
                func.coalesce(func.max(OpdSalesOrderItem.retail_price), 0).label("retail_price"),
            )
            .select_from(OpdSalesOrderItem)
            .join(
                OpdSalesOrder,
                OpdSalesOrderItem.sales_order_id == OpdSalesOrder.sales_order_id,
            )
            .outerjoin(
                OpdProduct,
                OpdSalesOrderItem.product_id == OpdProduct.product_id,
            )
            .outerjoin(
                OpdProductDetail,
                OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
            )
            .outerjoin(
                current_stock_subquery,
                OpdSalesOrderItem.product_id == current_stock_subquery.c.product_id,
            )
            .outerjoin(
                purchase_price_subquery,
                OpdSalesOrderItem.product_id == purchase_price_subquery.c.product_id,
            )
            .filter(OpdSalesOrder.order_date >= month_start_dt)
            .filter(OpdSalesOrder.order_date <= month_end_dt)
            .group_by(
                OpdSalesOrderItem.product_id,
                OpdProductDetail.product_name,
                OpdProductDetail.brand,
                current_stock_subquery.c.current_stock,
                purchase_price_subquery.c.purchase_price,
            )
            .order_by(
                func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).desc(),
                func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).desc(),
            )
            .limit(limit)
            .all()
        )

        return [_row_to_dict(row) for row in rows]

    finally:
        db.close()

__all__ = [
    "fetch_stock_dashboard_base_year",
    "fetch_stock_dashboard_base_year_month",
    "fetch_recent_inbound_rows",
    "fetch_recent_outbound_rows",
    "count_inbound_rows",
    "count_outbound_rows",
    "count_expiring_stock_rows",
    "fetch_monthly_stock_chart",
    "fetch_month_total_stock_quantity",
    "fetch_top_sales_stock_rows",
]
