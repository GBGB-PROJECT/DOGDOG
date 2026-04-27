# =========================================================
# 🔥 생산관리 메인 대시보드 Service
# - Repository의 raw DB 값을 Flet 화면에서 바로 쓰기 좋은 구조로 변환
# - 월 이동용 year/month 필터 지원
# =========================================================

from datetime import datetime, timedelta

from .dashboard_repository import (
    count_defective_rows,
    count_production_rows,
    fetch_dashboard_base_year_month,
    fetch_monthly_production_chart,
    fetch_recent_defective_rows,
    fetch_recent_production_rows,
    fetch_recent_purchase_cards,
)


# =========================================================
# 🔥 날짜 표시
# =========================================================
def _format_short_date(value):
    if not value:
        return ""

    clean = str(value)[:10]
    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return parsed.strftime("%y.%m.%d")
    except ValueError:
        return clean.replace("-", ".")


def _format_full_date(value):
    if not value:
        return "-"

    clean = str(value)[:10]
    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return parsed.strftime("%Y.%m.%d")
    except ValueError:
        return clean.replace("-", ".")


def _build_order_display_code(contract_date):
    """
    🔥 디자인 예시에 맞춘 발주 카드용 표시 코드
    - DB에 발주코드 컬럼이 따로 없으므로 발주일자 기준으로 화면용 코드 생성
    - 예: 2026-04-07 -> GAEBOB_260407
    """
    clean = str(contract_date or "")[:10]

    try:
        parsed = datetime.strptime(clean, "%Y-%m-%d")
        return f"GAEBOB_{parsed.strftime('%y%m%d')}"
    except ValueError:
        return "GAEBOB_ORDER"


# =========================================================
# 🔥 숫자 표시
# =========================================================
def _to_int(value, default=0):
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _format_count_text(value):
    return f"{_to_int(value):,}건"


def _format_quantity(value):
    return f"{_to_int(value):,} ea"


def _format_money_to_manwon(value):
    amount = _to_int(value)
    manwon = round(amount / 10000)
    return f"{manwon:,}만원"


# =========================================================
# 🔥 최근 생산/불량 박스 row 변환
# =========================================================
def _build_recent_production_screen_rows(rows):
    screen_rows = []

    for row in rows:
        screen_rows.append(
            [
                _format_short_date(row.get("dashboard_date") or row.get("inbound_complete")),
                "생산",
                row.get("product_name") or row.get("supplier_name") or "-",
                _format_quantity(row.get("save_stock")),
                _format_money_to_manwon(row.get("production_amount")),
            ]
        )

    return screen_rows


def _build_recent_defective_screen_rows(rows):
    screen_rows = []

    for row in rows:
        screen_rows.append(
            [
                _format_short_date(row.get("dashboard_date") or row.get("inbound_complete")),
                "불량",
                row.get("product_name") or row.get("supplier_name") or "-",
                _format_quantity(row.get("defective")),
                _format_money_to_manwon(row.get("defective_amount")),
            ]
        )

    return screen_rows


# =========================================================
# 🔥 월별 차트 데이터 변환
# - DB 금액은 원 단위
# - 화면 차트는 천원 단위로 표시
# =========================================================
def _build_chart_data(monthly_rows):
    month_map = {
        _to_int(row.get("month")): row
        for row in monthly_rows
        if _to_int(row.get("month")) > 0
    }

    chart_data = []

    for month in range(1, 13):
        row = month_map.get(month, {})
        production_amount = _to_int(row.get("production_amount"))
        defective_amount = _to_int(row.get("defective_amount"))

        chart_data.append(
            (
                f"{month}월",
                round(production_amount / 1000),
                round(defective_amount / 1000),
            )
        )

    return chart_data


# =========================================================
# 🔥 최근 발주 카드 변환
# - 디자인 예시 기준으로 발주서 단위 카드 표시
# - 상단: GAEBOB_YYMMDD
# - 본문: 발주일자 / 총발주량 / 입고예정일
# =========================================================
def _build_purchase_card_items(rows):
    items = []

    for row in rows:
        purchase_order_id = row.get("purchase_order_id", "")
        purchase_quantity_sum = _to_int(row.get("purchase_quantity_sum"), 0)
        order_display_code = _build_order_display_code(row.get("contract_date"))

        items.append(
            {
                # 🔥 카드 상단 표기
                "name": order_display_code,
                "order_display_code": order_display_code,

                # 🔥 상세 모달 조회용 실제 PK
                "purchase_order_id": purchase_order_id,

                # 🔥 버튼 문구
                "action_text": "상세내역",

                # 🔥 디자인 예시 기준 row
                "rows": [
                    ("발주일자", _format_full_date(row.get("contract_date"))),
                    ("총발주량", _format_quantity(purchase_quantity_sum)),
                    ("입고예정일", _format_full_date(row.get("inbound_scheduled_date"))),
                ],
            }
        )

    return items


# =========================================================
# 🔥 월 시작/끝 날짜
# - 생산 입고 화면 이동 시 해당 월 입고완료일 필터에 사용
# =========================================================
def _build_month_range(year: int, month: int):
    start = f"{year:04d}-{month:02d}-01"

    if month == 12:
        end = f"{year:04d}-12-31"
    else:
        end_dt = datetime(year, month + 1, 1) - timedelta(days=1)
        end = end_dt.strftime("%Y-%m-%d")

    return start, end


# =========================================================
# 🔥 생산관리 메인 대시보드 전체 조회
# =========================================================
def fetch_production_dashboard(year=None, month=None):
    base_year, base_month = fetch_dashboard_base_year_month()

    target_year = int(year or base_year)
    target_month = int(month or base_month)

    production_rows = fetch_recent_production_rows(
        limit=5,
        year=target_year,
        month=target_month,
    )

    defective_rows = fetch_recent_defective_rows(
        limit=5,
        year=target_year,
        month=target_month,
    )

    monthly_rows = fetch_monthly_production_chart(
        year=target_year,
    )

    purchase_card_rows = fetch_recent_purchase_cards(
        limit=5,
        year=target_year,
        month=target_month,
    )

    production_count = count_production_rows(
        year=target_year,
        month=target_month,
    )

    defective_count = count_defective_rows(
        year=target_year,
        month=target_month,
    )

    month_start, month_end = _build_month_range(target_year, target_month)

    status_box_data = [
        {
            "title": "생산 입고",
            "count_text": _format_count_text(production_count),
            "count": _to_int(production_count),
            "subtitle": "최근 생산 내역",
            "rows": _build_recent_production_screen_rows(production_rows),
        },
        {
            "title": "불량 내역",
            "count_text": _format_count_text(defective_count),
            "count": _to_int(defective_count),
            "subtitle": "최근 불량 내역",
            "rows": _build_recent_defective_screen_rows(defective_rows),
        },
    ]

    top_production_section_data = {
        "title": "최근 발주 내역",
        "items": _build_purchase_card_items(purchase_card_rows),
    }

    return {
        "current_year": target_year,
        "current_month": target_month,
        "current_month_text": f"{target_year}년 {target_month}월",
        "month_start": month_start,
        "month_end": month_end,
        "status_box_data": status_box_data,
        "chart_data": _build_chart_data(monthly_rows),
        "top_production_section_data": top_production_section_data,
    }


__all__ = ["fetch_production_dashboard"]