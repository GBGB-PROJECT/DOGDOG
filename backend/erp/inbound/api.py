# =========================================================
# 🔥 생산입고 API
# - ERP.inbound + ERP.inbound_status JOIN 목록 조회
# - 입고상태는 inbound_status_id 숫자가 아니라 inbound_status.status 문자로 응답
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .service import count_inbounds, fetch_inbounds


router = APIRouter(
    prefix="/erp/inbound",
    tags=["inbound"],
)


SEARCH_TYPE_LABELS = {
    "inbound_id": "입고ID",
    "purchase_order_id": "발주ID",
    "supplier_id": "거래처ID",
    "supplier_name": "거래처명",
    "inbound_status": "입고상태",
    "employee_id": "담당자ID",
    "inbound_scheduled_date": "입고예정일",
    "inbound_start": "입고시작일",
    "inbound_complete": "입고완료일",
}


def _format_datetime(value):
    if not value:
        return ""
    return str(value)[:19]


def _format_date(value):
    if not value:
        return ""
    return str(value)[:10]


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "inbound_id": row.get("inbound_id", ""),
                "purchase_order_id": row.get("purchase_order_id", ""),
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "inbound_status": row.get("inbound_status", ""),  # 🔥 상태명 문자
                "inbound_scheduled_date": _format_date(row.get("inbound_scheduled_date", "")),
                "inbound_start": _format_datetime(row.get("inbound_start", "")),
                "inbound_complete": _format_datetime(row.get("inbound_complete", "")),
                "employee_id": row.get("employee_id", ""),
                "last_update": _format_datetime(row.get("last_update", "")),
            }
        )

    return rows


@router.get(
    "",
    summary="생산입고 현황 목록 조회",
    description=(
        "생산관리 > 생산입고 화면에서 사용하는 입고 현황 조회 API입니다. "
        "ERP.inbound와 ERP.inbound_status를 JOIN하여 입고상태 ID가 아닌 상태명을 반환합니다."
    ),
)
def get_inbound_list(
    search_type: Literal[
        "inbound_id",
        "purchase_order_id",
        "supplier_id",
        "supplier_name",
        "inbound_status",
        "employee_id",
        "inbound_scheduled_date",
        "inbound_start",
        "inbound_complete",
    ] = Query(
        default="inbound_id",
        description="검색 조건",
        examples=["inbound_id"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["1"],
    ),
    page: int = Query(
        default=1,
        ge=1,
        description="페이지 번호",
        examples=[1],
    ),
    size: int = Query(
        default=50,
        ge=1,
        le=100,
        description="페이지당 조회 건수",
        examples=[50],
    ),
    start_date: date | None = Query(
        default=None,
        description="조회 시작일. 기본은 입고시작일 기준이며, 검색조건이 입고완료일/입고예정일이면 해당 날짜 기준입니다.",
        examples=["2026-04-01"],
    ),
    end_date: date | None = Query(
        default=None,
        description="조회 종료일. 기본은 입고시작일 기준이며, 검색조건이 입고완료일/입고예정일이면 해당 날짜 기준입니다.",
        examples=["2026-04-30"],
    ),
):
    try:
        clean_search_type = (search_type or "inbound_id").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_inbounds(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_inbounds(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
        )

        result_items = build_response_rows(items, page, size)

        if total_count == 0:
            return {
                "success": True,
                "message": "일치하는 정보가 없습니다.",
                "data": {
                    "items": [],
                    "pagination": {
                        "page": 1,
                        "size": size,
                        "total_count": 0,
                        "total_pages": 1,
                    },
                    "search": {
                        "search_type": clean_search_type,
                        "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }

        return {
            "success": True,
            "message": "생산입고 목록 조회에 성공했습니다.",
            "data": {
                "items": result_items,
                "pagination": {
                    "page": page,
                    "size": size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                },
                "search": {
                    "search_type": clean_search_type,
                    "search_type_label": SEARCH_TYPE_LABELS.get(clean_search_type, clean_search_type),
                    "keyword": clean_keyword,
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
                "error_code": "INBOUND_LIST_FAILED",
                "message": f"생산입고 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
