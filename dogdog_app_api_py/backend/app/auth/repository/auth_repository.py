from sqlalchemy.orm import Session
from db.models import CompanionCustomer, CompanionCustomerDetail


class AuthRepository:
    """회원 정보 관리를 위한 Repository"""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_by_email(self, email: str) -> CompanionCustomerDetail | None:
        """이메일로 사용자를 조회합니다."""
        return (
            self.db.query(CompanionCustomerDetail)
            .filter(CompanionCustomerDetail.email == email)
            .first()
        )

    def create_customer(self) -> CompanionCustomer:
        """기본 고객 정보를 생성합니다."""
        customer = CompanionCustomer(
            is_subscribed=False, subs_count=0, permission=1, active=True
        )
        self.db.add(customer)
        # customer_id 확보를 위해 flush
        self.db.flush()
        return customer

    def create_customer_detail(
        self,
        customer_id: int,
        email: str,
        hashed_password: str,
        nickname: str,
        phone: str | None,
    ) -> CompanionCustomerDetail:
        """상세 고객 정보를 생성합니다."""
        detail = CompanionCustomerDetail(
            customer_id=customer_id,
            email=email,
            password=hashed_password,
            nickname=nickname,
            phone=phone,
        )
        self.db.add(detail)
        return detail

    def get_customer_by_id(self, customer_id: int) -> CompanionCustomerDetail | None:
        """아이디로 사용자를 조회합니다."""
        return (
            self.db.query(CompanionCustomerDetail)
            .filter(CompanionCustomerDetail.customer_id == customer_id)
            .first()
        )

    def update_refresh_token(self, customer_id: int, hashed_token: str, expires_at) -> None:
        """리프레시 토큰을 업데이트합니다."""
        detail = self.get_customer_by_id(customer_id)
        if detail:
            detail.refresh_token = hashed_token
            detail.refresh_token_exp = expires_at
        self.db.flush()

    def clear_refresh_token(self, customer_id: int) -> None:
        """리프레시 토큰을 무효화(로그아웃)합니다."""
        detail = self.get_customer_by_id(customer_id)
        if detail:
            detail.refresh_token = None
            detail.refresh_token_exp = None
        self.db.flush()

    def commit(self):
        """트랜잭션을 커밋합니다."""
        self.db.commit()

    def rollback(self):
        """오류 시 롤백합니다."""
        self.db.rollback()
