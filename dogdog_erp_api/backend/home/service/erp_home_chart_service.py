from datetime import date
from sqlalchemy.orm import Session
# 실제 프로젝트 경로에 맞게 Repo 임포트
from backend.erp.home.repository.erp_home_chart_repository import DashboardRepo

class DashboardService:
    """개밥개밥 ERP 대시보드를 위한 서비스 로직을 처리합니다."""

    def __init__(self, db: Session):
        # Service가 생성될 때 Repository도 함께 초기화하여 연결해줍니다.
        self.repo = DashboardRepo(db)

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
    
    def get_production_status_chart(self, target_amount: int = 5000) -> tuple:
        """
        생산 현황(생산 달성률, 불량률) 차트용 데이터를 반환합니다.
        민트색 박스: 전월 대비 증감률(MoM) 적용
        """
        try:
            # 1. Repository 호출 (Raw Data 확보)
            raw_data = self.repo.get_monthly_production_stock()
            
        except Exception as e:
            print(f"🚨 생산 현황 DB 조회 에러 원인: {e}")
            return 500, "DB_ERROR", "생산 데이터를 불러오는 중 DB 연결 오류가 발생했습니다.", None

        if not raw_data:
            return 404, "NOT_FOUND", "해당 기간의 생산 데이터가 존재하지 않습니다.", None

        from datetime import date
        today = date.today()
        
        # 2. 타겟 월 리스트 생성 [작년 동월, 4개월 전, 3개월 전, 2개월 전, 1개월 전, 당월]
        target_months = [f"{today.year - 1}-{today.month:02d}"]
        for i in range(4, -1, -1):
            y, m = today.year, today.month - i
            if m <= 0:
                m += 12
                y -= 1
            target_months.append(f"{y}-{m:02d}")

        # 3. 달성률 및 불량률 리스트 생성
        production_rate = []
        defect_rate = []  # 불량률 예시 데이터 (실제 데이터 연동 가능)

        for tm in target_months:
            month_data = raw_data.get(tm, {"stock": 0, "defect": 0})
            current_stock = month_data["stock"]
            current_defect = month_data["defect"]
            
            # 1. 생산 달성률 계산 (전년 동월 대비 1.2배 목표)
            last_year_month = f"{int(tm[:4])-1}-{tm[5:]}"
            last_year_data = raw_data.get(last_year_month, {"stock": 0})
            target_amount = last_year_data["stock"] * 1.2
            
            p_rate = round((current_stock / target_amount), 2) if target_amount > 0 else 0.0
            production_rate.append(p_rate)

            # 2. 실제 불량률 계산: 불량 / (정상 + 불량)
            total_produced = current_stock + current_defect
            d_rate = round((current_defect / total_produced), 2) if total_produced > 0 else 0.0
            defect_rate.append(d_rate)

        # 4. 민트색 박스용 전월 대비 증감률(MoM) 계산
        # 생산 달성률 MoM: (당월 달성률 - 전월 달성률) / 전월 달성률 * 100
        current_p_rate = production_rate[-1]
        prev_p_rate = production_rate[-2]
        
        if prev_p_rate > 0:
            prod_mom = round(((current_p_rate - prev_p_rate) / prev_p_rate) * 100, 1)
        else:
            prod_mom = 0.0

        # 불량률 MoM 편차: 당월 % - 전월 % (Percentage Point)
        current_d_rate = defect_rate[-1]
        prev_d_rate = defect_rate[-2]
        defect_mom = round((current_d_rate - prev_d_rate) * 100, 1)

        chart_data = {
            "production_rate": production_rate,
            "defect_rate": defect_rate,
            "production_mom": f"{'+' if prod_mom >= 0 else ''}{prod_mom}%",
            "defect_mom": f"{'+' if defect_mom >= 0 else ''}{defect_mom}%p",
            "base_date": today.strftime("%Y/%m/%d")
        }

        return 200, "SUCCESS", "생산 현황 데이터를 성공적으로 불러왔습니다.", chart_data