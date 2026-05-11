import re # 정규표현식(패턴 찾기용 도구)
import httpx

# 🔥 FastAPI 서버 주소
import os
from dotenv import load_dotenv
load_dotenv()
BASE_URL = os.getenv("ERP_API_URL") if os.getenv("ERP_API_URL") else "http://localhost:8001"

class AuthController:
    
    @staticmethod
    def validate_login(uid, email, pw):
        """입력값의 형식이 맞는지 1차 검사 (기존 로직 유지)"""
        if not uid:
            return False, "사번을 입력해주세요.", "id"
        if "@" not in email:
            return False, "올바른 이메일 형식이 아닙니다.", "email"
        if len(pw) < 4:
            return False, "비밀번호는 4자리 이상이어야 합니다.", "pw"
        return True, None, None

    @staticmethod
    def login_user(account_id: str, email: str, password: str):
        """실제 Backend 서버와 통신하여 로그인 수행"""
        url = f"{BASE_URL}/erp/employee/signup"
        
        payload = {
            "account_id": account_id,
            "email": email,
            "password": password
        }

        try:
            # 1. 서버에 데이터 전송
            response = httpx.post(
                url,
                json=payload,
                timeout=5.0
            )

            # 2. 성공 시 (200번대 응답)
            if 200 <= response.status_code < 300:
                return response.json()

            # 3. 실패 시 (서버에서 보낸 에러 메시지 추출)
            try:
                error_data = response.json()
                # 서버가 주는 상세 에러 메시지가 있으면 쓰고, 없으면 기본 메시지 사용
                message = error_data.get("detail", "로그인 정보가 일치하지 않습니다.")
            except Exception:
                message = f"서버 에러 (상태 코드: {response.status_code})"
            
            raise Exception(message)
        
        except httpx.ConnectError:
            raise Exception("Backend 서버가 꺼져 있거나 연결할 수 없습니다.")
        
        except httpx.TimeoutException:
            raise Exception("서버 응답 시간이 초과되었습니다.")
        
        except httpx.RequestError as e:
            raise Exception(f"통신 중 오류 발생: {str(e)}")