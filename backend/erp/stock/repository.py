from sqlalchemy import cast
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import ErpStock
from backend.erp.common.query_utils import model_to_dict, like_keyword


# =========================================================
# ☑️ 재고관리 Repository
# - ERP.stock ORM 모델 기반 조회
# - product_id / inbound_id / 재고 수량 / 유통기한 검색 처리
# - count + limit/offset 페이지네이션 처리
# =========================================================

STOCK_COLUMNS = [
    "product_id",
    "inbound_id",
    "save_stock",
    "sale_stock",
    "scrap_stock",
    "stock_available",
    "expiration_date",
    "last_update",
]


def _apply_stock_filter(query, search_type: str, keyword: str):
    clean = (keyword or "").strip()

    if not clean:
        return query

    if search_type == "product_id":
        return query.filter(cast(ErpStock.product_id, String).like(like_keyword(clean)))

    if search_type == "inbound_id":
        return query.filter(cast(ErpStock.inbound_id, String).like(like_keyword(clean)))

    if search_type == "save_stock":
        return query.filter(cast(ErpStock.save_stock, String).like(like_keyword(clean)))

    if search_type == "sale_stock":
        return query.filter(cast(ErpStock.sale_stock, String).like(like_keyword(clean)))

    if search_type == "scrap_stock":
        return query.filter(cast(ErpStock.scrap_stock, String).like(like_keyword(clean)))

    if search_type == "stock_available":
        return query.filter(cast(ErpStock.stock_available, String).like(like_keyword(clean)))

    if search_type == "expiration_date":
        return query.filter(cast(ErpStock.expiration_date, String).like(like_keyword(clean)))

    if search_type == "last_update":
        return query.filter(cast(ErpStock.last_update, String).like(like_keyword(clean)))

    return query


def count_stocks(search_type="product_id", keyword=""):
    db = SessionLocal()
    try:
        query = db.query(ErpStock)
        query = _apply_stock_filter(query, search_type, keyword)
        return query.count()
    finally:
        db.close()


def fetch_stocks(search_type="product_id", keyword="", limit=50, offset=0):
    db = SessionLocal()
    try:
        query = db.query(ErpStock)
        query = _apply_stock_filter(query, search_type, keyword)
        rows = (
            query.order_by(
                ErpStock.product_id.asc(),
                ErpStock.inbound_id.asc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )
        return [model_to_dict(row, STOCK_COLUMNS) for row in rows]
    finally:
        db.close()
