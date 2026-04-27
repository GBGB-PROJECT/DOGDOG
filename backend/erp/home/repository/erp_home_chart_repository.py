from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date, timedelta
from collections import defaultdict 
from db.models import OpdSubsItem, OpdSalesOrderItem

class DashboardRepo:
    """home_view의 매출 하이라이트를 채우기 위한 데이터"""

    def __init__(self, db: Session): 
        self.db = db

    def get_sale_hightlight(self, target_year: int) -> dict:
        """
        주어진 년도와 작년 매출과 판매량을 구함
        구독 상품과 일반 상품 테이블을 합산함
        """
        last_year = target_year - 1
        today = date.today()
        
        # 올해 데이터 구하기 (구독 상품 + 일반 판매상품)
        ## 구독상품 합계(매출액, 개수합계)
        subs_current = self.db.query(
            func.sum(OpdSubsItem.final_amount).label("subs_amount"),
            func.sum(OpdSubsItem.quantity).label("subs_qty")
        ).filter(extract('year',OpdSubsItem.last_update)==target_year).first()

        ## 일반상품 합계(매출액, 개수 합계)
        sales_current = self.db.query(
            func.sum(OpdSalesOrderItem.total_amount).label("sales_amount"),
            func.sum(OpdSalesOrderItem.quantity).label("sales_qty")
        ).filter(extract('year',OpdSalesOrderItem.last_update)==target_year).first()

        # 작년 데이터 조회 (매출액, 개수 필요함)
        subs_last_current = self.db.query(
            func.sum(OpdSubsItem.final_amount).label("subs_last_amount"),
            func.sum(OpdSubsItem.quantity).label("subs_last_qty")
            ).filter(
            extract('year', OpdSubsItem.last_update) == last_year,
            extract('month', OpdSubsItem.last_update) <= today.month
            ).first()
            
        sales_last_current = self.db.query(
            func.sum(OpdSalesOrderItem.total_amount).label("sales_last_amount"),
            func.sum(OpdSalesOrderItem.quantity).label("sales_last_qty")
            ).filter(
            extract('year', OpdSalesOrderItem.last_update) == last_year,
            extract('month', OpdSalesOrderItem.last_update) <= today.month                
            ).first()
        
        ## 최종 조립
        current_totalAmount = (subs_current.subs_amount or 0) + (sales_current.sales_amount or 0)# 매출 총액
        current_totalQty = (subs_current.subs_qty or 0) + (sales_current.sales_qty or 0) # 총 판매 수량
        last_current_totalAmount = (subs_last_current.subs_last_amount or 0) + (sales_last_current.sales_last_amount or 0) #지난 해 총액
        last_current_totalQty = (subs_last_current.subs_last_qty or 0) + (sales_last_current.sales_last_qty or 0)#지난 해 총 판매 수량

        # 4. 반환값 (Service 계층의 변수명과 일치시킴)
        return {
            "total_amount": int(current_totalAmount),
            "total_qty": int(current_totalQty),
            "last_year_amount": int(last_current_totalAmount),
            "last_year_qty": int(last_current_totalQty),
        }


    # ==========================================
    # [추가할 부분] 차트용 주/월/년도별 매출 및 판매량 조회
    # ==========================================
    def get_chart_data(self, period: str) -> list[dict]:
        """
        요청받은 기간(1주일/1개월/1년)에 맞춰 
        구독 상품과 일반 상품의 매출액(revenue)과 판매량(volume)을 그룹화하여 반환합니다.
        """
        today = date.today()
        
        # 1. 기간에 따른 그룹화 기준(DB) 및 조회 시작일 설정
        if period == "1주일":
            # 최근 7일 (일별)
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

        # 2. 두 장부의 데이터를 합치기 위한 기본 딕셔너리 준비
        # 구조 예시: { "4/1": {"revenue": 0, "volume": 0}, "4/2": ... }
        merged_data = defaultdict(lambda: {"revenue": 0, "volume": 0})

# 3. 구독 상품 조회 (Group By)
        subs_data = self.db.query(
            group_subs.label("label"),
            func.coalesce(func.sum(OpdSubsItem.final_amount), 0).label("revenue"), # 수정됨
            func.coalesce(func.sum(OpdSubsItem.quantity), 0).label("volume")
        ).filter(OpdSubsItem.last_update >= start_date).group_by(group_subs).all()

        for row in subs_data:
            label_str = self._format_label(period, row.label)
            merged_data[label_str]["revenue"] += int(row.revenue)
            merged_data[label_str]["volume"] += int(row.volume)

        # 4. 일반 판매 상품 조회 (Group By)
        sales_data = self.db.query(
            group_sales.label("label"),
            func.coalesce(func.sum(OpdSalesOrderItem.total_amount), 0).label("revenue"), # 수정됨
            func.coalesce(func.sum(OpdSalesOrderItem.quantity), 0).label("volume")
        ).filter(OpdSalesOrderItem.last_update >= start_date).group_by(group_sales).all()

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