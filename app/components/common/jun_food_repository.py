from junhwan.database.db import get_connection
from junhwan.database.queries import Product


def fetch_food_rows(keyword=""):
    conn = None
    cursor = None
    # ✅ conn: DB 연결 객체 (데이터베이스랑 연결하는 통로)
    # ✅ cursor: SQL 실행 도구 (쿼리 날리는 손)

    try:
        # ☑️ DB 연결 시작
        conn = get_connection()

        # ☑️ cursor 생성 (이걸로 SQL 실행함)
        cursor = conn.cursor()

        # ☑️ 검색어가 있는지 확인
        if keyword.strip():
            # ☑️ keyword가 있으면 → 검색 쿼리 실행
            cursor.execute(
                Product.product_search_query,
                (f"%{keyword.strip()}%",),
            )
            # 👉 %키워드% = 포함 검색 (LIKE)

        else:
            # ☑️ keyword 없으면 → 전체 목록 조회
            cursor.execute(Product.product_list_query)

        # ☑️ 실행된 결과 전부 가져오기
        rows = cursor.fetchall()

        # ☑️ 정상 결과 반환
        return rows, None

    except Exception as err:
        # ❌ 에러 발생 시
        if conn is not None:
            # ☑️ 혹시라도 변경된게 있으면 롤백 (되돌림)
            conn.rollback()

        # ☑️ 에러 메시지 반환
        return None, f"사료 조회 실패: {err}"

    finally:
        # 🔚 무조건 실행되는 영역 (성공/실패 상관없이)

        if cursor:
            # ☑️ cursor 닫기 (메모리 정리)
            cursor.close()

        if conn is not None and getattr(conn, "closed", 1) == 0:
            # ☑️ conn이 열려있으면 닫기
            conn.close()