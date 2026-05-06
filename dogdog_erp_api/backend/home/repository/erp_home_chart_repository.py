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

    def get_chart_data(self, period: str) -> list[dict]:
        today = date.today()
        end_date = today  # 미래 데이터 차단 원칙 유지
        merged_data = defaultdict(lambda: {"revenue": 0, "volume": 0})

        # 1. 기간 설정 및 그룹화 기준
        if period == "1주일":
            start_date = today - timedelta(days=6)
            group_subs = func.date(OpdSubsItem.last_update)
            group_sales = func.date(OpdSalesOrderItem.last_update)
        elif period == "1개월":
            start_date = date(today.year, 1, 1)
            group_subs = extract('month', OpdSubsItem.last_update)
            group_sales = extract('month', OpdSalesOrderItem.last_update)
        elif period == "1년":
            start_date = date(today.year - 4, 1, 1)
            for y in range(today.year - 4, today.year + 1):
                merged_data[f"{y}년"] = {"revenue": 0, "volume": 0}
            group_subs = extract('year', OpdSubsItem.last_update)
            group_sales = extract('year', OpdSalesOrderItem.last_update)
        else:
            return []

        # 날짜 순서 보장을 위해 순서가 있는 리스트나 정렬용 키를 가진 딕셔너리 사용
        merged_data = defaultdict(lambda: {"revenue": 0, "volume": 0})

        # 2. 데이터 조회 함수 (중복 제거를 위해 내부 함수화)
        def process_query(query_res, period_type):
            for row in query_res:
                label = self._format_label(period_type, row.label)
                merged_data[label]["revenue"] += int(row.revenue or 0)
                merged_data[label]["volume"] += int(row.volume or 0)

        # 구독 상품 조회
        subs_res = self.db.query(
            group_subs.label("label"),
            func.coalesce(func.sum(OpdSubsItem.final_amount), 0).label("revenue"),
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("volume")
        ).filter(func.date(OpdSubsItem.last_update).between(start_date, end_date)).group_by(group_subs).all()
        process_query(subs_res, period)

        # 일반 판매 상품 조회 (누락되었던 처리 추가)
        sales_res = self.db.query(
            group_sales.label("label"),
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).label("revenue"),
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("volume")
        ).filter(func.date(OpdSalesOrderItem.last_update).between(start_date, end_date)).group_by(group_sales).all()
        process_query(sales_res, period)

        # 3. 정렬 로직 보완 (단순 문자열 정렬이 아닌 시간순 정렬 필요)
        # 팁: _format_label의 결과가 "05/01"이나 "2026" 형식이므로 
        # "1월" 대신 "01월"처럼 숫자를 맞추면 sorted()가 잘 작동합니다.
        formatted_data = [
            {"period": key, "revenue": val["revenue"], "volume": val["volume"]}
            for key, val in sorted(merged_data.items())
        ]

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