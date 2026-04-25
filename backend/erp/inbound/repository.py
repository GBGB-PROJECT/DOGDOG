# =========================================================
# 🔥 생산입고 Repository
# - ERP.inbound + ERP.inbound_status JOIN
# - 입고 상태 ID를 숫자로 노출하지 않고 inbound_status.status 문자로 반환
# - 발주/거래처 정보는 입고 현황에서 같이 보기 좋도록 purchase_order/supplier까지 LEFT JOIN
# - 검색어, 날짜 범위, 50개 단위 페이지네이션 처리
# =========================================================

import datetime

from sqlalchemy import cast, func, or_
from sqlalchemy.types import String

from db.db import SessionLocal
from db.models import ErpInbound, ErpInboundStatus, ErpPurchaseOrder, ErpSupplier
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
# - ID 검색에서 0 같은 숫자를 LIKE로만 처리하면 의도치 않은 데이터가 섞일 수 있음
# - 숫자만 입력된 경우 정확히 int 비교
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
# 🔥 생산입고 기본 JOIN 쿼리
# =========================================================
def _base_query(db):
    return (
        db.query(
            ErpInbound.inbound_id.label("inbound_id"),
            ErpInbound.purchase_order_id.label("purchase_order_id"),
            ErpPurchaseOrder.supplier_id.label("supplier_id"),
            ErpSupplier.supplier_name.label("supplier_name"),
            ErpInboundStatus.status.label("inbound_status"),  # 🔥 숫자 ID 대신 상태명 반환
            ErpInbound.inbound_start.label("inbound_start"),
            ErpInbound.inbound_complete.label("inbound_complete"),
            ErpInbound.employee_id.label("employee_id"),
            ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
            ErpInbound.last_update.label("last_update"),
        )
        .outerjoin(
            ErpInboundStatus,
            ErpInbound.inbound_status_id == ErpInboundStatus.inbound_status_id,
        )
        .outerjoin(
            ErpPurchaseOrder,
            ErpInbound.purchase_order_id == ErpPurchaseOrder.purchase_order_id,
        )
        .outerjoin(
            ErpSupplier,
            ErpPurchaseOrder.supplier_id == ErpSupplier.supplier_id,
        )
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
        )
    )


# =========================================================
# 🔥 날짜 범위 처리
# - 기본 기준: 입고 시작일(inbound_start)
# - search_type이 입고완료일/입고예정일이면 해당 컬럼 기준으로 날짜 필터 적용
# =========================================================
def _apply_date_filter(query, search_type="inbound_id", start_date=None, end_date=None):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if not start_dt and not end_dt:
        return query

    if search_type == "inbound_complete":
        target_column = ErpInbound.inbound_complete
    elif search_type == "inbound_scheduled_date":
        target_column = ErpPurchaseOrder.inbound_scheduled_date
    else:
        target_column = ErpInbound.inbound_start

    if start_dt:
        query = query.filter(func.date(target_column) >= start_dt.date())

    if end_dt:
        query = query.filter(func.date(target_column) <= end_dt.date())

    return query


# =========================================================
# 🔥 생산입고 총 건수
# =========================================================
def count_inbounds(
    search_type="inbound_id",
    keyword="",
    start_date=None,
    end_date=None,
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type=search_type, keyword=keyword)
        query = _apply_date_filter(
            query,
            search_type=search_type,
            start_date=start_date,
            end_date=end_date,
        )
        return query.count()
    finally:
        db.close()


# =========================================================
# 🔥 생산입고 목록 조회
# =========================================================
def fetch_inbounds(
    search_type="inbound_id",
    keyword="",
    limit=50,
    offset=0,
    start_date=None,
    end_date=None,
):
    db = SessionLocal()
    try:
        query = _base_query(db)
        query = _apply_filter(query, search_type=search_type, keyword=keyword)
        query = _apply_date_filter(
            query,
            search_type=search_type,
            start_date=start_date,
            end_date=end_date,
        )

        rows = (
            query.order_by(
                ErpInbound.inbound_id.desc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()
