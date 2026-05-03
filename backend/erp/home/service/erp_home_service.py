from sqlalchemy.orm import Session
from erp.home.repository.erp_home_repository import DashboardRepo
import datetime

class DashboardService:
    def __init__(self, db: Session):
        self.repo = DashboardRepo(db)

    def get_dashboard_hightlight(self):
        today = datetime.date.today()
        target_year = today.year

        ### 1. 월 범위 계산 (MTD 방식)
        month_start = today.replace(day=1)
        # 끝 날짜를 '오늘'로 고정하여 미래 데이터 차단
        month_end = today 

        ### 2. 주간 범위 계산 (WTD 방식)
        week_start = today - datetime.timedelta(days=today.weekday())
        # 주간 역시 '오늘'까지만의 실적을 집계
        week_end = today

        # 3. 데이터 조회 (이제 5월 1일 ~ 5월 3일 데이터만 가져옵니다)
        monthly_raw_amount = self.repo.get_sales_by_period(month_start, month_end)
        monthly_amount = monthly_raw_amount if monthly_raw_amount is not None else 0
        
        # 주간 데이터도 동일하게 처리
        weekly_raw_amount = self.repo.get_sales_by_period(week_start, week_end)
        weekly_amount = weekly_raw_amount if weekly_raw_amount is not None else 0

        try:
            # 1. 원본데이터 조회
            highlight_data = self.repo.get_sale_hightlight(target_year)
        except Exception as e:
            print(f"DB 조회 원인: ", e)
            return 500, "DB_ERROR", "DB 연결에 오류가 발생하였습니다.", None

        # [수정] 404 에러 메시지도 동적으로 변경해 두었습니다.
        if not highlight_data:
            return 404, "NOT_FOUND", f"{target_year}년도의 데이터가 존재하지 않습니다.", None

        # 2. 계산 시작
        total_amount = highlight_data["total_amount"] # 총 매출
        last_year_amount = highlight_data["last_year_amount"] # 지난 해

        # ==========================================
        # [계산 1] 전년 대비 성장률 (%)
        # 공식: ((작년 매출 - 올해 매출) / 작년 매출) * 100
        # ==========================================
        if last_year_amount > 0:
            growth_rate = ((last_year_amount - total_amount) / last_year_amount) * 100
        else:
            # 방어막: 작년 매출이 0원이면 나누기 에러(ZeroDivisionError)가 나므로 예외 처리
            growth_rate = 100.0 if total_amount > 0 else 0.0

        # ==========================================
        # [계산 2] 연간 목표대비 달성률 (%)
        # 공식: (올해 매출 / 연간 목표액) * 100
        # ==========================================
        # (임시) 목표액을 60억으로 가정했습니다.
        yearly_target_amount = (last_year_amount)* 1.2 # 올해 목표 매출(작년 * 1.2)
        monthly_target = yearly_target_amount / 12  # 월간 목표 (올해 목표 / 12)
        weekly_target = monthly_target / 4.345 # 주간 목표 (월 목표 / 4.345)

        # 월간 기간 데이터(동적연결)
        monthly_raw_amount = self.repo.get_sales_by_period(month_start, month_end)
        monthly_amount = monthly_raw_amount if monthly_raw_amount is not None else 0
        ### 디버깅 용도
        print(f"Debug: {month_start} ~ {month_end}의 기간 매출액은 {monthly_amount}입니다.")

        # 주간 기간 데이터(동적 연결)
        weekly_amount = self.repo.get_sales_by_period(week_start, week_end)

        target_achievement_rate = (total_amount / yearly_target_amount * 100) if yearly_target_amount > 0 else 0.0 # 전체 매출 / 목표 매출
        monthly_achievement_rate = (monthly_amount / monthly_target * 100) if monthly_target > 0 else 0.0 # 월간 매출 달성률
        weekly_achievement_rate = (weekly_amount / weekly_target * 100) if weekly_target > 0 else 0.0 # 주간 매출 달성률

        # 3. 계산된 결과(%)를 프론트엔드가 쓰기 좋게 딕셔너리에 추가합니다.
        highlight_data['year'] = target_year
        # round(값, 1)을 사용하여 소수점 첫째 자리까지만 깔끔하게 자릅니다.
        highlight_data["growth_rate"] = round(growth_rate, 1)
        highlight_data["target_achievement_rate"] = round(target_achievement_rate, 1)
        
        # 프론트엔드에서 목표 금액 텍스트를 그릴 때 쓸 수 있도록 같이 넘겨줍니다.
        highlight_data["yearly_target_amount"] = int(yearly_target_amount)

        highlight_data["monthly_amount"] = int(monthly_amount) if monthly_amount is not None else 0
        highlight_data["monthly_target"] = int(monthly_target) # 금액은 소수점이 나오지 않게 int()로 정수 처리
        highlight_data["monthly_achievement_rate"] = round(monthly_achievement_rate, 1) if monthly_achievement_rate else 0.0

        highlight_data["weekly_amount"] = weekly_amount
        highlight_data["weekly_target"] = int(weekly_target)
        highlight_data["weekly_achievement_rate"] = round(weekly_achievement_rate, 1)

        return 200, "SUCCESS", f"{target_year}년도 매출 현황을 성공적으로 불러왔습니다.", highlight_data