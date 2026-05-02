# =========================================================
# 🔥 고객 주문 관리 API
# =========================================================

from math import ceil
from typing import Literal
from datetime import date  # 🔥 추가: Swagger UI에서 날짜 선택 형식으로 표시하기 위한 date 타입

from fastapi import APIRouter, HTTPException, Query

from .order_service import count_customer_orders, fetch_customer_orders
from .order_schema import ErpCustomerOrderListResponse

router = APIRouter(
    prefix="/erp/customer/order",
    tags=["customer"],
)

SEARCH_TYPE_LABELS = {
    "order_number": "주문번호",
    "customer_id": "고객ID",
    "phone": "전화번호",
    "address": "배송지",
    "product": "상품",  # 🔥 상품ID/브랜드/상품명 통합 검색
}


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "order_number": row.get("order_number", ""),
                "order_date": row.get("order_date", ""),
                "sales_order_id": row.get("sales_order_id", ""),
                "customer_id": row.get("customer_id", ""),
                "recipient": row.get("recipient", ""),
                "phone": row.get("phone", ""),
                "address": row.get("address", ""),  # 🔥 추가: 배송지 응답 포함
                "product_id": row.get("product_id", ""),
                "product_detail_id": row.get("product_detail_id", ""),
                "product_brand": row.get("product_brand", ""),
                "product_name": row.get("product_name", ""),
                "product_weight": row.get("product_weight", ""),
                "product_unit_quantity": row.get("product_unit_quantity", ""),
                "quantity": row.get("quantity", ""),
                "retail_price": row.get("retail_price", ""),
                "total_amount": row.get("total_amount", ""),
                "payment_billing_id": row.get("payment_billing_id", ""),
            }
        )

    return rows


@router.get(
    "",
    summary="고객 주문 관리 목록 조회",
    description=(
        "고객 주문 관리 화면에서 사용하는 목록 조회 API입니다. "
        "검색 조건, 검색어, 주문일 날짜 범위, 페이지 정보를 받아 고객 주문 목록을 반환합니다."
    ),
    response_model=ErpCustomerOrderListResponse,  # 🔥 ERP 조회 응답 Schema 연결
)
def get_customer_orders(
    search_type: Literal[
        "order_number",
        "customer_id",
        "phone",
        "address",
        "product",  # 🔥 상품ID/브랜드/상품명 통합 검색
    ] = Query(
        default="order_number",
        description="검색 조건",
        examples=["order_number"],
    ),
    keyword: str = Query(
        default="",
        description="검색어",
        examples=["ORD"],
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
        description="주문일 시작일",
        examples=["2026-04-01"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
    end_date: date | None = Query(
        default=None,
        description="주문일 종료일",
        examples=["2026-04-30"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
):
    try:
        clean_search_type = (search_type or "order_number").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_customer_orders(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_customer_orders(
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
                        "search_type_label": SEARCH_TYPE_LABELS.get(
                            clean_search_type, clean_search_type
                        ),
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }

        return {
            "success": True,
            "message": "고객 주문 목록 조회에 성공했습니다.",
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
                    "search_type_label": SEARCH_TYPE_LABELS.get(
                        clean_search_type, clean_search_type
                    ),
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
                "error_code": "CUSTOMER_ORDER_LIST_FAILED",
                "message": f"고객 주문 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )