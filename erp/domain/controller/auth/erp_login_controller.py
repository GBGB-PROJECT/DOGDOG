import re # 정규표현식(패턴 찾기용 도구)

class AuthController:
    @staticmethod
    def validate_login(user_id, email, password):
        # 1단계: 사번 규정 체크 (GB + 숫자 4자리)
        id_pattern = r"^GB\d{4}$"
        if not user_id:
            return False, "사번을 입력해 주세요.", "id"
        if not re.match(id_pattern, user_id):
            return False, "사번 형식이 올바르지 않습니다. (예: GB0001)", "id"

        # 2단계: 이메일 형식 체크 (@ 와 . 포함)
        email_pattern = r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not email:
            return False, "이메일을 입력해 주세요.", "email"
        if not re.match(email_pattern, email):
            return False, "올바른 이메일 형식이 아닙니다.(예: dogdog@gaebap.com)", "email"

        # 3단계: 비밀번호 길이 체크 (8자 이상)
        if not password:
            return False, "비밀번호를 입력해 주세요.", "pw"
        if re.search(r'[가-힣]', password):
            return False, "비밀번호에 한글을 포함할 수 없습니다.", "pw"

        # 모든 관문을 무사히 통과했다면? 프리패스!
        return True, "", ""