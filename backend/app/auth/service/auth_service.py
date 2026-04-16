from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt
from app.auth.repository.auth_repository import AuthRepository
from app.auth.schemas import EmailSignupRequest

# 중앙화된 config에서 JWT 환경 변수 설정값 임포트
from app.config import (
    JWT_SECRET_KEY, 
    JWT_ALGORITHM, 
    JWT_ACCESS_EXPIRE_MINUTES, 
    JWT_REFRESH_EXPIRE_DAYS
)

# Bcrypt를 사용하는 암호화 컨텍스트
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """회원가입 및 인증 관련 비즈니스 로직을 처리하는 서비스"""
    def __init__(self, repository: AuthRepository):
        self.repo = repository

    def hash_password(self, password: str) -> str:
        """비밀번호(또는 민감한 토큰)를 단방향 Bcrypt로 암호화합니다."""
        return pwd_context.hash(password)

    def create_access_token(self, subject: str) -> str:
        """단기 유효 Access Token을 발급합니다."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_EXPIRE_MINUTES)
        to_encode = {"exp": expire, "sub": str(subject)}
        return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def create_refresh_token(self, subject: str) -> tuple[str, datetime]:
        """장기 유효 Refresh Token과 만료시간을 발급합니다."""
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_EXPIRE_DAYS)
        to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        return encoded_jwt, expire

    def register_user(self, request: EmailSignupRequest):
        """
        이메일 회원가입 요청을 처리합니다.
        1. 이메일 중복 확인
        2. 비밀번호 해싱
        3. 새 레코드(Customer, CustomerDetail) Transaction 기록
        4. 토큰 발급 및 해싱 저장
        """
        # 1. 중복 검증
        existing_user = self.repo.get_customer_by_email(request.email)
        if existing_user:
            raise ValueError("EMAIL_ALREADY_EXISTS")

        # 2. 비밀번호 암호화
        hashed_password = self.hash_password(request.password)

        try:
            # 3. DB 저장 (1단계): customer 테이블에 기본 정보 기록, flush()로 ID 획득
            customer = self.repo.create_customer()
            customer_id = customer.customer_id

            # 4. DB 저장 (2단계): 얻어온 customer_id를 기반으로 customer_detail 생성
            detail = self.repo.create_customer_detail(
                customer_id=customer_id,
                email=request.email,
                hashed_password=hashed_password,
                nickname=request.nickname,
                phone=request.phone
            )
            
            # 토큰 정보를 detail 객체에 업데이트하기 위해 다시 flush
            self.repo.db.flush()

            # 5. 토큰 발급
            access_token = self.create_access_token(subject=str(customer_id))
            refresh_token, refresh_exp = self.create_refresh_token(subject=str(customer_id))

            # 발급된 원본 Refresh Token을 Bcrypt로 해싱하여 업데이트
            hashed_rt = self.hash_password(refresh_token)
            detail.refresh_token = hashed_rt
            
            # DB Schema (DateTime)와 호환되도록 tzinfo 제거
            detail.refresh_token_exp = refresh_exp.replace(tzinfo=None)

            # 6. 최종 커밋 (두 테이블 모두 성공 시)
            self.repo.commit()

            return {
                "customer": detail,
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_in": JWT_ACCESS_EXPIRE_MINUTES
            }
        except Exception as e:
            # 실패 시 전체 롤백 처리를 진행
            self.repo.rollback()
            raise e

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """비밀번호 일치 여부를 확인합니다."""
        return pwd_context.verify(plain_password, hashed_password)

    def login_user(self, request) -> dict:
        """
        이메일과 비밀번호로 로그인하여 토큰을 발급합니다.
        """
        user = self.repo.get_customer_by_email(request.email)
        if not user or not user.password:
            raise ValueError("INVALID_CREDENTIALS")

        if not self.verify_password(request.password, user.password):
            raise ValueError("INVALID_CREDENTIALS")

        customer_id = user.customer_id
        
        # 새로운 토큰 발급
        access_token = self.create_access_token(subject=str(customer_id))
        refresh_token, refresh_exp = self.create_refresh_token(subject=str(customer_id))

        # Refresh 토큰 DB 저장 (해싱)
        hashed_rt = self.hash_password(refresh_token)
        try:
            self.repo.update_refresh_token(
                customer_id=customer_id, 
                hashed_token=hashed_rt, 
                expires_at=refresh_exp.replace(tzinfo=None)
            )
            self.repo.commit()
        except Exception as e:
            self.repo.rollback()
            raise e

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_EXPIRE_MINUTES
        }

    def refresh_user_token(self, refresh_token: str) -> dict:
        """
        Refresh Token을 검증하고 새로운 Access/Refresh Token을 발급합니다.
        """
        try:
            payload = jwt.decode(refresh_token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            customer_id_str = payload.get("sub")
            token_type = payload.get("type")
            
            if token_type != "refresh" or not customer_id_str:
                raise ValueError("INVALID_TOKEN")
                
            customer_id = int(customer_id_str)
        except getattr(jwt, 'JWTError', Exception):
            raise ValueError("INVALID_TOKEN")

        # DB 검증: 유저 확인 및 토큰 일치 여부 확인
        user = self.repo.get_customer_by_id(customer_id)
        if not user or not user.refresh_token:
            raise ValueError("INVALID_TOKEN")

        # 전달받은 Refresh Token과 DB의 해시된 Refresh Token 일치 확인
        if not self.verify_password(refresh_token, user.refresh_token):
            raise ValueError("INVALID_TOKEN")

        # 검증 완료, Rotate Tokens (새로운 토큰 쌍 발급)
        new_access_token = self.create_access_token(subject=str(customer_id))
        new_refresh_token, new_refresh_exp = self.create_refresh_token(subject=str(customer_id))
        new_hashed_rt = self.hash_password(new_refresh_token)

        try:
            self.repo.update_refresh_token(
                customer_id=customer_id, 
                hashed_token=new_hashed_rt, 
                expires_at=new_refresh_exp.replace(tzinfo=None)
            )
            self.repo.commit()
        except Exception as e:
            self.repo.rollback()
            raise e

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "expires_in": JWT_ACCESS_EXPIRE_MINUTES
        }

    def logout_user(self, customer_id: int):
        """
        현재 유저의 리프레시 토큰을 무효화(삭제)합니다.
        """
        try:
            self.repo.clear_refresh_token(customer_id)
            self.repo.commit()
        except Exception as e:
            self.repo.rollback()
            raise e
