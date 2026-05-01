from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta
from collections import defaultdict 
from db.models import OpdSubsItem, OpdSalesOrderItem, ErpStock, ErpInbound, ErpPurchaseOrderItem

class DashboardRepo:
    """home_view의 매출 하이라이트를 채우기 위한 데이터"""

    def __init__(self, db: Session): 
        self.db = db

    # [추가할 부분] 차트용 주/월/년도별 매출 및 판매량 조회
    def get_chart_data(self, period: str) -> list[dict]:
        """
        요청받은 기간(1주일/1개월/1년)에 맞춰 
        구독 상품과 일반 상품의 매출액(revenue)과 판매량(volume)을 그룹화하여 반환합니다.
        """
        today = date.today()
        end_date = today
        
        # 1. 기간에 따른 그룹화 기준(DB) 및 조회 시작일 설정
        if period == "1주일":
            start_date = today - timedelta(days=6)
            group_subs = func.date(OpdSubsItem.last_update)
            group_sales = func.date(OpdSalesOrderItem.last_update)
        
        elif period == "1개월":
            # 올해 데이터 (월별)
            start_date = date(today.year, 1, 1)
            group_subs = extract('month', OpdSubsItem.last_update)
            group_sales = extract('month', OpdSalesOrderItem.last_update)
            
        elif period == "1년":
            # 최근 5년 (연도별)
            start_date = date(today.year - 4, 1, 1)
            group_subs = extract('year', OpdSubsItem.last_update)
            group_sales = extract('year', OpdSalesOrderItem.last_update)
            
        else:
            return []

        merged_data = defaultdict(lambda: {"revenue": 0, "volume": 0})

        # [추가된 부분] 1주일의 경우 데이터가 없는 날도 포함하여 정확히 7개 출력 보장
        if period == "1주일":
            for i in range(6, -1, -1):
                target_date = today - timedelta(days=i)
                merged_data[target_date.strftime("%m/%d")] = {"revenue": 0, "volume": 0}

# 3. 구독 상품 조회 (Group By)
        subs_data = self.db.query(
            group_subs.label("label"),
            func.coalesce(func.sum(OpdSubsItem.final_amount), 0).label("revenue"),
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("volume")
        ).filter(
            func.date(OpdSubsItem.last_update) >= start_date,
            func.date(OpdSubsItem.last_update) <= end_date  
        ).group_by(group_subs).all()

        for row in subs_data:
            label_str = self._format_label(period, row.label)
            merged_data[label_str]["revenue"] += int(row.revenue)
            merged_data[label_str]["volume"] += int(row.volume)

    # 일반 판매 상품 조회 부분
        sales_data = self.db.query(
            group_sales.label("label"),
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).label("revenue"),
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("volume")
        ).filter(
            func.date(OpdSalesOrderItem.last_update) >= start_date,
            func.date(OpdSalesOrderItem.last_update) <= end_date  # 이 부분이 반드시 포함되어야 합니다.
        ).group_by(group_sales).all()

    # 구독 상품 조회 부분
        subs_data = self.db.query(
            group_subs.label("label"),
            func.coalesce(func.sum(OpdSubsItem.final_amount), 0).label("revenue"),
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("volume")
        ).filter(
            func.date(OpdSubsItem.last_update) >= start_date,
            func.date(OpdSubsItem.last_update) <= end_date  # 이 부분이 반드시 포함되어야 합니다.
        ).group_by(group_subs).all()

        # 누락되었던 반복문 복구
        for row in subs_data:
            label_str = self._format_label(period, row.label)
            merged_data[label_str]["revenue"] += int(row.revenue)
            merged_data[label_str]["volume"] += int(row.volume)

        # 5. 프론트엔드가 요구하는 형식의 리스트로 변환 후 시간순 정렬
        formatted_data = []
        for key in sorted(merged_data.keys()): 
            formatted_data.append({
                "period": key,
                "revenue": merged_data[key]["revenue"],
                "volume": merged_data[key]["volume"]
            })

        return formatted_data

    def _format_label(self, period_type: str, raw_label) -> str:
        """
        DB에서 추출된 그룹화 기준 값을 차트 X축에 맞게 이쁘게 포맷팅합니다.
        """
        if period_type == "1주일":
            # 날짜 객체 또는 문자열(SQLite 등) 처리 -> "04/01" 형식
            if isinstance(raw_label, str):
                return raw_label[5:10].replace("-", "/") 
            return raw_label.strftime("%m/%d")
            
        elif period_type == "1개월":
            # extract('month')는 보통 숫자를 반환함 -> "4월" 형식
            return f"{int(raw_label)}월"
            
        elif period_type == "1년":
            # extract('year') -> "2026년" 형식
            return str(int(raw_label))
            
        return str(raw_label)

    ## 순수하게 데이터만 출력하는 repo
    def get_monthly_production_stock(self) -> dict:
        """
        DB에서 월별 입고 완료된 재고 총량을 조회합니다.
        범위: 전년 1월 1일부터 현재까지 (YoY 및 MoM 계산용)
        """
        today = date.today()
        # 전년도 동월 데이터 및 전월 데이터를 비교하기 위해 작년 1월부터 조회
        start_date = date(today.year - 1, 1, 1)

        # PostgreSQL 환경에 최적화된 날짜 포맷팅 (YYYY-MM)
        month_expr = func.to_char(ErpInbound.inbound_complete, 'YYYY-MM')

        results = self.db.query(
            month_expr.label('month'),
            func.sum(ErpStock.save_stock).label('total_stock'),
            func.sum(ErpPurchaseOrderItem.defective).label('total_defect') 
        ).join(
            ErpStock, ErpInbound.inbound_id == ErpStock.inbound_id  # Inbound와 Stock 연결
        ).join(
            ErpPurchaseOrderItem, ErpInbound.purchase_order_id == ErpPurchaseOrderItem.purchase_order_id # Inbound와 Purchase 연결
        ).filter(
            ErpInbound.inbound_complete >= start_date
        ).group_by(
            month_expr
        ).all()

        # { 'YYYY-MM': {'stock': 100, 'defect': 5} } 형태로 반환
        return {
            row.month: {
                "stock": float(row.total_stock or 0),
                "defect": float(row.total_defect or 0)
            } for row in results
        }