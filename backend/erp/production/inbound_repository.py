# =========================================================
# 🔥 생산입고 Repository
# - ERP.inbound + ERP.inbound_status JOIN
# - ERP.stock + ERP.purchase_order_item + OPD.product + OPD.product_detail JOIN 추가
# - 대시보드의 생산 입고 카드와 동일하게 상품명/입고수량/입고금액까지 조회
# - 입고 상태 ID를 숫자로 노출하지 않고 inbound_status.status 문자로 반환
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
    ErpStock,
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
# - 기존: inbound 문서 헤더 중심
# - 수정: stock 기준으로 상품별 입고 현황 조회
# =========================================================
def _base_query(db):
    # 🔥 입고금액 = 실제 입고수량(save_stock) * 발주 구매단가(purchase_price)
    inbound_amount_expr = func.coalesce(
        ErpStock.save_stock * ErpPurchaseOrderItem.purchase_price,
        0,
    )

    return (
        db.query(
            ErpInbound.inbound_id.label("inbound_id"),
            ErpPurchaseOrder.supplier_id.label("supplier_id"),
            ErpSupplier.supplier_name.label("supplier_name"),
            ErpInboundStatus.status.label("inbound_status"),  # 🔥 숫자 ID 대신 상태명 반환
            ErpStock.product_id.label("product_id"),
            OpdProduct.product_detail_id.label("product_detail_id"),  # 🔥 추가: 화면 상품번(product_detail_id-product_id) 구성용
            OpdProductDetail.brand.label("brand"),
            OpdProductDetail.product_name.label("product_name"),
            OpdProduct.weight.label("weight"),
            ErpStock.save_stock.label("save_stock"),
            ErpPurchaseOrderItem.purchase_price.label("purchase_price"),
            inbound_amount_expr.label("inbound_amount"),
            ErpStock.expiration_date.label("expiration_date"),
            ErpPurchaseOrder.inbound_scheduled_date.label("inbound_scheduled_date"),
            ErpInbound.inbound_start.label("inbound_start"),
            ErpInbound.inbound_complete.label("inbound_complete"),
            ErpInbound.employee_id.label("employee_id"),
            ErpInbound.last_update.label("last_update"),
        )
        # 🔥 상품 입고 현황이므로 stock을 기준 테이블로 사용
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
        # 🔥 취소된 발주건은 생산입고 현황에서 제외
        .filter(ErpPurchaseOrder.is_purchase_order_cancel.is_(False))
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

    if search_type in {"product_no", "product_id"}:
        return query.filter(
            or_(
                cast(ErpStock.product_id, String).like(like_keyword(clean)),
                cast(OpdProduct.product_detail_id, String).like(like_keyword(clean)),
                func.concat(cast(OpdProduct.product_detail_id, String), "-", cast(ErpStock.product_id, String)).like(like_keyword(clean)),
            )
        )

    if search_type in {"product_name", "brand"}:
        return query.filter(
            or_(
                OpdProductDetail.brand.ilike(like_keyword(clean)),
                OpdProductDetail.product_name.ilike(like_keyword(clean)),
                cast(OpdProduct.weight, String).like(like_keyword(clean)),
            )
        )

    # 🔥 호환용: 예전 product 통합 검색이 넘어와도 기존처럼 처리
    if search_type == "product":
        return query.filter(
            or_(
                cast(ErpStock.product_id, String).like(like_keyword(clean)),
                cast(OpdProduct.product_detail_id, String).like(like_keyword(clean)),
                func.concat(cast(OpdProduct.product_detail_id, String), "-", cast(ErpStock.product_id, String)).like(like_keyword(clean)),
                OpdProductDetail.brand.ilike(like_keyword(clean)),
                OpdProductDetail.product_name.ilike(like_keyword(clean)),
                cast(OpdProduct.weight, String).like(like_keyword(clean)),
            )
        )

    if search_type == "employee_id":
        if _is_int_text(clean):
            return query.filter(ErpInbound.employee_id == int(clean))
        return query.filter(cast(ErpInbound.employee_id, String).like(like_keyword(clean)))

    if search_type == "expiration_date":
        return query.filter(cast(ErpStock.expiration_date, String).like(like_keyword(clean)))

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
            cast(ErpStock.product_id, String).like(like_keyword(clean)),
            cast(OpdProduct.product_detail_id, String).like(like_keyword(clean)),  # 🔥 추가: 상품번 앞자리 검색
            func.concat(cast(OpdProduct.product_detail_id, String), "-", cast(ErpStock.product_id, String)).like(like_keyword(clean)),  # 🔥 추가: 57-135 형태 상품번 검색
            OpdProductDetail.brand.ilike(like_keyword(clean)),
            OpdProductDetail.product_name.ilike(like_keyword(clean)),
            cast(OpdProduct.weight, String).like(like_keyword(clean)),
        )
    )


# =========================================================
# 🔥 날짜 범위 처리
# - 검색조건(search_type)과 날짜 기준(date_filter_type)을 분리
# - 생산관리 68건 > 으로 들어온 경우 검색조건을 거래처명/상품명으로 바꿔도
#   날짜 범위는 계속 입고완료일(inbound_complete) 기준으로 유지되어야 함
# =========================================================
def _apply_date_filter(
    query,
    search_type="inbound_id",
    start_date=None,
    end_date=None,
    date_filter_type="inbound_start",
):
    start_dt = _normalize_start_datetime(start_date)
    end_dt = _normalize_end_datetime(end_date)

    if not start_dt and not end_dt:
        return query

    clean_date_filter_type = date_filter_type or "inbound_start"

    # 🔥 기존 호출 호환: date_filter_type이 없고 검색조건이 날짜형이면 그 검색조건을 날짜 기준으로 사용
    if clean_date_filter_type not in {
        "expiration_date",
        "inbound_scheduled_date",
        "inbound_start",
        "inbound_complete",
    }:
        clean_date_filter_type = search_type if search_type in {
            "expiration_date",
            "inbound_scheduled_date",
            "inbound_start",
            "inbound_complete",
        } else "inbound_start"

    if clean_date_filter_type == "inbound_complete":
        target_column = ErpInbound.inbound_complete
    elif clean_date_filter_type == "inbound_scheduled_date":
        target_column = ErpPurchaseOrder.inbound_scheduled_date
    elif clean_date_filter_type == "expiration_date":
        target_column = ErpStock.expiration_date
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
    date_filter_type="inbound_start",
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
            # 🔥 검색조건과 날짜 기준 분리
            date_filter_type=date_filter_type,
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
    date_filter_type="inbound_start",
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
            # 🔥 검색조건과 날짜 기준 분리
            date_filter_type=date_filter_type,
        )

        rows = (
            query.order_by(
                ErpInbound.inbound_complete.desc().nullslast(),
                ErpInbound.inbound_id.desc(),
                ErpStock.product_id.asc(),
            )
            .limit(limit)
            .offset(offset)
            .all()
        )

        return [_row_to_dict(row) for row in rows]
    finally:
        db.close()
