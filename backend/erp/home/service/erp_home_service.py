from sqlalchemy.orm import Session
from erp.home.repository.erp_home_repository import DashboardRepo
import datetime

class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepo(db)

    def get_dashboard_hightlight(self, target_year: 2026):
        try:
            # 1. 창고지기에게 원본 데이터(올해 매출, 수량, 작년 매출)를 받습니다.
            highlight_data = self.repo.get_sale_hightlight(target_year)
        except Exception as e:
            print(f"DB 조회 원인: ", e)
            return 500, "DB_ERROR", "DB 연결에 오류가 발생하였습니다.", None

        # [수정] 404 에러 메시지도 동적으로 변경해 두었습니다.
        if not highlight_data:
            return 404, "NOT_FOUND", f"{target_year}년도의 데이터가 존재하지 않습니다.", None

        # 2. 매니저의 계산기 두드리기 타임!
        total_amount = highlight_data["total_amount"]
        last_year_amount = highlight_data["last_year_amount"]

        # ==========================================
        # [계산 1] 전년 대비 성장률 (%)
        # 공식: ((올해 매출 - 작년 매출) / 작년 매출) * 100
        # ==========================================
        if last_year_amount > 0:
            growth_rate = ((total_amount - last_year_amount) / last_year_amount) * 100
        else:
            # 방어막: 작년 매출이 0원이면 나누기 에러(ZeroDivisionError)가 나므로 예외 처리
            growth_rate = 100.0 if total_amount > 0 else 0.0

        # ==========================================
        # [계산 2] 연간 목표대비 달성률 (%)
        # 공식: (올해 매출 / 연간 목표액) * 100
        # ==========================================
        # (임시) 목표액을 60억으로 가정했습니다.
        yearly_target_amount = 600000000 
        monthly_target = yearly_target_amount / 12  # 월간 목표
        weekly_target = monthly_target / 4 # 주간 목표

      # 월간 (4월 1일 ~ 4월 30일)
        month_start = datetime.date(2026, 4, 1)
        month_end = datetime.date(2026, 4, 30)
        monthly_amount = self.repo.get_sales_by_period(month_start, month_end)

        # 주간 (5月 3日 - 5月 9日)
        week_start = datetime.date(2026, 5, 3)
        week_end = datetime.date(2026, 5, 9)
        weekly_amount = self.repo.get_sales_by_period(week_start, week_end)


        if yearly_target_amount > 0:
            target_achievement_rate = (total_amount / yearly_target_amount) * 100
        else:
            target_achievement_rate = 0.0
        ## 월간/주간 달성률 계산하기
        monthly_achievement_rate = (monthly_amount / monthly_target) * 100 if monthly_target > 0 else 0.0
        weekly_achievement_rate = (weekly_amount / weekly_target) * 100 if weekly_target > 0 else 0.0


        # 3. 계산된 결과(%)를 프론트엔드가 쓰기 좋게 딕셔너리에 추가합니다.
        # round(값, 1)을 사용하여 소수점 첫째 자리까지만 깔끔하게 자릅니다.
        highlight_data["growth_rate"] = round(growth_rate, 1)
        highlight_data["target_achievement_rate"] = round(target_achievement_rate, 1)
        
        # 프론트엔드에서 목표 금액 텍스트를 그릴 때 쓸 수 있도록 같이 넘겨줍니다.
        highlight_data["yearly_target_amount"] = yearly_target_amount 

        highlight_data["monthly_amount"] = monthly_amount
        highlight_data["monthly_target"] = int(monthly_target) # 금액은 소수점이 나오지 않게 int()로 정수 처리
        highlight_data["monthly_achievement_rate"] = round(monthly_achievement_rate, 1) # 퍼센트는 소수점 첫째 자리까지

        highlight_data["weekly_amount"] = weekly_amount
        highlight_data["weekly_target"] = int(weekly_target)
        highlight_data["weekly_achievement_rate"] = round(weekly_achievement_rate, 1)

        return 200, "SUCCESS", f"{target_year}년도 매출 현황을 성공적으로 불러왔습니다.", highlight_data