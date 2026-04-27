# =========================================================
# 🔥 생산관리 메인 대시보드 Service
# - Repository의 raw DB 값을 Flet 화면에서 바로 쓰기 좋은 구조로 변환
# =========================================================

from datetime import date, datetime

from .dashboard_repository import (
    count_defective_rows,
    count_production_rows,
    fetch_dashboard_base_year,
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


def _format_stock(value):
    return f"{_to_int(value):,} ea"


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
# =========================================================
def _build_purchase_card_items(rows):
    items = []
    for row in rows:
        product_name = row.get("represent_product_name") or row.get("supplier_name") or "발주 상품"
        item_count = _to_int(row.get("item_count"), 1)

        if item_count > 1:
            card_name = f"{product_name} 외 {item_count - 1}건"
        else:
            card_name = product_name

        items.append(
            {
                "name": card_name,
                "action_text": "상세 내역",
                "purchase_order_id": row.get("purchase_order_id", ""),
                "rows": [
                    ("발주 일자", _format_full_date(row.get("contract_date"))),
                    ("현 재고량", _format_stock(row.get("stock_available_sum"))),
                    ("입고 예정일", _format_full_date(row.get("inbound_scheduled_date"))),
                ],
            }
        )

    return items


# =========================================================
# 🔥 생산관리 메인 대시보드 전체 조회
# =========================================================
def fetch_production_dashboard(year=None):
    target_year = int(year or fetch_dashboard_base_year())

    production_rows = fetch_recent_production_rows(limit=5)
    defective_rows = fetch_recent_defective_rows(limit=5)
    monthly_rows = fetch_monthly_production_chart(year=target_year)
    purchase_card_rows = fetch_recent_purchase_cards(limit=5)

    production_count = count_production_rows()
    defective_count = count_defective_rows()

    status_box_data = [
        {
            "title": "생산 입고",
            "count_text": _format_count_text(production_count),
            "subtitle": "최근 생산 내역",
            "rows": _build_recent_production_screen_rows(production_rows),
        },
        {
            "title": "불량 내역",
            "count_text": _format_count_text(defective_count),
            "subtitle": "최근 불량 내역",
            "rows": _build_recent_defective_screen_rows(defective_rows),
        },
    ]

    top_production_section_data = {
        "title": "최근 발주 내역",
        "items": _build_purchase_card_items(purchase_card_rows),
    }

    return {
        "current_month_text": f"{target_year}년 {date.today().month}월",
        "status_box_data": status_box_data,
        "chart_data": _build_chart_data(monthly_rows),
        "top_production_section_data": top_production_section_data,
    }


__all__ = ["fetch_production_dashboard"]
