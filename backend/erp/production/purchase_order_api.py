# =========================================================
# 🔥 발주관리 API
# - 생산관리 > 발주 관리 화면용 실제 HTTP API
# - Flet 화면은 backend service/repository를 직접 import하지 않고 이 API를 호출하는 방향으로 전환
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .purchase_order_service import (
    count_purchase_orders,
    fetch_purchase_orders,
    fetch_purchase_order_detail,
    fetch_purchase_order_items,
)
from .purchase_order_schema import (
    ErpProductionPurchaseOrderListResponse,
    ErpProductionPurchaseOrderDetailResponse,
    ErpProductionPurchaseOrderItemsResponse,
)


router = APIRouter(
    prefix="/erp/production/purchase-order",
    tags=["production"],
)


SEARCH_TYPE_LABELS = {
    "purchase_order_id": "발주ID",
    "supplier_id": "거래처ID",
    "supplier_name": "거래처명",
    "pay_status": "결제상태",
    "is_purchase_order_cancel": "발주상태",
    "employee_id": "담당자ID",
    "product_id": "상품ID",
}

DATE_TYPE_LABELS = {
    "contract_date": "계약일자",
    "inbound_scheduled_date": "입고예정일",
}


def _format_date(value):
    if not value:
        return ""
    return str(value)[:10]


def _format_datetime(value):
    if not value:
        return ""
    return str(value)[:19]


def _format_number(value):
    if value in (None, ""):
        return ""
    try:
        return f"{int(value):,}"
    except Exception:
        return str(value)


def _normalize_pay_status(value):
    status = str(value or "").strip()
    if status == "completed":
        return "결제완료"
    if status == "scheduled":
        return "결제예정"
    return status


def _normalize_cancel_text(value):
    return "취소" if value else "정상"


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "purchase_order_id": row.get("purchase_order_id", ""),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "contract_date": _format_date(row.get("contract_date", "")),
                "inbound_scheduled_date": _format_date(row.get("inbound_scheduled_date", "")),
                "pay_status": _normalize_pay_status(row.get("pay_status", "")),
                "adjustment_date": _format_datetime(row.get("adjustment_date", "")),
                "is_purchase_order_cancel": _normalize_cancel_text(row.get("is_purchase_order_cancel")),
                "employee_id": row.get("employee_id", ""),
                "order_form_file_path": row.get("order_form_file_path", ""),
                "item_count": row.get("item_count", ""),
                "final_amount_sum": _format_number(row.get("final_amount_sum", "")),
                "last_update": _format_datetime(row.get("last_update", "")),
            }
        )
    return rows


@router.get(
    "",
    summary="발주 관리 목록 조회",
    description=(
        "생산관리 > 발주 관리 화면에서 사용하는 목록 조회 API입니다. "
        "ERP.purchase_order, ERP.purchase_order_item, ERP.supplier를 기준으로 "
        "검색 조건, 날짜 조건, 페이지 정보를 받아 발주 목록을 반환합니다."
    ),
    response_model=ErpProductionPurchaseOrderListResponse,
)
def get_purchase_orders(
    search_type: Literal[
        "purchase_order_id",
        "supplier_id",
        "supplier_name",
        "pay_status",
        "is_purchase_order_cancel",
        "employee_id",
        "product_id",
    ] = Query(default="purchase_order_id", description="검색 조건", examples=["purchase_order_id"]),
    keyword: str = Query(default="", description="검색어", examples=["368"]),
    date_type: Literal["contract_date", "inbound_scheduled_date"] = Query(
        default="contract_date",
        description="날짜 조건",
        examples=["contract_date"],
    ),
    page: int = Query(default=1, ge=1, description="페이지 번호", examples=[1]),
    size: int = Query(default=50, ge=1, le=100, description="페이지당 조회 건수", examples=[50]),
    start_date: date | None = Query(default=None, description="조회 시작일", examples=["2026-05-01"]),
    end_date: date | None = Query(default=None, description="조회 종료일", examples=["2026-05-31"]),
):
    try:
        clean_search_type = (search_type or "purchase_order_id").strip()
        clean_keyword = (keyword or "").strip()
        clean_date_type = (date_type or "contract_date").strip()

        total_count = count_purchase_orders(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
            date_type=clean_date_type,
        )
        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_purchase_orders(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            date_type=clean_date_type,
        )

        return {
            "success": True,
            "message": "일치하는 정보가 없습니다." if total_count == 0 else "발주 목록 조회에 성공했습니다.",
            "data": {
                "items": build_response_rows(items, page, size),
                "pagination": {
                    "page": 1 if total_count == 0 else page,
                    "size": size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                },
                "search": {
                    "search_type": clean_search_type,
                    "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                    "keyword": clean_keyword,
                    "date_type": clean_date_type,
                    "date_type_label": DATE_TYPE_LABELS.get(clean_date_type, clean_date_type),
                    "start_date": start_date,
                    "end_date": end_date,
                },
            },
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "PURCHASE_ORDER_LIST_FAILED",
                "message": f"발주 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )


@router.get(
    "/{purchase_order_id}",
    summary="발주 상세 조회",
    response_model=ErpProductionPurchaseOrderDetailResponse,
)
def get_purchase_order_detail(purchase_order_id: int):
    try:
        data = fetch_purchase_order_detail(purchase_order_id)
        if not data:
            return {"success": True, "message": "일치하는 발주 정보가 없습니다.", "data": None}
        return {"success": True, "message": "발주 상세 조회에 성공했습니다.", "data": data}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "PURCHASE_ORDER_DETAIL_FAILED",
                "message": f"발주 상세 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )


@router.get(
    "/{purchase_order_id}/items",
    summary="발주 품목 목록 조회",
    response_model=ErpProductionPurchaseOrderItemsResponse,
)
def get_purchase_order_items(purchase_order_id: int):
    try:
        items = fetch_purchase_order_items(purchase_order_id)
        return {"success": True, "message": "발주 품목 목록 조회에 성공했습니다.", "data": items}
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_code": "PURCHASE_ORDER_ITEMS_FAILED",
                "message": f"발주 품목 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
