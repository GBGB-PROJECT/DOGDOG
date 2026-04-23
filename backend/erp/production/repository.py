from sqlalchemy import cast, func
from sqlalchemy.types import String

from backend.db.db import SessionLocal
from backend.db.models import ErpSupplier, ErpPurchaseOrder, ErpPurchaseOrderItem, OpdProduct, OpdProductDetail
from backend.erp.common.query_utils import (
    model_to_dict,
    like_keyword,
    normalize_bool_keyword,
    parse_date,
    to_plain_value,
)

SUPPLIER_COLUMNS = [
    "supplier_id", "supplier_name", "brn", "is_contact_status",
    "designated_payment_date", "scheduled_payment_date", "employee_id",
    "memo", "sup_manager", "phone", "last_update",
]


def _row_to_dict(row):
    if row is None:
        return None
    if hasattr(row, "_mapping"):
        return {key: to_plain_value(value) for key, value in row._mapping.items()}
    if hasattr(row, "_asdict"):
        return {key: to_plain_value(value) for key, value in row._asdict().items()}
    return row


def _apply_supplier_filter(query, search_type: str, keyword: str, start_date=None, end_date=None):
    clean = (keyword or "").strip()
    if clean:
        if search_type == "supplier_id":
            query = query.filter(cast(ErpSupplier.supplier_id, String).like(like_keyword(clean)))
        elif search_type == "supplier_name":
            query = query.filter(ErpSupplier.supplier_name.ilike(like_keyword(clean)))
        elif search_type == "brn":
            query = query.filter(ErpSupplier.brn.ilike(like_keyword(clean)))
        elif search_type == "is_contact_status":
            bool_value = normalize_bool_keyword(clean, true_words={"가능"}, false_words={"불가"})
            if bool_value is not None:
                query = query.filter(ErpSupplier.is_contact_status.is_(bool_value))
            else:
                query = query.filter(cast(ErpSupplier.is_contact_status, String).ilike(like_keyword(clean)))
        elif search_type == "sup_manager":
            query = query.filter(ErpSupplier.sup_manager.ilike(like_keyword(clean)))
        elif search_type == "phone":
            query = query.filter(ErpSupplier.phone.ilike(like_keyword(clean)))

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    if parsed_start:
        query = query.filter(func.date(ErpSupplier.last_update) >= parsed_start)
    if parsed_end:
        query = query.filter(func.date(ErpSupplier.last_update) <= parsed_end)
    return query


def count_suppliers(search_type="supplier_name", keyword="", start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(ErpSupplier)
        query = _apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        return query.count()
    finally:
        db.close()


def fetch_suppliers(search_type="supplier_name", keyword="", limit=50, offset=0, start_date=None, end_date=None):
    db = SessionLocal()
    try:
        query = db.query(ErpSupplier)
        query = _apply_supplier_filter(query, search_type, keyword, start_date, end_date)
        rows = query.order_by(ErpSupplier.supplier_id.asc()).limit(limit).offset(offset).all()
        return [model_to_dict(row, SUPPLIER_COLUMNS) for row in rows]
    finally:
        db.close()


def _apply_purchase_order_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()
    if not clean:
        return query
    if search_type == "purchase_order_id":
        return query.filter(cast(ErpPurchaseOrder.purchase_order_id, String).like(like_keyword(clean)))
    if search_type == "supplier_id":
        return query.filter(cast(ErpPurchaseOrder.supplier_id, String).like(like_keyword(clean)))
    if search_type == "supplier_name":
        return query.filter(ErpSupplier.supplier_name.ilike(like_keyword(clean)))
    if search_type == "pay_status":
        lowered = clean.lower()
        if clean in {"결제완료", "완료"} or lowered in {"completed", "complete"}:
            return query.filter(ErpPurchaseOrder.pay_status == "completed")
        if clean in {"결제예정", "예정"} or lowered in {"scheduled", "schedule"}:
            return query.filter(ErpPurchaseOrder.pay_status == "scheduled")
        return query.filter(ErpPurchaseOrder.pay_status.ilike(like_keyword(clean)))
    if search_type == "is_purchase_order_cancel":
        bool_value = normalize_bool_keyword(clean, true_words={"취소", "취소됨"}, false_words={"정상", "미취소", "진행"})
        if bool_value is not None:
            return query.filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(bool_value))
        return query.filter(cast(ErpPurchaseOrder.is_purchase_order_cancel, String).ilike(like_keyword(clean)))
    if search_type == "employee_id":
        return query.filter(cast(ErpPurchaseOrder.employee_id, String).like(like_keyword(clean)))
    if search_type == "product_id":
        return query.filter(cast(ErpPurchaseOrderItem.product_id, String).like(like_keyword(clean)))
    return query


def count_purchase_orders(search_type="purchase_order_id", keyword=""):
    db = SessionLocal()
    try:
        query = (
            db.query(ErpPurchaseOrder.purchase_order_id)
            .outerjoin(ErpSupplier, ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id)
            .outerjoin(ErpPurchaseOrderItem, ErpPurchaseOrder.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id)
        )
        query = _apply_purchase_order_filter(query, search_type, keyword)
        return query.distinct().count()
    finally:
        db.close()


