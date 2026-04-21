import os
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime, date


# =========================================================
# ☑️ .env 파일 간단 로드
# - erp/.env 파일에 있는 DB 접속정보를 os.environ에 올림
# - python-dotenv 설치 없이 표준 라이브러리만 사용
# =========================================================
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), ".env")

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()


# =========================================================
# ☑️ DB 접속 설정
# - 기존 DB_CONFIG 구조 유지
# - 실제 접속정보는 erp/.env 또는 OS 환경변수에서 읽어옴
# =========================================================
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": int(os.getenv("DB_PORT", "5432")),
}


# =========================================================
# ☑️ 공통 DB 연결 함수
# - psycopg2로 PostgreSQL DB 연결
# =========================================================
def get_connection():
    return psycopg2.connect(**DB_CONFIG)


# =========================================================
# ☑️ Flet 직렬화용 값 변환
# =========================================================
def sanitize_for_flet(value):
    if isinstance(value, Decimal):
        return float(value)

    if isinstance(value, (datetime, date)):
        return str(value)

    if isinstance(value, dict):
        return {
            key: sanitize_for_flet(val)
            for key, val in value.items()
        }

    if isinstance(value, list):
        return [sanitize_for_flet(item) for item in value]

    if isinstance(value, tuple):
        return tuple(sanitize_for_flet(item) for item in value)

    return value


# =========================================================
# ☑️ 여러 행 조회
# =========================================================
def fetch_all(query: str, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return sanitize_for_flet(rows)
    finally:
        conn.close()


# =========================================================
# ☑️ 한 행만 조회
# =========================================================
def fetch_one(query: str, params=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params or ())
            row = cur.fetchone()
            return sanitize_for_flet(row)
    finally:
        conn.close()


# =========================================================
# ☑️ 실행 함수 제거
# - 실제 데이터 저장/수정/삭제를 막기 위해 execute()는 사용 불가
# =========================================================
def execute(query: str, params=None):
    raise RuntimeError(
        "현재는 조회 전용 모드입니다. INSERT / UPDATE / DELETE 는 막아둔 상태입니다."
    )