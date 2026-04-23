from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from db.models import OpdSubsItem, OpdSalesOrderItem

class DashboardRepo:
    """home_view를 채우기 위한 데이터"""

    def __init__(self, db: Session): # db 연결
        self.db = db

    def get_sale_hightlight(self, target_year: int):
        
        # 1. 구독 상품(Subs) 조회 (last_updates에서 연도만 가위로 오려내어 비교)
        subs_data = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.final_amount * OpdSubsItem.quantity), 0).label("subs_amount"),
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("subs_qty")
        ).filter(extract('year', OpdSubsItem.last_update) == target_year).first()

        # 2. 일반 판매 상품(Sales) 조회 (last_updates에서 연도만 가위로 오려내어 비교)
        sales_data = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount * OpdSalesOrderItem.quantity), 0).label("sales_amount"),
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("sales_qty")
        ).filter(extract('year', OpdSalesOrderItem.last_update) == target_year).first()

        ## 장부 결합
        total_amount = subs_data.subs_amount + sales_data.sales_amount # 매출 합계
        total_qty = subs_data.subs_qty + sales_data.sales_qty # 총 판매 상품 개수

        return {
            "total_amount": total_amount, # 총 매출액
            "total_qty": total_qty        # 총 판매 수량
        }