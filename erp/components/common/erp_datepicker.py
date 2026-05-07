import datetime


def normalize_datepicker_value(value, add_hours=9):
    # 🔥 Flet DatePicker UTC성 값으로 하루 밀리는 문제 방지용 공통 보정
    if not value:
        return None

    if isinstance(value, datetime.datetime):
        return (value + datetime.timedelta(hours=add_hours)).replace(tzinfo=None)

    if isinstance(value, datetime.date):
        base = datetime.datetime(value.year, value.month, value.day)
        return (base + datetime.timedelta(hours=add_hours)).replace(tzinfo=None)

    return value


def normalize_datepicker_date(value, add_hours=9):
    normalized = normalize_datepicker_value(value, add_hours=add_hours)
    if isinstance(normalized, datetime.datetime):
        return normalized.date()
    return normalized


def parse_prefilter_datetime(value):
    if not value:
        return None
    if isinstance(value, datetime.datetime):
        return value.replace(tzinfo=None)
    if isinstance(value, datetime.date):
        return datetime.datetime(value.year, value.month, value.day)
    clean = str(value).strip()[:10]
    for fmt in ("%Y-%m-%d", "%Y.%m.%d"):
        try:
            return datetime.datetime.strptime(clean.replace(".", "-"), "%Y-%m-%d") if fmt == "%Y.%m.%d" else datetime.datetime.strptime(clean, fmt)
        except ValueError:
            pass
    return None


def parse_prefilter_date(value):
    parsed = parse_prefilter_datetime(value)
    return parsed.date() if isinstance(parsed, datetime.datetime) else parsed
