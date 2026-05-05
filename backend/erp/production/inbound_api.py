# =========================================================
# 🔥 생산입고 API
# - ERP.inbound + ERP.inbound_status JOIN 목록 조회
# - ERP.stock + ERP.purchase_order_item + OPD.product + OPD.product_detail JOIN 추가
# - 입고상태는 inbound_status_id 숫자가 아니라 inbound_status.status 문자로 응답
# - 생산관리 메인 카드에서 보이는 상품명/수량/금액과 이어지는 상품별 입고 현황 응답
# =========================================================

from math import ceil
from typing import Literal
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from .inbound_service import count_inbounds, fetch_inbounds
from .inbound_schema import ErpProductionInboundListResponse


router = APIRouter(
    prefix="/erp/production/inbound",
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
    "inbound_complete": "입고완료일",
    "expiration_date": "유통기한",
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
                "supplier_id": row.get("supplier_id", ""),
                "supplier_name": row.get("supplier_name", ""),
                "inbound_status": row.get("inbound_status", ""),  # 🔥 상태명 문자
                "product_id": row.get("product_id", ""),
                "product_detail_id": row.get("product_detail_id", ""),
                "product_no": _build_product_no(row.get("product_detail_id", ""), row.get("product_id", "")),
                "brand": row.get("brand", ""),
                "product_name": row.get("product_name", ""),
                "weight": row.get("weight", ""),
                "weight_text": _format_weight(row.get("weight", "")),
                "save_stock": row.get("save_stock", ""),
                "purchase_price": row.get("purchase_price", ""),
                "inbound_amount": row.get("inbound_amount", ""),
                "expiration_date": _format_date(row.get("expiration_date", "")),
                "inbound_scheduled_date": _format_date(row.get("inbound_scheduled_date", "")),
                "inbound_start": _format_datetime(row.get("inbound_start", "")),
                # 🔥 입고완료일은 시간 없이 날짜만 반환
                "inbound_complete": _format_date(row.get("inbound_complete", "")),
                "employee_id": row.get("employee_id", ""),
                "last_update": _format_datetime(row.get("last_update", "")),
            }
        )

    return rows


@router.get(
    "",
    summary="생산입고현황조회",
    description=(
        "생산관리 > 생산입고현황조회 화면에서 사용하는 상품별 입고 현황 조회 API입니다. "
        "ERP.inbound, ERP.inbound_status, ERP.stock, ERP.purchase_order_item, "
        "OPD.product, OPD.product_detail을 JOIN하여 입고상태명과 상품 정보를 함께 반환합니다."
    ),
    response_model=ErpProductionInboundListResponse,  # 🔥 ERP 조회 응답 Schema 연결
)
def get_inbound_list(
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
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["콤보"],
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
        description="조회 시작일. 기본은 입고시작일 기준이며, 검색조건이 입고완료일/입고예정일/유통기한이면 해당 날짜 기준입니다.",
        examples=["2026-04-01"],
    ),
    end_date: date | None = Query(
        default=None,
        description="조회 종료일. 기본은 입고시작일 기준이며, 검색조건이 입고완료일/입고예정일/유통기한이면 해당 날짜 기준입니다.",
        examples=["2026-04-30"],
    ),
    date_filter_type: Literal[
        "inbound_complete",
        "expiration_date",
    ] = Query(
        default="inbound_complete",
        description="날짜 범위를 적용할 기준 컬럼. 화면 DatePicker 기준: inbound_complete=입고완료일, expiration_date=유통기한.",
        examples=["inbound_complete"],
    ),
):
    try:
        clean_search_type = (search_type or "inbound_id").strip()
        clean_keyword = (keyword or "").strip()
        clean_date_filter_type = (date_filter_type or "inbound_start").strip()

        total_count = count_inbounds(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
            # 🔥 검색조건과 날짜 기준 분리
            date_filter_type=clean_date_filter_type,
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
            # 🔥 검색조건과 날짜 기준 분리
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
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                        "date_filter_type": clean_date_filter_type,
                        "date_filter_type_label": DATE_FILTER_TYPE_LABELS.get(clean_date_filter_type, clean_date_filter_type),
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
                    "date_filter_type": clean_date_filter_type,
                    "date_filter_type_label": DATE_FILTER_TYPE_LABELS.get(clean_date_filter_type, clean_date_filter_type),
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
