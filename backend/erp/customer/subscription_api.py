# =========================================================
# 🔥 고객 구독 관리 API
# =========================================================

from math import ceil
from typing import Literal
from datetime import date  # 🔥 추가: Swagger UI에서 날짜 선택 형식으로 표시하기 위한 date 타입

from fastapi import APIRouter, HTTPException, Query

from .subscription_service import (
    count_customer_subscriptions,
    fetch_customer_subscriptions,
)


router = APIRouter(
    prefix="/erp/customer/subscription",
    tags=["customer"],
)


SEARCH_TYPE_LABELS = {
    "subs_id": "구독ID",
    "customer_id": "고객ID",
    "subs_plan_id": "구독플랜ID",
    "is_auto_delivery": "자동배송여부",
    "is_subs_status": "구독상태",
    "subs_day": "배송신청요일",
    "delivery_cycle": "배송주기",
    "subs_sale": "구독 회원 할인율",
    "address": "배송지",
    "name": "이름",
    "phone": "전화번호",
    "subs_date": "구독시작일",
}


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "subs_id": row.get("subs_id", ""),
                "customer_id": row.get("customer_id", ""),
                "subs_date": row.get("subs_date", ""),
                "subs_plan_id": row.get("subs_plan_id", ""),
                "is_auto_delivery": row.get("is_auto_delivery", ""),
                "is_subs_status": row.get("is_subs_status", ""),
                "subs_day": row.get("subs_day", ""),
                "delivery_cycle": row.get("delivery_cycle", ""),
                "subs_sale": row.get("subs_sale", ""),
                "address": row.get("address", ""),
                "name": row.get("name", ""),
                "phone": row.get("phone", ""),
            }
        )

    return rows


@router.get(
    "",
    summary="고객 구독 관리 목록 조회",
    description=(
        "고객 구독 관리 화면에서 사용하는 목록 조회 API입니다. "
        "OPD.subs, OPD.subs_plan, OPD.subs_detail을 JOIN하여 구독 목록을 반환합니다."
    ),
)
def get_customer_subscription_list(
    search_type: Literal[
        "subs_id",
        "customer_id",
        "subs_plan_id",
        "is_auto_delivery",
        "is_subs_status",
        "subs_day",
        "delivery_cycle",
        "subs_sale",
        "address",
        "name",
        "phone",
        "subs_date",
    ] = Query(
        default="subs_id",
        description="검색 조건",
        examples=["subs_id"],
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
        description="구독시작일 시작일",
        examples=["2026-04-01"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
    end_date: date | None = Query(
        default=None,
        description="구독시작일 종료일",
        examples=["2026-04-30"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
):
    try:
        clean_search_type = (search_type or "subs_id").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_customer_subscriptions(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_customer_subscriptions(
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
                            clean_search_type,
                            clean_search_type,
                        ),
                        "keyword": clean_keyword,
                        "start_date": start_date,
                        "end_date": end_date,
                    },
                },
            }

        return {
            "success": True,
            "message": "고객 구독 목록 조회에 성공했습니다.",
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
                        clean_search_type,
                        clean_search_type,
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
                "error_code": "CUSTOMER_SUBSCRIPTION_LIST_FAILED",
                "message": f"고객 구독 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )