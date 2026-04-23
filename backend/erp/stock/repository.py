from sqlalchemy import cast, func
from sqlalchemy.types import String

from backend.db.db import SessionLocal
from backend.db.models import ErpStock
from backend.erp.common.query_utils import model_to_dict, like_keyword, parse_date


# =========================================================
# ☑️ 재고관리 Repository
# - ERP.stock ORM 모델 기반 조회
# - product_id / inbound_id / 재고 수량 / 유통기한 검색 처리
# - expiration_date 또는 last_update 기준 기간 필터 처리
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


def _get_date_column(date_field: str):
    if date_field == "expiration_date":
        return ErpStock.expiration_date
    return ErpStock.last_update


def _apply_stock_filter(query, search_type: str, keyword: str, start_date=None, end_date=None, date_field="last_update"):
    clean = (keyword or "").strip()

    if clean:
        if search_type == "product_id":
            query = query.filter(cast(ErpStock.product_id, String).like(like_keyword(clean)))

        elif search_type == "inbound_id":
            query = query.filter(cast(ErpStock.inbound_id, String).like(like_keyword(clean)))

        elif search_type == "save_stock":
            query = query.filter(cast(ErpStock.save_stock, String).like(like_keyword(clean)))

        elif search_type == "sale_stock":
            query = query.filter(cast(ErpStock.sale_stock, String).like(like_keyword(clean)))

        elif search_type == "scrap_stock":
            query = query.filter(cast(ErpStock.scrap_stock, String).like(like_keyword(clean)))

        elif search_type == "stock_available":
            query = query.filter(cast(ErpStock.stock_available, String).like(like_keyword(clean)))

        elif search_type == "expiration_date":
            query = query.filter(cast(ErpStock.expiration_date, String).like(like_keyword(clean)))

        elif search_type == "last_update":
            query = query.filter(cast(ErpStock.last_update, String).like(like_keyword(clean)))

    parsed_start = parse_date(start_date)
    parsed_end = parse_date(end_date)
    target_column = _get_date_column(date_field)

    if parsed_start:
        query = query.filter(func.date(target_column) >= parsed_start)

    if parsed_end:
        query = query.filter(func.date(target_column) <= parsed_end)

    return query


def count_stocks(search_type="product_id", keyword="", start_date=None, end_date=None, date_field="last_update"):
    db = SessionLocal()
    try:
        query = db.query(ErpStock)
        query = _apply_stock_filter(query, search_type, keyword, start_date, end_date, date_field)
        return query.count()
    finally:
        db.close()


def fetch_stocks(search_type="product_id", keyword="", limit=50, offset=0, start_date=None, end_date=None, date_field="last_update"):
    db = SessionLocal()
    try:
        query = db.query(ErpStock)
        query = _apply_stock_filter(query, search_type, keyword, start_date, end_date, date_field)
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
