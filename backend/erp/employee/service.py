from backend.erp.employee.repository import count_employees, fetch_employees


# =========================================================
# ☑️ 인사관리 Service
# - 현재는 조회 전용이라 repository 함수를 그대로 제공
# - 추후 사원 등록/수정/재직상태 처리 로직은 이 파일에서 확장
# =========================================================

__all__ = ["count_employees", "fetch_employees"]
