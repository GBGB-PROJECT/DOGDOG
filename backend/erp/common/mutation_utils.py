from datetime import datetime, date


# =========================================================
# ☑️ 등록/수정용 값 변환 공통 유틸
# - 모달 입력값은 대부분 문자열로 들어오기 때문에
# - DB insert 전에 int / float / bool / date / None으로 변환한다.
# =========================================================
def clean_text(value):
    if value is None:
        return None
    value = str(value).strip()
    return value if value != "" else None


def to_int_or_none(value):
    value = clean_text(value)
    if value is None:
        return None
    return int(str(value).replace(",", ""))


def to_float_or_none(value):
    value = clean_text(value)
    if value is None:
        return None
    return float(str(value).replace(",", ""))


def to_bool_or_none(value, default=None):
    value = clean_text(value)
    if value is None:
        return default

    lowered = str(value).lower()
    if lowered in {"true", "1", "y", "yes", "t"} or value in {
        "예", "사용", "활성", "재직", "구독", "가능", "정상", "판매중"
    }:
        return True

    if lowered in {"false", "0", "n", "no", "f"} or value in {
        "아니오", "미사용", "비활성", "퇴사", "미구독", "비구독", "불가", "취소", "판매중지"
    }:
        return False

    return default


# 기존 설명과 호환되도록 별칭 유지
to_bool = to_bool_or_none


def require_int(value, label):
    parsed = to_int_or_none(value)
    if parsed is None:
        raise ValueError(f"{label}은(는) 필수 입력값입니다.")
    return parsed


def require_bool(value, label):
    parsed = to_bool_or_none(value, None)
    if parsed is None:
        raise ValueError(f"{label}은(는) Y/N 또는 true/false처럼 명확한 값만 입력 가능합니다.")
    return parsed


def require_text(value, label):
    parsed = clean_text(value)
    if parsed is None:
        raise ValueError(f"{label}은(는) 필수 입력값입니다.")
    return parsed


def to_date_or_none(value):
    value = clean_text(value)
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(str(value), "%Y-%m-%d").date()


def require_date(value, label):
    parsed = to_date_or_none(value)
    if parsed is None:
        raise ValueError(f"{label}은(는) 필수 입력값입니다.")
    return parsed
