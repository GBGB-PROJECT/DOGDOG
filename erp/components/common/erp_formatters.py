import datetime
from decimal import Decimal


def format_date_only(value):
    # 🔥 ERP 조회 화면 공통 날짜 표시
    if not value:
        return ""
    if isinstance(value, datetime.datetime):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, datetime.date):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    return text[:10] if len(text) >= 10 else text


def format_number(value):
    # 🔥 Decimal/int/float 공통 숫자 표시
    if value in (None, ""):
        return ""
    try:
        number = float(value) if isinstance(value, Decimal) else value
        return f"{int(number):,}"
    except (TypeError, ValueError):
        return str(value)


def format_money(value, suffix="원"):
    text = format_number(value)
    return f"{text}{suffix}" if text else ""
