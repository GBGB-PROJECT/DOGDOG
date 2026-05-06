from sqlalchemy.orm import Session
from sqlalchemy import func, extract, exists
from datetime import date
import calendar
from dateutil.relativedelta import relativedelta # 날짜/월 계산을 쉽게 해주는 라이브러리 (필요시 pip install python-dateutil)
# 필요한 모델들을 모두 불러옵니다.
from db.models import ErpStock, ErpInbound, OpdSalesOrderItem, OpdSubsItem, ErpPurchaseOrder, ErpPurchaseOrderItem, OpdProduct, OpdProductDetail

class InvenDashboardRepo:
    """home_view의 생산/재고 하이라이트를 채우기 위한 데이터"""

    def __init__(self, db: Session):
        self.db = db

    def get_inventory_highlight(self): # 인자 제거: 시스템 날짜 기준으로 모두 내부에서 처리
        # 1. 날짜 범위 설정 (성능 최적화용)
        today = date.today()
        first_day = today.replace(day=1)
        last_day_val = calendar.monthrange(today.year, today.month)[1]
        end_day = today.replace(day=last_day_val)
        
        # 다음 달 범위
        next_month_start = first_day + relativedelta(months=1)
        next_month_end = next_month_start.replace(day=calendar.monthrange(next_month_start.year, next_month_start.month)[1])

        last_year_first_day = first_day - relativedelta(years=1)
        last_year_end_day = last_year_first_day.replace(day=calendar.monthrange(last_year_first_day.year, last_year_first_day.month)[1])

        # [1] 이번 달 생산/입고량 (범위 검색으로 변경)
        monthly_production = (
        self.db.query(func.coalesce(func.sum(ErpStock.stock_available), 0))
        .filter(
            ErpStock.inbound_id.in_(
                self.db.query(ErpInbound.inbound_id)
                .filter(
                    ErpInbound.inbound_complete >= first_day,
                    ErpInbound.inbound_complete <= end_day
                )
            )
        )
        .scalar()
)

        # ===========================================
        # [작년 동월 생산/입고량 조회 및 증감 계산]
        # ===========================================
        last_year_production = (
            self.db.query(func.coalesce(func.sum(ErpStock.stock_available), 0))
            .filter(
                ErpStock.inbound_id.in_(
                    self.db.query(ErpInbound.inbound_id)
                    .filter(
                        ErpInbound.inbound_complete >= last_year_first_day,
                        ErpInbound.inbound_complete <= last_year_end_day
                    )
                )
            )
            .scalar()
        )
        
        production_diff = monthly_production - last_year_production

        # [2] 입고 예정 (다음 달)
        expected_incoming = (
            self.db.query(func.coalesce(func.sum(ErpPurchaseOrderItem.quantity), 0))
            .join(ErpPurchaseOrder, ErpPurchaseOrderItem.purchase_order_id == ErpPurchaseOrder.purchase_order_id)
            .filter(ErpPurchaseOrder.inbound_scheduled_date >= next_month_start, 
                    ErpPurchaseOrder.inbound_scheduled_date <= next_month_end)
            .scalar()
        )

        # [3] 총 판매량 (일반 + 구독)
        # 일반 판매
        monthly_sales = self.db.query(func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0)).filter(
            OpdSalesOrderItem.last_update >= first_day, # 필드명은 DB 구조에 맞춰 조정
            OpdSalesOrderItem.last_update <= end_day
        ).scalar()

        # 구독 판매 (필터 기준을 구독 생성일/결제일로 수정)
        monthly_subs = self.db.query(func.coalesce(func.sum(OpdSubsItem.quantity), 0)).filter(
            OpdSubsItem.last_update >= first_day, 
            OpdSubsItem.last_update <= end_day
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
            "current_total_inventory": self.db.query(func.coalesce(func.sum(ErpStock.stock_available), 0)).scalar(),   # 전년 대비 성장(현재고)
            "yoy_inventory_growth": production_diff, # 전년 대비 증감량
            "monthly_total_sales": total_monthly_sales_qty,    # 총 판매량수
            "stock_type_status": stock_type_status             # 사료별 재고 현황(차트용)                     # 사료 타입별 개수 
        }