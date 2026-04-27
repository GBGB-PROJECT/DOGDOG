# =========================================================
# 🔥 ERP Frontend HTTP API Client
# - Flet 화면에서 backend service/repository를 직접 import하지 않기 위한 공통 클라이언트
# - 기본 주소는 로컬 FastAPI 서버
# - 필요 시 환경변수 ERP_API_BASE_URL=http://127.0.0.1:8000 형태로 변경 가능
# =========================================================

import os
from urllib.parse import urljoin

import requests


API_BASE_URL = os.getenv("ERP_API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_TIMEOUT = 10


def _build_url(path: str) -> str:
    clean_path = str(path or "").lstrip("/")
    return urljoin(f"{API_BASE_URL}/", clean_path)


def _extract_error_message(payload, fallback: str):
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, dict):
            return detail.get("message") or detail.get("error_code") or fallback
        if isinstance(detail, str):
            return detail
        return payload.get("message") or fallback
    return fallback


def get_json(path: str, params: dict | None = None):
    url = _build_url(path)

    try:
        response = requests.get(url, params=params or {}, timeout=DEFAULT_TIMEOUT)
    except requests.RequestException as exc:
        raise RuntimeError(f"API 서버에 연결할 수 없습니다. FastAPI 서버 실행 여부를 확인하세요. ({exc})")

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if response.status_code >= 400:
        raise RuntimeError(_extract_error_message(payload, f"API 요청 실패: {response.status_code}"))

    return payload
