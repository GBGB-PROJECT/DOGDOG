# =========================================================
# 🔥 불량현황 API
# - ERP.inbound + ERP.inbound_status JOIN
# - ERP.purchase_order_item.defective 기준 불량수량/불량금액 조회
# - 생산관리 메인 대시보드의 불량 내역 카드와 이어지는 상세 조회 API
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .defective_service import count_defectives, fetch_defectives
from .defective_schema import ErpProductionDefectiveListResponse


router = APIRouter(
    prefix="/erp/production/defective",
    tags=["production"],
)


SEARCH_TYPE_LABELS = {
    "inbound_id": "입고ID",
    "product_no": "상품번",  # 🔥 수정: 상품번과 상품명을 검색조건에서 분리
    "product_name": "상품명",  # 🔥 수정: 상품번과 상품명을 검색조건에서 분리
    "supplier_name": "거래처명",
    "inbound_status": "입고상태",
    "employee_id": "담당자ID",
}


DATE_FILTER_TYPE_LABELS = {
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


def _format_weight(value):
    if value in [None, ""]:
        return ""

    try:
        weight = int(float(value))
    except Exception:
        return str(value)

    if weight <= 0:
        return ""

    return f"{weight:,}g"


def _build_product_no(product_detail_id, product_id):
    product_detail_id = str(product_detail_id or "").strip()
    product_id = str(product_id or "").strip()

    if product_detail_id and product_id:
        return f"{product_detail_id}-{product_id}"

    return product_detail_id or product_id


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
                "inbound_status": row.get("inbound_status", ""),
                "product_id": row.get("product_id", ""),
                "product_detail_id": row.get("product_detail_id", ""),
                "product_no": _build_product_no(row.get("product_detail_id", ""), row.get("product_id", "")),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "weight": row.get("weight", ""),
                "weight_text": _format_weight(row.get("weight", "")),
                "defective": row.get("defective", ""),
                "purchase_price": row.get("purchase_price", ""),
                "defective_amount": row.get("defective_amount", ""),
                "inbound_scheduled_date": _format_date(row.get("inbound_scheduled_date", "")),
                "inbound_start": _format_datetime(row.get("inbound_start", "")),
                "inbound_complete": _format_date(row.get("inbound_complete", "")),
                "employee_id": row.get("employee_id", ""),
                "last_update": _format_datetime(row.get("last_update", "")),
            }
        )

    return rows


@router.get(
    "",
    summary="불량현황조회",
    description=(
        "생산관리 > 불량현황조회 화면에서 사용하는 상품별 불량 현황 조회 API입니다. "
        "ERP.inbound, ERP.inbound_status, ERP.purchase_order, ERP.purchase_order_item, "
        "OPD.product, OPD.product_detail을 JOIN하여 불량수량과 불량손실액을 반환합니다."
    ),
    response_model=ErpProductionDefectiveListResponse,
)
def get_defective_list(
    search_type: Literal[
        "inbound_id",
        "product_no",
        "product_name",
        "supplier_name",
        "inbound_status",
        "employee_id",
    ] = Query(
        default="inbound_id",
        description="검색 조건. product_no=상품번, product_name=상품명/브랜드/중량 검색",
        examples=["product_no"],
    ),
    date_filter_type: Literal[
        "inbound_scheduled_date",
        "inbound_start",
        "inbound_complete",
    ] = Query(
        default="inbound_complete",
        description="DatePicker 기간 검색 기준. 불량현황조회 화면 기본값은 테이블에 보이는 입고완료일입니다.",
        examples=["inbound_complete"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["닭고기"],
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
        description="조회 시작일. date_filter_type 기준 컬럼으로 기간을 필터링합니다.",
        examples=["2026-04-01"],
    ),
    end_date: date | None = Query(
        default=None,
        description="조회 종료일. date_filter_type 기준 컬럼으로 기간을 필터링합니다.",
        examples=["2026-04-30"],
    ),
):
    try:
        clean_search_type = (search_type or "inbound_id").strip()
        clean_date_filter_type = (date_filter_type or "inbound_complete").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_defectives(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
            date_filter_type=clean_date_filter_type,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_defectives(
            search_type=clean_search_type,
            keyword=clean_keyword,
            limit=size,
            offset=offset,
            start_date=start_date,
            end_date=end_date,
            date_filter_type=clean_date_filter_type,
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
                        "date_filter_type": clean_date_filter_type,
                        "date_filter_type_label": DATE_FILTER_TYPE_LABELS.get(clean_date_filter_type, clean_date_filter_type),
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }

        return {
            "success": True,
            "message": "불량현황조회에 성공했습니다.",
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
                "error_code": "PRODUCTION_DEFECTIVE_LIST_FAILED",
                "message": f"불량현황조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )
