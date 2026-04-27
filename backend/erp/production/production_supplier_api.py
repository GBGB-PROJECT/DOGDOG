# =========================================================
# 🔥 거래처 관리 API
# - ERP.supplier 기준 거래처 목록 조회 / 등록
# - 생산관리 > 거래처 관리 화면용 API
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .production_supplier_service import count_suppliers, fetch_suppliers
from .production_supplier_schema import ErpProductionSupplierListResponse

router = APIRouter(
    prefix="/erp/production/supplier",
    tags=["production"],
)

SEARCH_TYPE_LABELS = {
    "supplier_id": "거래처ID",
    "supplier_name": "거래처명",
    "brn": "사업자번호",
    "is_contact_status": "연락상태",
    "sup_manager": "담당자명",
    "phone": "전화번호",
}


def _format_contact_status(value):
    if value is True:
        return "활성"
    if value is False:
        return "비활성"

    lowered = str(value).strip().lower()
    if lowered in {"true", "1", "y", "yes", "가능", "활성"}:
        return "활성"
    if lowered in {"false", "0", "n", "no", "불가", "비활성"}:
        return "비활성"

    return str(value or "")


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "brn": row.get("brn", ""),
                "is_contact_status": _format_contact_status(row.get("is_contact_status", "")),
                "designated_payment_date": row.get("designated_payment_date", ""),
                "scheduled_payment_date": row.get("scheduled_payment_date", ""),
                "employee_id": row.get("employee_id", ""),
                "memo": row.get("memo", ""),
                "sup_manager": row.get("sup_manager", ""),
                "phone": row.get("phone", ""),
                "last_update": row.get("last_update", ""),
            }
        )

    return rows


@router.get(
    "",
    summary="거래처 관리 목록 조회",
    description=(
        "생산관리 > 거래처 관리 화면에서 사용하는 목록 조회 API입니다. "
        "ERP.supplier 테이블 기준으로 검색 조건, 검색어, 최종수정일 날짜 범위, 페이지 정보를 받아 거래처 목록을 반환합니다."
    ),
    response_model=ErpProductionSupplierListResponse,  # 🔥 ERP 조회 응답 Schema 연결
)
def get_suppliers(
    search_type: Literal[
        "supplier_id",
        "supplier_name",
        "brn",
        "is_contact_status",
        "sup_manager",
        "phone",
    ] = Query(default="supplier_name", description="검색 조건", examples=["supplier_name"]),
    keyword: str = Query(default="", description="검색어", examples=["하림"]),
    page: int = Query(default=1, ge=1, description="페이지 번호", examples=[1]),
    size: int = Query(default=50, ge=1, le=100, description="페이지당 조회 건수", examples=[50]),
    start_date: date | None = Query(default=None, description="최종수정일 시작일", examples=["2026-04-01"]),
    end_date: date | None = Query(default=None, description="최종수정일 종료일", examples=["2026-04-30"]),
):
    try:
        clean_search_type = (search_type or "supplier_name").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_suppliers(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )
        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_suppliers(
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
                    "pagination": {"page": 1, "size": size, "total_count": 0, "total_pages": 1},
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
            "message": "거래처 목록 조회에 성공했습니다.",
            "data": {
                "items": result_items,
                "pagination": {"page": page, "size": size, "total_count": total_count, "total_pages": total_pages},
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
                "error_code": "SUPPLIER_LIST_FAILED",
                "message": f"거래처 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
