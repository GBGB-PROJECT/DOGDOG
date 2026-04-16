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
