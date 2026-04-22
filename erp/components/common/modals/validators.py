import re
from datetime import datetime
import flet as ft


# =========================================================
# ☑️ 등록 폼 검증 유틸
# - 저장 버튼 클릭 전에 이상한 값은 DB로 보내지 않도록 막는다.
# - 화면 1차 검증이고, repository에서도 2차 검증을 한 번 더 한다.
# =========================================================
def show_message(page: ft.Page, text: str):
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(value=text),
            open=True,
        )
    )


def is_valid_url(value: str) -> bool:
    if not value:
        return True
    pattern = re.compile(
        r"^(https?://)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}([/\w .\-?&=%#:]*)?$"
    )
    return bool(re.fullmatch(pattern, value))


def is_valid_email(value: str) -> bool:
    if not value:
        return True
    pattern = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
    return bool(re.fullmatch(pattern, value))


def is_valid_phone(value: str) -> bool:
    if not value:
        return True
    pattern = re.compile(r"^[0-9\-]+$")
    return bool(re.fullmatch(pattern, value)) and len(value) <= 13


def is_valid_business_number(value: str) -> bool:
    if not value:
        return True
    digits = value.replace("-", "").strip()
    return digits.isdigit() and len(digits) == 10


def is_valid_postal(value: str) -> bool:
    if not value:
        return True
    return value.isdigit() and len(value) == 5


def is_valid_date(value: str) -> bool:
    if not value:
        return True
    try:
        parsed = datetime.strptime(value, "%Y-%m-%d")
        return parsed.strftime("%Y-%m-%d") == value
    except ValueError:
        return False


def is_valid_name(value: str) -> bool:
    if not value:
        return True
    pattern = re.compile(r"^[ㄱ-ㅎㅏ-ㅣ가-힣a-zA-Z\s]+$")
    return bool(re.fullmatch(pattern, value))


def normalize_bool_text(value: str):
    clean = (value or "").strip()
    lowered = clean.lower()

    true_values = {
        "true", "1", "y", "yes", "t",
        "예", "사용", "활성", "재직", "구독", "가능", "정상", "판매중",
    }
    false_values = {
        "false", "0", "n", "no", "f",
        "아니오", "미사용", "비활성", "퇴사", "미구독", "비구독", "불가", "취소", "판매중지",
    }

    if lowered in true_values or clean in true_values:
        return True
    if lowered in false_values or clean in false_values:
        return False
    return None


def validate_field_value(field: dict, value: str):
    label = field["label"]
    field_type = field.get("type", "text")
    required = field.get("required", False)
    max_length = field.get("max_length")
    min_value = field.get("min_value")
    max_value = field.get("max_value")
    allowed_values = field.get("allowed_values")

    value = (value or "").strip()

    if required and not value:
        return f"{label}을(를) 입력해주세요."

    if not value:
        return None

    if max_length and len(value) > max_length:
        return f"{label}은(는) {max_length}자 이하로 입력해주세요."

    if allowed_values and value not in allowed_values:
        return f"{label}은(는) {', '.join(allowed_values)} 중 하나로 입력해주세요."

    if field_type == "int":
        normalized = value.replace(",", "")
        if not normalized.isdigit():
            return f"{label}은(는) 숫자만 입력 가능합니다."
        number = int(normalized)
        if min_value is not None and number < min_value:
            return f"{label}은(는) {min_value} 이상이어야 합니다."
        if max_value is not None and number > max_value:
            return f"{label}은(는) {max_value} 이하이어야 합니다."

    if field_type == "day":
        if not value.isdigit():
            return f"{label}은(는) 1~31 사이 숫자만 입력 가능합니다."
        day = int(value)
        if day < 1 or day > 31:
            return f"{label}은(는) 1~31 사이로 입력해주세요."

    if field_type == "float":
        try:
            num = float(value.replace(",", ""))
            if num < 0:
                return f"{label}은(는) 0 이상이어야 합니다."
        except ValueError:
            return f"{label}은(는) 올바른 숫자 형식이어야 합니다."
        if "." in value and len(value.split(".")[1]) > 2:
            return f"{label}은(는) 소수점 두 자리까지만 입력 가능합니다."

    if field_type == "bool":
        if normalize_bool_text(value) is None:
            return f"{label}은(는) Y/N, true/false, 예/아니오, 활성/비활성처럼 명확한 값만 입력 가능합니다."

    if field_type == "url" and not is_valid_url(value):
        return f"{label}의 URL 형식이 올바르지 않습니다."

    if field_type == "name" and not is_valid_name(value):
        return f"{label}에는 숫자 또는 특수문자를 입력할 수 없습니다."

    if field_type == "email" and not is_valid_email(value):
        return f"{label} 형식이 올바르지 않습니다."

    if field_type == "phone" and not is_valid_phone(value):
        return f"{label}은(는) 숫자와 하이픈(-)만 입력 가능합니다."

    if field_type == "bizno" and not is_valid_business_number(value):
        return f"{label}은(는) 10자리 숫자 형식이어야 합니다. 예: 123-45-67890"

    if field_type == "postal" and not is_valid_postal(value):
        return f"{label}은(는) 5자리 숫자로 입력해주세요."

    if field_type == "date" and not is_valid_date(value):
        return f"{label}은(는) YYYY-MM-DD 형식의 올바른 날짜로 입력해주세요."

    return None


def validate_form(page: ft.Page, fields: list, session_prefix: str):
    for field in fields:
        key = f"{session_prefix}_{field['key']}"
        value = page.session.store.get(key) or ""
        error = validate_field_value(field, value)
        if error:
            show_message(page, error)
            return False
    return True
