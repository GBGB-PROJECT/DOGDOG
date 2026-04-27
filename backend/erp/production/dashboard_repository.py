# =========================================================
# 🔥 생산관리 메인 대시보드 Repository
# - 업로드한 실제 테이블 구조 기준으로 다시 작성
# - ERP.inbound / ERP.inbound_status / ERP.stock
# - ERP.purchase_order / ERP.purchase_order_item / ERP.supplier
# - OPD.product / OPD.product_detail JOIN
# =========================================================

from datetime import date

from sqlalchemy import and_, func

from db.db import SessionLocal
from db.models import (
    ErpInbound,
    ErpInboundStatus,
    ErpPurchaseOrder,
    ErpPurchaseOrderItem,
    ErpStock,
    ErpSupplier,
    OpdProduct,
    OpdProductDetail,
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


# =========================================================
# 🔥 생산관리 기준일
# - 실제 생산/입고 결과 화면이므로 입고완료일 우선
# - 입고완료일이 없으면 입고시작일 사용
# =========================================================
def _dashboard_date_expr():
    return func.coalesce(
        ErpInbound.inbound_complete,
        ErpInbound.inbound_start,
    )


# =========================================================
# 🔥 실제 생산 입고 기본 JOIN
# - 생산 입고 수량은 ERP.stock.save_stock 기준
# - 금액은 save_stock * purchase_order_item.purchase_price 기준
# - purchase_order_item.quantity는 발주 수량이라 대시보드 입고량으로 쓰지 않음
# =========================================================
def _base_stock_production_query(db):
    dashboard_date = _dashboard_date_expr()
    production_amount_expr = func.coalesce(
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
            ErpStock.save_stock.label("save_stock"),
            ErpStock.sale_stock.label("sale_stock"),
            ErpStock.scrap_stock.label("scrap_stock"),
            ErpStock.stock_available.label("stock_available"),
            ErpStock.expiration_date.label("expiration_date"),
            ErpPurchaseOrder.contract_date.label("contract_date"),
            ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
            ErpPurchaseOrder.supplier_id.label("supplier_id"),
            ErpSupplier.supplier_name.label("supplier_name"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProductDetail.brand.label("brand"),
            ErpPurchaseOrderItem.purchase_price.label("purchase_price"),
            production_amount_expr.label("production_amount"),
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
            ErpSupplier,
            ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id,
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
        .filter(ErpInbound.inbound_status_id == 103)  # 🔥 inbound_status.html 기준: 입고 완료
    )


# =========================================================
# 🔥 불량 기본 JOIN
# - 불량은 ERP.purchase_order_item.defective 기준
# - 금액은 defective * purchase_price 기준
# =========================================================
def _base_defective_query(db):
    dashboard_date = _dashboard_date_expr()
    defective_amount_expr = func.coalesce(
        ErpPurchaseOrderItem.defective * ErpPurchaseOrderItem.purchase_price,
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
            ErpPurchaseOrder.contract_date.label("contract_date"),
            ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
            ErpPurchaseOrder.supplier_id.label("supplier_id"),
            ErpSupplier.supplier_name.label("supplier_name"),
            ErpPurchaseOrderItem.product_id.label("product_id"),
            ErpPurchaseOrderItem.defective.label("defective"),
            ErpPurchaseOrderItem.purchase_price.label("purchase_price"),
            defective_amount_expr.label("defective_amount"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProductDetail.brand.label("brand"),
            dashboard_date.label("dashboard_date"),
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
        .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
        .filter(ErpInbound.inbound_status_id == 103)  # 🔥 입고 완료 건만 대시보드 반영
        .filter(ErpPurchaseOrderItem.defective > 0)
    )


# =========================================================
# 🔥 대시보드 기준 연도
# - API나 화면에서 연도를 넘기지 않으면 DB의 최신 입고완료 연도를 사용
# =========================================================
def fetch_dashboard_base_year():
    db = SessionLocal()
    try:
        dashboard_date = _dashboard_date_expr()
        latest_year = (
            db.query(func.extract("year", dashboard_date).label("year"))
            .select_from(ErpInbound)
            .filter(dashboard_date.isnot(None))
            .order_by(dashboard_date.desc())
            .limit(1)
            .scalar()
        )
        return int(latest_year or date.today().year)
    finally:
        db.close()


# =========================================================
# 🔥 최근 생산 입고 내역 5건
# =========================================================
def fetch_recent_production_rows(limit=5):
    db = SessionLocal()
    try:
        rows = (
            _base_stock_production_query(db)
            .order_by(_dashboard_date_expr().desc().nullslast(), ErpInbound.inbound_id.desc())
            .limit(limit)
            .all()
        )
        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()


# =========================================================
# 🔥 최근 불량 내역 5건
# =========================================================
def fetch_recent_defective_rows(limit=5):
    db = SessionLocal()
    try:
        rows = (
            _base_defective_query(db)
            .order_by(_dashboard_date_expr().desc().nullslast(), ErpInbound.inbound_id.desc())
            .limit(limit)
            .all()
        )
        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()


# =========================================================
# 🔥 생산 입고 건수
# =========================================================
def count_production_rows():
    db = SessionLocal()
    try:
        return _base_stock_production_query(db).count()
    finally:
        db.close()


# =========================================================
# 🔥 불량 건수
# =========================================================
def count_defective_rows():
    db = SessionLocal()
    try:
        return _base_defective_query(db).count()
    finally:
        db.close()


# =========================================================
# 🔥 월별 생산/불량 실적
# - 생산: ERP.stock.save_stock * ERP.purchase_order_item.purchase_price
# - 불량: ERP.purchase_order_item.defective * ERP.purchase_order_item.purchase_price
# - 단위 변환은 service에서 천원 단위로 처리
# =========================================================
def fetch_monthly_production_chart(year=None):
    target_year = int(year or fetch_dashboard_base_year())

    db = SessionLocal()
    try:
        dashboard_date = _dashboard_date_expr()
        month_expr = func.extract("month", dashboard_date)

        production_amount_expr = func.coalesce(
            ErpStock.save_stock * ErpPurchaseOrderItem.purchase_price,
            0,
        )

        # 🔥 생산 금액: stock을 기준으로 실제 입고된 재고만 합산
        production_subquery = (
            db.query(
                month_expr.label("month"),
                func.coalesce(func.sum(production_amount_expr), 0).label("production_amount"),
            )
            .select_from(ErpStock)
            .join(ErpInbound, ErpStock.inbound_id == ErpInbound.inbound_id)
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
            .filter(func.extract("year", dashboard_date) == target_year)
            .group_by(month_expr)
            .subquery()
        )

        defective_amount_expr = func.coalesce(
            ErpPurchaseOrderItem.defective * ErpPurchaseOrderItem.purchase_price,
            0,
        )

        # 🔥 불량 금액: purchase_order_item.defective 기준
        defective_subquery = (
            db.query(
                month_expr.label("month"),
                func.coalesce(func.sum(defective_amount_expr), 0).label("defective_amount"),
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
            .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
            .filter(ErpInbound.inbound_status_id == 103)
            .filter(ErpPurchaseOrderItem.defective > 0)
            .filter(func.extract("year", dashboard_date) == target_year)
            .group_by(month_expr)
            .subquery()
        )

        rows = (
            db.query(
                production_subquery.c.month.label("month"),
                func.coalesce(production_subquery.c.production_amount, 0).label("production_amount"),
                func.coalesce(defective_subquery.c.defective_amount, 0).label("defective_amount"),
            )
            .select_from(production_subquery)
            .outerjoin(
                defective_subquery,
                production_subquery.c.month == defective_subquery.c.month,
            )
            .order_by(production_subquery.c.month.asc())
            .all()
        )

        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()


# =========================================================
# =========================================================
# 🔥 최근 발주 카드 5건
# - 카드명: 대표상품명 외 N건
# - 현 재고량: 해당 발주와 연결된 inbound_id의 stock_available만 합산
# - 주의: product_id만으로 stock을 합산하면 과거 모든 입고 재고가 합쳐져 수만 ea로 튀어버림
# =========================================================
def fetch_recent_purchase_cards(limit=5):
    db = SessionLocal()
    try:
        rows = (
            db.query(
                ErpPurchaseOrder.purchase_order_id.label("purchase_order_id"),
                ErpPurchaseOrder.contract_date.label("contract_date"),
                ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
                ErpSupplier.supplier_name.label("supplier_name"),
                func.min(OpdProductDetail.product_name).label("represent_product_name"),
                func.count(ErpPurchaseOrderItem.product_id).label("item_count"),
                func.coalesce(func.sum(ErpStock.stock_available), 0).label("stock_available_sum"),
            )
            .select_from(ErpPurchaseOrder)
            .outerjoin(
                ErpSupplier,
                ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id,
            )
            .outerjoin(
                ErpInbound,
                ErpPurchaseOrder.purchase_order_id == ErpInbound.purchase_order_id,
            )
            .outerjoin(
                ErpPurchaseOrderItem,
                ErpPurchaseOrder.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id,
            )
            .outerjoin(
                ErpStock,
                and_(
                    ErpStock.product_id == ErpPurchaseOrderItem.product_id,
                    ErpStock.inbound_id == ErpInbound.inbound_id,
                ),
            )
            .outerjoin(
                OpdProduct,
                ErpPurchaseOrderItem.product_id == OpdProduct.product_id,
            )
            .outerjoin(
                OpdProductDetail,
                OpdProduct.product_detail_id == OpdProductDetail.product_detail_id,
            )
            .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
            .group_by(
                ErpPurchaseOrder.purchase_order_id,
                ErpPurchaseOrder.contract_date,
                ErpPurchaseOrder.inbound_scheduled_date,
                ErpSupplier.supplier_name,
            )
            .order_by(
                ErpPurchaseOrder.contract_date.desc().nullslast(),
                ErpPurchaseOrder.purchase_order_id.desc(),
            )
            .limit(limit)
            .all()
        )
        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()
