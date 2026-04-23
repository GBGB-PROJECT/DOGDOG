from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from db.models import OpdSubsItem, OpdSalesOrderItem

class DashboardRepo:
    """home_view의 매출 하이라트를 채우기 위한 데이터"""

    def __init__(self, db: Session): # db 연결
        self.db = db

    def get_sale_hightlight(self, target_year: int):
        
        # ==========================================
        # [1] 올해 (target_year) 장부 조회
        # ==========================================
        subs_data = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.final_amount * OpdSubsItem.quantity), 0).label("subs_amount"),
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("subs_qty")
        ).filter(extract('year', OpdSubsItem.last_update) == target_year).first()

        sales_data = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount * OpdSalesOrderItem.quantity), 0).label("sales_amount"),
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("sales_qty")
        ).filter(extract('year', OpdSalesOrderItem.last_update) == target_year).first()

        # 올해 실적 결합
        total_amount = subs_data.subs_amount + sales_data.sales_amount # 총 매출 (올해)
        total_qty = subs_data.subs_qty + sales_data.sales_qty # 총 판매량수 (올해)

        # ==========================================
        # [2] 작년 (target_year - 1) 장부 조회
        # ==========================================
        last_year = target_year - 1 # 작년 연도 계산 (예: 2026 - 1 = 2025)

        # 작년은 '성장률' 계산을 위해 '매출액'만 필요하므로 금액만 가져옵니다.
        subs_data_last_year = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.final_amount * OpdSubsItem.quantity), 0).label("subs_amount")
        ).filter(extract('year', OpdSubsItem.last_update) == last_year).first()

        sales_data_last_year = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount * OpdSalesOrderItem.quantity), 0).label("sales_amount")
        ).filter(extract('year', OpdSalesOrderItem.last_update) == last_year).first()

        # 작년 실적 결합
        last_year_amount = subs_data_last_year.subs_amount + sales_data_last_year.sales_amount # 총 매출 (작년)

        # ==========================================
        # [3] 매니저(Service)에게 결과물 전달
        # ==========================================
        return {
            "total_amount": total_amount,         # 올해 총 매출
            "total_qty": total_qty,               # 올해 총 판매량수
            "last_year_amount": last_year_amount  # 작년 총 매출 (전년 대비 성장률 계산용)
        }
    
    # ==========================================
    # [추가할 부분] 특정 기간(월간/주간) 매출 조회 기능
    # ==========================================
    def get_sales_by_period(self, start_date: date, end_date: date):
        """
        [특정 기간 매출 조회]
        시작일과 종료일을 주면, 그 기간의 장부만 찾아서 매출을 더해줍니다.
        """
        # 1. 구독 상품 (시작일 ~ 종료일 사이의 매출 합산)
        subs_data = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.final_amount * OpdSubsItem.quantity), 0).label("subs_amount")
        ).filter(
            OpdSubsItem.last_update >= start_date,
            OpdSubsItem.last_update <= end_date
        ).first()

        # 2. 일반 판매 상품 (시작일 ~ 종료일 사이의 매출 합산)
        sales_data = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount * OpdSalesOrderItem.quantity), 0).label("sales_amount")
        ).filter(
            OpdSalesOrderItem.last_update >= start_date,
            OpdSalesOrderItem.last_update <= end_date
        ).first()

        # 두 장부의 매출만 더해서 돌려줍니다.
        return subs_data.subs_amount + sales_data.sales_amount