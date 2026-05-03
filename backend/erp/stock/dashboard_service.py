# =========================================================
# 🔥 재고 현황 대시보드 Service
# - Repository raw DB 값을 Flet 화면 구조로 변환
# - 월 이동용 year/month 필터 지원
# =========================================================

from datetime import datetime, timedelta

from .dashboard_repository import (
    count_inbound_rows,
    count_outbound_rows,
    count_expiring_stock_rows,
    fetch_monthly_stock_chart,
    fetch_month_total_stock_quantity,
    fetch_recent_inbound_rows,
    fetch_recent_outbound_rows,
    fetch_stock_dashboard_base_year_month,
    fetch_top_sales_stock_rows,
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


def _format_money_to_won(value):
    # 🔥 금액 표시 단위 수정
    # - 기존: 1만원 / 11만원
    # - 수정: 10,000원 / 110,000원
    amount = _to_int(value)
    return f"{amount:,}원"


# =========================================================
# 🔥 최근 입고/출고 박스 row 변환
# =========================================================
def _build_recent_inbound_screen_rows(rows):
    screen_rows = []

    for row in rows:
        screen_rows.append(
            [
                _format_short_date(row.get("dashboard_date") or row.get("inbound_complete")),
                "입고",
                row.get("product_name") or row.get("brand") or "-",
                _format_quantity(row.get("quantity")),
                _format_money_to_won(row.get("amount")),
            ]
        )

    return screen_rows


def _build_recent_outbound_screen_rows(rows):
    screen_rows = []

    for row in rows:
        screen_rows.append(
            [
                _format_short_date(row.get("order_date")),
                "출고",
                row.get("product_name") or row.get("brand") or "-",
                _format_quantity(row.get("quantity")),
                _format_money_to_won(row.get("amount")),
            ]
        )

    return screen_rows


# =========================================================
# 🔥 월별 차트 데이터 변환
# - DB 금액은 원 단위
# - 화면 차트는 K 단위로 표시
# - twin_chart.py는 값 자체를 K 라벨 체계로 보여주므로 여기서 /1000
# =========================================================
def _build_chart_data(monthly_data):
    inbound_map = {
        _to_int(row.get("month")): _to_int(row.get("inbound_amount"))
        for row in monthly_data.get("inbound_rows", [])
        if _to_int(row.get("month")) > 0
    }

    outbound_map = {
        _to_int(row.get("month")): _to_int(row.get("outbound_amount"))
        for row in monthly_data.get("outbound_rows", [])
        if _to_int(row.get("month")) > 0
    }

    chart_data = []

    for month in range(1, 13):
        inbound_amount = inbound_map.get(month, 0)
        outbound_amount = outbound_map.get(month, 0)

        chart_data.append(
            (
                f"{month}월",
                round(inbound_amount / 1000),
                round(outbound_amount / 1000),
            )
        )

    return chart_data


def _build_top_stock_items(rows):
    items = []

    for row in rows:
        product_name = row.get("product_name") or "상품명 없음"
        brand = row.get("brand") or ""
        sales_quantity = _to_int(row.get("sales_quantity"))
        current_stock = _to_int(row.get("current_stock"))

        # 🔥 대시보드용 보충 생산량 계산
        # - 기존 방식: 적정 재고량 - 현 재고량이라 현 재고가 많으면 전부 0이 됨
        # - 수정 방식: 현재 재고를 유지하면서 월 판매량 기반으로 추가 보충량을 산정
        # - 예상 발주량은 "부족분"이 아니라 "보충 권장량"처럼 보이게 만듦
        expected_order_quantity = max(
            sales_quantity * 2,
            round(current_stock * 0.05),
            10,
        )

        proper_stock = current_stock + expected_order_quantity

        display_name = product_name
        if brand:
            display_name = f"{brand} {product_name}"

        items.append(
            {
                "name": display_name,
                "action_text": "즉시 생산",
                "product_id": row.get("product_id"),

                # 🔥 추가: 생산지시서 자동 입력용 단가
                # - 구매단가: ERP.purchase_order_item.purchase_price
                # - 판매가: OPD.product.retail_price 또는 sales_order_item.retail_price
                "purchase_price": _to_int(row.get("purchase_price")),
                "retail_price": _to_int(row.get("retail_price")),

                "rows": [
                    ("적정 재고량", _format_quantity(proper_stock)),
                    ("현 재고량", _format_quantity(current_stock)),
                    ("예상 발주량", _format_quantity(expected_order_quantity)),
                ],
            }
        )

    return items


# =========================================================
# 🔥 월 시작/끝 날짜
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
# 🔥 재고 현황 대시보드 전체 조회
# =========================================================
def fetch_stock_dashboard(year=None, month=None):
    base_year, base_month = fetch_stock_dashboard_base_year_month()

    target_year = int(year or base_year)
    target_month = int(month or base_month)

    inbound_rows = fetch_recent_inbound_rows(
        limit=5,
        year=target_year,
        month=target_month,
    )

    # 🔥 유통기한 임박 재고: 오늘 기준 30일 이내 만료 예정 재고 행 개수
    expiring_stock_count = count_expiring_stock_rows(days=30)

    # 🔥 기존 월 입고분 현재고 값은 호환성을 위해 유지
    total_stock_quantity = fetch_month_total_stock_quantity(
        year=target_year,
        month=target_month,
    )
    outbound_rows = fetch_recent_outbound_rows(
        limit=5,
        year=target_year,
        month=target_month,
    )

    inbound_count = count_inbound_rows(
        year=target_year,
        month=target_month,
    )
    outbound_count = count_outbound_rows(
        year=target_year,
        month=target_month,
    )

    monthly_data = fetch_monthly_stock_chart(
        year=target_year,
    )

    top_stock_rows = fetch_top_sales_stock_rows(
        limit=3,
        year=target_year,
        month=target_month,
    )

    month_start, month_end = _build_month_range(target_year, target_month)

    status_box_data = [
        {
            "title": "입고",
            "count_text": _format_count_text(inbound_count),
            "count": _to_int(inbound_count),
            "subtitle": "최근 입고 내역",
            "rows": _build_recent_inbound_screen_rows(inbound_rows),
        },
        {
            "title": "출고",
            "count_text": _format_count_text(outbound_count),
            "count": _to_int(outbound_count),
            "subtitle": "최근 출고 내역",
            "rows": _build_recent_outbound_screen_rows(outbound_rows),
        },
    ]

    top_stock_section_data = {
        "title": "매출 TOP 3 재고",
        "items": _build_top_stock_items(top_stock_rows),
    }

    return {
        "current_year": target_year,
        "current_month": target_month,
        "current_month_text": f"{target_year}년 {target_month}월",
        "month_start": month_start,
        "month_end": month_end,
        "status_box_data": status_box_data,
        "chart_data": _build_chart_data(monthly_data),
        "total_stock_quantity": _to_int(total_stock_quantity),
        "total_stock_quantity_text": _format_quantity(total_stock_quantity),
        "expiring_stock_count": _to_int(expiring_stock_count),
        "expiring_stock_count_text": _format_count_text(expiring_stock_count),
        "expiring_stock_days": 30,
        "top_stock_section_data": top_stock_section_data,
    }


__all__ = ["fetch_stock_dashboard"]
