import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime, date


# =========================================================
# ☑️ DB 접속 설정
# - host: DB 서버 주소
# - dbname: 데이터베이스 이름
# - user: DB 계정
# - password: DB 비밀번호
# - port: 포트 번호
#
# ※ 현재는 조회 전용으로만 사용
# ※ INSERT / UPDATE / DELETE 같은 실제 반영 기능은 아예 제거함
# =========================================================
DB_CONFIG = {
    "host": "pg.nas6418.ddns.net",
    "dbname": "Dogdog",
    "user": "dog_5",
    "password": "kosmo",
    "port": 9934,
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