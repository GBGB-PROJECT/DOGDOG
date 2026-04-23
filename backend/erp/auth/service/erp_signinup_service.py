from sqlalchemy.orm import Session
from backend.erp.auth.repository.erp_signinup_repository import EmployeeRepository

class AuthService:
    def __init__(self, db: Session):
        self.repo = EmployeeRepository(db)

    def verify_login(self, account_id: str, email: str, password: str):
        try:
            # DB에서 사원 정보 조회
            employee = self.repo.get_auth_info(account_id)
        except Exception as e:
            return 500, "SERVER_ERROR", "현재 DB 연결에 오류가 발생했습니다.", None

    # [수정] 모든 리턴을 (숫자코드, 문자코드, 메시지) 3개로 통일!
        if not employee:
            return 404, "FAIL_ID", "존재하지 않는 아이디입니다.",None

        if employee.email != email:
            return 401, "FAIL_EMAIL", "등록된 이메일이 아닙니다.",None

        if employee.password != password:
            return 401, "FAIL_PASSWORD", "비밀번호가 일치하지 않습니다.",None

        if hasattr(employee, 'active') and not employee.active:
            return 403, "FAIL_ACTIVE", "비활성화된 계정입니다.",None

        emp_data = {
            "username": employee.username,
            "email": employee.email,
            "emp_position_id":employee.position_name if employee.position_name else "직급 없음"
    }

        # 성공 시에도 3개를 맞춰줍니다.
        return 200, "SUCCESS", f"{employee.username}님 환영합니다!", emp_data