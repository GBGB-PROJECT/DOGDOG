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
        
        # 이번 달의 시작일과 다음 달의 시작일 구하기 (이번 달 생산량 계산용)
        # 예: 오늘이 3월이라면, start_date는 3월 1일, end_date는 4월 1일 직전까지
        this_month_start = date(current_year, current_month, 1)
        next_month_start = this_month_start + relativedelta(months=1) 
        
        # [수정: 익월 구하기] 입고 예정량은 보통 "다음 달" 기준이므로
        next_month = (current_month % 12) + 1
        target_year_for_expected = current_year if next_month > 1 else current_year + 1

        # ==========================================
        # [당월 생산량(입고량)] - 시스템 연/월 기준 필터링
        # ==========================================
        monthly_stock_data = (
            self.db.query(
                # 중복 합산을 방지하기 위해 ErpStock의 합계를 구하되,
                # 조인으로 인해 늘어난 행을 고려하여 로직을 점검해야 합니다.
                func.coalesce(func.sum(ErpStock.save_stock), 0).label("monthly_stock")
            )
            .join(ErpInbound, ErpStock.inbound_id == ErpInbound.inbound_id)
            .filter(  
                # [수정] extract를 사용하여 시스템 연도와 월을 정확히 매칭합니다.
                extract('year', ErpInbound.inbound_complete) == current_year,
                extract('month', ErpInbound.inbound_complete) == current_month
            )
            .first()
        )

        # ==========================================
        # [익월 입고 예정량 - 구매 주문 기준] - 시스템 날짜의 '다음 달' 기준
        # ==========================================
        expected_inbound_data = (
            self.db.query(
                func.coalesce(func.sum(ErpPurchaseOrderItem.quantity), 0).label("expected_qty")
            )
            .join(ErpPurchaseOrder, ErpPurchaseOrderItem.purchase_order_id == ErpPurchaseOrder.purchase_order_id)
            .filter(
                extract('year', ErpPurchaseOrder.inbound_scheduled_date) == target_year_for_expected,
                extract('month', ErpPurchaseOrder.inbound_scheduled_date) == next_month
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
        # [월평균 판매량] - 수정: '올해' 총 판매량을 '현재 월'로 나눔
        # ==========================================
        # 올해 누적 일반 판매량
        sales_data = self.db.query(
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0)
        ).filter(extract('year', OpdSalesOrderItem.last_update) == current_year).scalar() 

        # 올해 누적 구독 판매량
        subs_data = self.db.query(
            func.coalesce(func.sum(OpdSubsItem.quantity), 0)
        ).filter(extract('year', OpdSubsItem.last_update) == current_year).scalar() 

        total_qty_this_year = (sales_data or 0) + (subs_data or 0)
        
        # 예: 5월이라면 올해 총판매량을 5로 나누어 월평균 계산
        monthly_avg_sales = total_qty_this_year // current_month 

        # ===========================================
        # [판매 사료의 각 타입의 합]
        # ===========================================
        feed_size_count_data = (
            self.db.query(
                OpdProductDetail.type.label("feed_type"),
                func.count(OpdProduct.product_id).label("type_count")
            )
            # [수정됨] 어떤 테이블을 메인으로 삼을지 명시적으로 선언해줍니다.
            .select_from(OpdProduct) 
            .join(OpdProductDetail, OpdProduct.product_id == OpdProductDetail.product_detail_id)
            .filter(
                OpdProduct.active == True
            )
            .group_by(OpdProductDetail.type)
            .all()
        )

        feed_type_counts = {row.feed_type: row.type_count for row in feed_size_count_data}

        # ===========================================
        # [최종 바구니(Return)]
        # ===========================================
        return {
            "monthly_stock": monthly_stock_data.monthly_stock,             # 당월 생산(입고)량
            "expected_inbound_stock": expected_inbound_data.expected_qty,  # 익월 입고 예정량
            "monthly_available_stock": current_stock_data.total_available, # 현재 총 재고량
            "monthly_avg_sales": monthly_avg_sales,                        # 당해 연도 누적 월평균 판매량
            "feed_type_counts": feed_type_counts                           # 사료 타입별 개수 
        }