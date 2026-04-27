from math import ceil
from typing import Literal
from datetime import date  # 🔥 추가: Swagger UI에서 날짜 선택 형식으로 표시하기 위한 date 타입

from fastapi import APIRouter, HTTPException, Query

from .customer_info_service import count_customers, fetch_customers, create_customer

router = APIRouter(
    prefix="/erp/customer/info",  # 🔥 수정: 고객 정보 관리 전용 API 경로로 변경
    tags=["customer"],  # 🔥 수정: Swagger에서 고객 정보 관리 API로 분리 표시
)

SEARCH_TYPE_LABELS = {
    "customer_id": "고객ID",
    "email": "이메일",
    "oauth_type": "OAuth유형",
    "nickname": "닉네임",
    "phone": "전화번호",
    "is_subscribed": "구독여부",
    "subs_count": "구독횟수",
    "active": "상태",
    "create_date": "가입일",
}


def _format_bool_yn(value):
    return "Y" if value else "N"


def _format_active(value):
    return "활성" if value else "비활성"


def build_response_rows(items: list, page: int, size: int):
    start_no = ((page - 1) * size) + 1
    rows = []

    for index, row in enumerate(items, start=start_no):
        rows.append(
            {
                "no": index,
                "customer_id": row.get("customer_id", ""),
                "email": row.get("email", ""),
                "oauth_type": row.get("oauth_type", ""),
                "nickname": row.get("nickname", ""),
                "phone": row.get("phone", ""),
                "is_subscribed": _format_bool_yn(row.get("is_subscribed", False)),
                "subs_count": row.get("subs_count", ""),
                "active": _format_active(row.get("active", False)),
                "create_date": row.get("create_date", ""),
            }
        )

    return rows


@router.get(
    "",
    summary="고객 정보 관리 목록 조회",
    description=(
        "고객 정보 관리 화면에서 사용하는 목록 조회 API입니다. "
        "검색 조건, 검색어, 날짜 범위, 페이지 정보를 받아 고객 목록을 반환합니다."
    ),
)
def get_customer_list(
    search_type: Literal[
        "customer_id",
        "email",
        "oauth_type",
        "nickname",
        "phone",
        "is_subscribed",
        "subs_count",
        "active",
        "create_date",
    ] = Query(
        default="customer_id",
        description="검색 조건",
        examples=["customer_id"],
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
        description="가입일 시작일",
        examples=["2026-04-01"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
    end_date: date | None = Query(
        default=None,
        description="가입일 종료일",
        examples=["2026-04-30"],
    ),  # 🔥 수정: str → date, Swagger UI 날짜 선택 형식
):
    try:
        clean_search_type = (search_type or "customer_id").strip()
        clean_keyword = (keyword or "").strip()

        total_count = count_customers(
            search_type=clean_search_type,
            keyword=clean_keyword,
            start_date=start_date,
            end_date=end_date,
        )

        total_pages = max(1, ceil(total_count / size))
        offset = (page - 1) * size

        items = fetch_customers(
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
            "message": "고객 목록 조회에 성공했습니다.",
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
                "error_code": "INTERNAL_ERROR",
                "message": f"고객 목록 조회 중 서버 오류가 발생했습니다. {exc}",
            },
        )


@router.post(
    "",
    summary="고객 등록",
    description="고객관리 화면의 등록 모달에서 사용하는 고객 등록 API입니다.",
)
def post_customer_create(body: dict):
    try:
        created = create_customer(body)

        return {
            "success": True,
            "message": "고객 등록에 성공했습니다.",
            "data": {
                "customer_id": created.get("customer_id", ""),
                "email": created.get("email", ""),
                "oauth_type": created.get("oauth_type", ""),
                "nickname": created.get("nickname", ""),
                "phone": created.get("phone", ""),
                "is_subscribed": _format_bool_yn(created.get("is_subscribed", False)),
                "subs_count": created.get("subs_count", ""),
                "active": _format_active(created.get("active", False)),
                "create_date": created.get("create_date", ""),
            },
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_code": "CUSTOMER_CREATE_FAILED",
                "message": str(exc),
            },
        )