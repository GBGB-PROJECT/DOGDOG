import psycopg2
import os 
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime, date


# =========================================================
# ☑️ .env 파일 간단 로드
# - erp/.env 파일에 있는 DB 접속정보를 os.environ에 올림
# - python-dotenv 설치 없이 사용
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
            os.environ.setdefault(key.strip(), value.strip())


load_env()


# =========================================================
# ☑️ DB 접속 설정
# - 기존 DB_CONFIG 형태 유지
# - 값만 .env / 환경변수에서 읽음
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
# - PostgreSQL에서 가져온 Decimal / datetime 타입은
#   Flet Web(msgpack)에서 바로 직렬화되지 않을 수 있음
# - 따라서 화면에 넘기기 전에 기본 타입으로 변환
#
# 변환 규칙:
# - Decimal -> float
# - datetime/date -> 문자열
# - dict/list/tuple 내부도 재귀적으로 변환
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
# - SELECT 결과를 리스트로 반환
# - RealDictCursor를 사용해서 컬럼명을 key처럼 바로 쓸 수 있음
# - Decimal / datetime 타입은 sanitize_for_flet()로 변환
#
# 예:
# rows = fetch_all(ProductDetail.list_query)
# rows[0]["product_name"]
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
# - SELECT 결과 중 1행만 반환
# - Decimal / datetime 타입은 sanitize_for_flet()로 변환
#
# 예:
# row = fetch_one("SELECT ... WHERE id = %s", (1,))
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
# - 실수로 저장 버튼을 눌러도 DB 반영이 일어나지 않도록 차단
# =========================================================
def execute(query: str, params=None):
    raise RuntimeError(
        "현재는 조회 전용 모드입니다. INSERT / UPDATE / DELETE 는 막아둔 상태입니다."
    )