def fetch_purchase_orders(search_type="purchase_order_id", keyword="", limit=50, offset=0):
    db = SessionLocal()
    try:
        final_amount_expr = func.coalesce(ErpPurchaseOrderItem.final_amount, ErpPurchaseOrderItem.total_amount, 0)
        query = (
            db.query(
                ErpPurchaseOrder.purchase_order_id.label("purchase_order_id"),
                ErpPurchaseOrder.supplier_id.label("supplier_id"),
                ErpSupplier.supplier_name.label("supplier_name"),
                ErpPurchaseOrder.contract_date.label("contract_date"),
                ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
                ErpPurchaseOrder.pay_status.label("pay_status"),
                ErpPurchaseOrder.adjustment_date.label("adjustment_date"),
                ErpPurchaseOrder.is_purchase_order_cancel.label("is_purchase_order_cancel"),
                ErpPurchaseOrder.employee_id.label("employee_id"),
                ErpPurchaseOrder.order_form_file_path.label("order_form_file_path"),
                ErpPurchaseOrder.last_update.label("last_update"),
                func.count(ErpPurchaseOrderItem.product_id).label("item_count"),
                func.coalesce(func.sum(final_amount_expr), 0).label("final_amount_sum"),
            )
            .outerjoin(ErpSupplier, ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id)
            .outerjoin(ErpPurchaseOrderItem, ErpPurchaseOrder.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id)
        )
        query = _apply_purchase_order_filter(query, search_type, keyword)
        rows = (
            query.group_by(
                ErpPurchaseOrder.purchase_order_id,
                ErpPurchaseOrder.supplier_id,
                ErpSupplier.supplier_name,
                ErpPurchaseOrder.contract_date,
                ErpPurchaseOrder.inbound_scheduled_date,
                ErpPurchaseOrder.pay_status,
                ErpPurchaseOrder.adjustment_date,
                ErpPurchaseOrder.is_purchase_order_cancel,
                ErpPurchaseOrder.employee_id,
                ErpPurchaseOrder.order_form_file_path,
                ErpPurchaseOrder.last_update,
            )
            .order_by(ErpPurchaseOrder.purchase_order_id.asc())
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()


def fetch_purchase_order_detail(purchase_order_id):
    db = SessionLocal()
    try:
        row = (
            db.query(
                ErpPurchaseOrder.purchase_order_id.label("purchase_order_id"),
                ErpPurchaseOrder.supplier_id.label("supplier_id"),
                ErpSupplier.supplier_name.label("supplier_name"),
                ErpSupplier.brn.label("supplier_brn"),
                ErpSupplier.phone.label("supplier_phone"),
                ErpSupplier.sup_manager.label("supplier_manager"),
                ErpPurchaseOrder.contract_date.label("contract_date"),
                ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
                ErpPurchaseOrder.pay_status.label("pay_status"),
                ErpPurchaseOrder.adjustment_date.label("adjustment_date"),
                ErpPurchaseOrder.is_purchase_order_cancel.label("is_purchase_order_cancel"),
                ErpPurchaseOrder.employee_id.label("employee_id"),
                ErpPurchaseOrder.order_form_file_path.label("order_form_file_path"),
                ErpPurchaseOrder.last_update.label("last_update"),
            )
            .outerjoin(ErpSupplier, ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id)
            .filter(ErpPurchaseOrder.purchase_order_id == purchase_order_id)
            .first()
        )
        return _row_to_dict(row)
    finally:
        db.close()


def fetch_purchase_order_items(purchase_order_id):
    db = SessionLocal()
    try:
        rows = (
            db.query(
                ErpPurchaseOrderItem.purchase_order_id.label("purchase_order_id"),
                ErpPurchaseOrderItem.product_id.label("product_id"),
                ErpPurchaseOrderItem.storage_method.label("storage_method"),
                ErpPurchaseOrderItem.quantity.label("quantity"),
                ErpPurchaseOrderItem.purchase_price.label("purchase_price"),
                ErpPurchaseOrderItem.total_amount.label("total_amount"),
                ErpPurchaseOrderItem.defective.label("defective"),
                ErpPurchaseOrderItem.final_amount.label("final_amount"),
                ErpPurchaseOrderItem.memo.label("memo"),
                ErpPurchaseOrderItem.last_update.label("last_update"),
                OpdProduct.weight.label("weight"),
                OpdProduct.quantity.label("product_quantity"),
                OpdProductDetail.product_name.label("product_name"),
                OpdProductDetail.type.label("product_type"),
                OpdProductDetail.brand.label("brand"),
            )
            .outerjoin(OpdProduct, ErpPurchaseOrderItem.product_id == OpdProduct.product_id)
            .outerjoin(OpdProductDetail, OpdProduct.product_detail_id == OpdProductDetail.product_detail_id)
            .filter(ErpPurchaseOrderItem.purchase_order_id == purchase_order_id)
            .order_by(ErpPurchaseOrderItem.product_id.asc())
            .all()
        )
        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()
