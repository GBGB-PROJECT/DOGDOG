from datetime import date
from sqlalchemy.orm import Session
# 실제 프로젝트 경로에 맞게 Repo 임포트
from erp.home.repository.erp_home_chart_repository import DashboardRepo

class DashboardService:
    """개밥개밥 ERP 대시보드를 위한 서비스 로직을 처리합니다."""

    def __init__(self, db: Session):
        # Service가 생성될 때 Repository도 함께 초기화하여 연결해줍니다.
        self.repo = DashboardRepo(db)

    def get_summary_metrics(self, target_year: int = None) -> dict:
        """
        올해 총 매출, 판매량 및 전년 대비 성장률(%)을 계산하여 반환합니다.
        """
        # 연도가 지정되지 않았다면 올해를 기준으로 삼습니다.
        if target_year is None:
            target_year = date.today().year
        try:
            # 1. Repository를 통해 장부 데이터 조회
            raw_data = self.repo.get_sale_hightlight(target_year)
        except Exception as e:
            print(f"매출요약 에러 원인 > ", e)
            return 500, "DB_ERROR", " DB 연결 오류가 발생했습니다.", None

        ## 데이터가 존재하지 않을 경우의 에러 처리
        if not raw_data:
            return 404, "NOT_FOUND", "해당 기간의 매출/판매 데이터가 없음", None

        ## repo에서 data 가져오기
        current_amount = raw_data["total_amount"]
        current_qty = raw_data["total_qty"]
        last_year_amount = raw_data["last_year_amount"]
        last_year_qty = raw_data["last_year_qty"]

        ## 성장률 계산하기: 0나누기 에러 방지하여 계산하기
        growth_amount_rate = 0.0
        if last_year_amount > 0: # 지난 매출이 0보다 큰 경우(일반 계산 可)
            growth_amount_rate = ((current_amount - last_year_amount) / last_year_amount) * 100
        elif last_year_amount == 0 and current_amount > 0: # 작년 매출 0, 올해는 0보다 커(그럼 걍 100%성장으로 퉁침)
            growth_amount_rate = 100.0

        growth_qty_rate = 0.0
        if last_year_qty > 0:
            growth_qty_rate = ((current_qty - last_year_qty) / last_year_qty) * 100
        elif last_year_qty == 0 and current_qty > 0:
            growth_qty_rate = 100.0

        ##  최종 frontend에 보내도록 setting
        summary_data =  {
            "year": target_year,
            "totalAmount": current_amount,
            "totalQuantity": current_qty,
            "growthRate": round(growth_amount_rate, 2),       # 매출 성장률
            "growthQtyRate": round(growth_qty_rate, 2),       # 판매량 성장률 (필요시 사용)
            "lastYearAmount": last_year_amount
        }
        return 200, "SUCCESS", "매출데이터 불러오기 완료.", summary_data      



    def get_chart_statistics(self, period: str) -> tuple:
        """
        요청받은 기간(1주일/1개월/1년)의 차트용 데이터를 반환합니다.
        """
        # 1. 입력값 유효성 검사 (실패 시 400 Bad Request 포장)
        valid_periods = ["1주일", "1개월", "1년"]
        if period not in valid_periods:
            return 400, "BAD_REQUEST", f"유효하지 않은 기간입니다. 다음 중 하나를 선택해주세요: {valid_periods}", None

        try:
            # 2. Repository 호출하여 장부 데이터 가져오기
            chart_data = self.repo.get_chart_data(period)
            
        except Exception as e:
            # DB 연결이나 조회 중 뻗었을 때 500 포장
            print(f"🚨 차트 DB 조회 에러 원인: {e}")
            return 500, "DB_ERROR", "차트 데이터를 불러오는 중 DB 연결 오류가 발생했습니다.", None

        # 3. 데이터가 아예 비어있을 때 404 포장
        if not chart_data:
            return 404, "NOT_FOUND", "해당 기간의 차트 데이터가 존재하지 않습니다.", None

        # (참고: 누락된 날짜를 0으로 채우는 비즈니스 로직은 향후 이 위치에 들어가면 완벽합니다!)

        # 4. 성공적으로 요리가 끝났을 때 200 정상 응답 포장
        return 200, "SUCCESS", "차트 데이터를 성공적으로 불러왔습니다.", chart_data