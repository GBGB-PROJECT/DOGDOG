import re
from datetime import datetime
import flet as ft


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

    pattern = re.compile(
        r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    )
    return bool(re.fullmatch(pattern, value))


def is_valid_phone(value: str) -> bool:
    if not value:
        return True

    pattern = re.compile(r"^[0-9\-() ]+$")
    return bool(re.fullmatch(pattern, value))


def is_valid_business_number(value: str) -> bool:
    if not value:
        return True

    digits = value.replace("-", "").strip()
    return digits.isdigit() and len(digits) == 10


def is_valid_postal(value: str) -> bool:
    if not value:
        return True

    digits = value.replace("-", "").strip()
    return digits.isdigit() and len(digits) in [5, 6]


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


def validate_field_value(field: dict, value: str):
    label = field["label"]
    field_type = field.get("type", "text")
    required = field.get("required", False)
    max_length = field.get("max_length")

    value = (value or "").strip()

    if required and not value:
        return f"{label}을(를) 입력해주세요."

    if not value:
        return None

    if max_length and len(value) > max_length:
        return f"{label}은(는) {max_length}자 이하로 입력해주세요."

    if field_type == "int":
        if not value.isdigit():
            return f"{label}은(는) 숫자만 입력 가능합니다."
        if int(value) < 0:
            return f"{label}은(는) 0 이상이어야 합니다."

    if field_type == "float":
        try:
            num = float(value)
            if num < 0:
                return f"{label}은(는) 0 이상이어야 합니다."
        except ValueError:
            return f"{label}은(는) 올바른 숫자 형식이어야 합니다."

        if "." in value and len(value.split(".")[1]) > 2:
            return f"{label}은(는) 소수점 두 자리까지만 입력 가능합니다."

    if field_type == "url":
        if not is_valid_url(value):
            return f"{label}의 URL 형식이 올바르지 않습니다."

    if field_type == "name":
        if not is_valid_name(value):
            return f"{label}에는 숫자 또는 특수문자를 입력할 수 없습니다."

    if field_type == "email":
        if not is_valid_email(value):
            return f"{label} 형식이 올바르지 않습니다."

    if field_type == "phone":
        if not is_valid_phone(value):
            return f"{label} 형식이 올바르지 않습니다."

    if field_type == "bizno":
        if not is_valid_business_number(value):
            return f"{label}은(는) 10자리 숫자 형식이어야 합니다."

    if field_type == "postal":
        if not is_valid_postal(value):
            return f"{label} 형식이 올바르지 않습니다."

    if field_type == "date":
        if not is_valid_date(value):
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