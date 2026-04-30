from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from dateutil.relativedelta import relativedelta # 날짜/월 계산을 쉽게 해주는 라이브러리 (필요시 pip install python-dateutil)
# 필요한 모델들을 모두 불러옵니다.
from db.models import ErpStock, ErpInbound, OpdSalesOrderItem, OpdSubsItem, ErpPurchaseOrder, ErpPurchaseOrderItem, OpdProduct, OpdProductDetail

class InvenDashboardRepo:
    """home_view의 생산/재고 하이라이트를 채우기 위한 데이터"""

    def __init__(self, db: Session):
        self.db = db
  
    def get_inventory_highlight(self): # 인자 제거: 시스템 날짜 기준으로 모두 내부에서 처리
        
        # 시스템 날짜 동적 할당
        today = date.today()
        current_year = today.year
        current_month = today.month
        
        # 입고 예정을 구하기 위한 연/월 계산
        next_month_date = today + relativedelta(months=1)
        next_month = next_month_date.month
        target_year_for_expected = next_month_date.year

        # ==========================================
        # [1] 이번 달 생산량(입고량이 더 맞음)
        # ==========================================
        monthly_production = (
            self.db.query(func.coalesce(func.sum(ErpStock.stock_available), 0))
            .join(ErpInbound, ErpStock.inbound_id == ErpInbound.inbound_id)
            .filter(
                extract('year', ErpInbound.inbound_complete) == current_year,
                extract('month', ErpInbound.inbound_complete) == current_month
            )
            .scalar()
        )

        # ==========================================
        # [2] 입고 예정
        # ==========================================
        expected_incoming = (
            self.db.query(func.coalesce(func.sum(ErpPurchaseOrderItem.quantity), 0))
            .join(ErpPurchaseOrder, ErpPurchaseOrderItem.purchase_order_id == ErpPurchaseOrder.purchase_order_id)
            .filter(
                extract('year', ErpPurchaseOrder.inbound_scheduled_date) == target_year_for_expected,
                extract('month', ErpPurchaseOrder.inbound_scheduled_date) == next_month
            )
            .scalar()
        )

        # ==========================================
        # [현재 총 재고량 조회]
        # ==========================================
        ## 현재 총 가용 재고
        current_total_stock = self.db.query(func.coalesce(func.sum(ErpStock.stock_available), 0)).scalar()
        
        # 작년 이맘때(또는 작년말) 총 재고 (비교용)
        last_year_stock = (
            self.db.query(func.coalesce(func.sum(ErpStock.save_stock), 0))
            .join(ErpInbound, ErpStock.inbound_id == ErpInbound.inbound_id)
            .filter(extract('year', ErpInbound.inbound_complete) < current_year)
            .scalar()
        )
        # 이미지의 '850'처럼 현재의 총 재고 상태를 반환하거나 성장 수치를 계산하여 반환
        inventory_growth_val = current_total_stock

        # ==========================================
        # [월평균 판매량] - 수정: '올해' 총 판매량을 '현재 월'로 나눔
        # ==========================================
        monthly_sales = self.db.query(func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0)).filter(
            extract('year', OpdSalesOrderItem.last_update) == current_year,
            extract('month', OpdSalesOrderItem.last_update) == current_month
        ).scalar()

        monthly_subs = self.db.query(func.coalesce(func.sum(OpdSubsItem.quantity), 0)).filter(
            extract('year', OpdSubsItem.last_update) == current_year,
            extract('month', OpdSubsItem.last_update) == current_month
        ).scalar()

        total_monthly_sales_qty = (monthly_sales or 0) + (monthly_subs or 0)

        # ===========================================
        # [판매 사료의 각 타입의 합]
        # ===========================================
        stock_by_type_data = (
            self.db.query(
                OpdProductDetail.type.label("feed_type"),
                func.coalesce(func.sum(ErpStock.stock_available), 0).label("stock_sum")
            )
            .select_from(ErpStock)
            .join(OpdProduct, ErpStock.product_id == OpdProduct.product_id)
            .join(OpdProductDetail, OpdProduct.product_id == OpdProductDetail.product_detail_id)
            .group_by(OpdProductDetail.type)
            .all()
        )

        stock_type_status = {row.feed_type: row.stock_sum for row in stock_by_type_data}
        # ===========================================
        # [최종 바구니(Return)]
        # ===========================================
        return {
            "monthly_production_qty": monthly_production,      # 이번달 생산량
            "expected_incoming_qty": expected_incoming,        # 입고 예정
            "current_total_inventory": inventory_growth_val,   # 전년 대비 성장(현재고)
            "monthly_total_sales": total_monthly_sales_qty,    # 총 판매량수
            "stock_type_status": stock_type_status             # 사료별 재고 현황(차트용)                     # 사료 타입별 개수 
        }