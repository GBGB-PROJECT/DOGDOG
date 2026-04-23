from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
# 필요한 모델들을 모두 불러옵니다.
from db.models import ErpStock, ErpInbound, OpdSalesOrderItem, OpdSubsItem, ErpPurchaseOrder, ErpPurchaseOrderItem, OpdProduct, OpdProductDetail

class InvenDashboardRepo:
    """home_view의 생산/재고 하이라이트를 채우기 위한 데이터"""

    def __init__(self, db: Session):
        self.db = db
  
    def get_inventory_highlight(self, start_date: date, end_date: date, target_year: int = 2026):
        
        # ==========================================
        # [3월 생산량(입고량)]
        # ==========================================
        monthly_stock_data = (
            self.db.query(
                func.coalesce(func.sum(ErpStock.save_stock), 0).label("monthly_stock")
            )
            .join(ErpInbound, ErpStock.inbound_id == ErpInbound.inbound_id)
            .filter(  
                # [수정] inbound_complete 대신 실제 날짜가 들어있는 컬럼(예: inbound_date)을 사용해야 합니다.
                ErpInbound.inbound_complete >= start_date,    
                ErpInbound.inbound_complete <= end_date
                # (선택) 만약 완료된 것만 필요하다면 ErpInbound.inbound_complete == True 를 추가하세요.
            )
            .first()
        )

        # ==========================================
        # [4월 입고 예정량 - 구매 주문 기준]
        # ==========================================
        expected_inbound_data = (
            self.db.query(
                func.coalesce(func.sum(ErpPurchaseOrderItem.quantity), 0).label("expected_qty")
            )
            .join(ErpPurchaseOrder, ErpPurchaseOrderItem.purchase_order_id == ErpPurchaseOrder.purchase_order_id)
            .filter(
                extract('year', ErpPurchaseOrder.inbound_scheduled_date) == target_year,
                extract('month', ErpPurchaseOrder.inbound_scheduled_date) == 4
            )
            .first()
        )

        # ==========================================
        # [현재 총 재고량 조회]
        # ==========================================
        current_stock_data = (
            self.db.query(
                func.coalesce(func.sum(ErpStock.stock_available), 0).label("total_available")
            )
            .first()
        )

        # ==========================================
        # [월평균 판매량 - 전체 데이터 기준]
        # ==========================================
        sales_data = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0)
        ).scalar() 

        subs_data = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.quantity), 0)
        ).scalar() 

        total_qty = (sales_data or 0) + (subs_data or 0)
        monthly_avg_sales = total_qty // 12

        # ===========================================
        # [판매 사료의 각 타입의 합]
        # ===========================================
        """
        OPDProduct와 OPDProduct_detail을 조인하여, 
        판매 중(active=True)인 상품의 타입(type)별 개수를 반환합니다.
        """
        feed_size_count_data = (
            self.db.query(
                OpdProductDetail.type.label("feed_type"),
                func.count(OpdProduct.product_id).label("type_count")
            )
            # [수정] OpdProduct.product_id 와 OpdProductDetail.product_id 를 올바르게 연결합니다.
            .join(OpdProductDetail, OpdProduct.product_id == OpdProductDetail.product_detail_id)
            .filter(
                OpdProduct.active == True
            )
            .group_by(OpdProductDetail.type)
            .all()
        )

        # 프론트엔드가 사용하기 편하도록 [{"건식", 10}, {"습식", 5}] 같은 리스트를
        # {"건식": 10, "습식": 5, "간식": 3} 형태의 깔끔한 딕셔너리로 변환합니다.
        feed_type_counts = {row.feed_type: row.type_count for row in feed_size_count_data}


        # ===========================================
        # [최종 바구니(Return)]
        # ===========================================
        return {
            "monthly_stock": monthly_stock_data.monthly_stock,            # 3월 생산(입고)량
            "expected_inbound_stock": expected_inbound_data.expected_qty, # 4월 입고 예정량
            "monthly_available_stock": current_stock_data.total_available,# 현재 총 재고량
            "monthly_avg_sales": monthly_avg_sales,                       # 월평균 판매량
            "feed_type_counts": feed_type_counts                          # [추가] 사료 타입별 개수 
        }