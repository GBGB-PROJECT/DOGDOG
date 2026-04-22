from sqlalchemy.orm import Session
from db.models import ErpEmployee 
"""현재 table에서 account_id, email, password, active 을 가지고 옴"""

class EmployeeRepository:
    """인사 관리를 위한 창고지기"""

    def __init__(self, db: Session): # db 연결
        self.db = db

    def get_auth_info(self, account_id: str): # 정보 가져오기
        """
        [인증 전용 조회] 
        전체 정보 대신, 대조에 필요한 딱 3가지 핵심 정보만 포스트잇에 적어옵니다.
        """
        return (
            self.db.query(
                ErpEmployee.account_id, # account_id
                ErpEmployee.email, # email
                ErpEmployee.password, # password
                ErpEmployee.username
            )
            .filter(ErpEmployee.account_id == account_id)
            .first() # 조건에 맞는 사람 1명의 메모만 가져옵니다.
        )