from datetime import datetime, date
from decimal import Decimal


# =========================================================
# ☑️ ERP ORM 조회 공통 유틸
# - SQLAlchemy ORM model 객체를 Flet 화면에서 쓰기 좋은 dict로 변환
# - Decimal / Date / DateTime 값을 Flet 직렬화 가능한 값으로 변환
# - 도메인별 repository에서 공통으로 사용하는 검색어/boolean/date 처리
# =========================================================


def to_plain_value(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return str(value)

    return value


def model_to_dict(model, columns):
    return {
        column: to_plain_value(getattr(model, column, None))
        for column in columns
    }


def like_keyword(keyword: str):
    return f"%{(keyword or '').strip()}%"


def normalize_bool_keyword(keyword: str, true_words=None, false_words=None):
    clean = (keyword or "").strip()
    lowered = clean.lower()

    true_set = set(true_words or []) | {"y", "yes", "true", "1", "사용", "활성"}
    false_set = set(false_words or []) | {"n", "no", "false", "0", "미사용", "비활성"}

    if lowered in true_set or clean in true_set:
        return True

    if lowered in false_set or clean in false_set:
        return False

    return None


def parse_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
