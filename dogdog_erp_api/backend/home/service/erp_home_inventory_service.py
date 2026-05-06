import datetime
from sqlalchemy.orm import Session
from backend.erp.home.repository.erp_home_inventory_repository import InvenDashboardRepo

class InvenDashboardService:
    def __init__(self, db: Session):
        self.repo = InvenDashboardRepo(db)

    def get_invendashboard_highlight(self):
        
        # [수정됨] 창고지기가 알아서 오늘 날짜 기준으로 계산하므로,
        # Service단에서 억지로 2026년 4월 등 하드코딩된 날짜를 만들 필요가 없습니다.
        # 기존의 start_date, end_date, target_year 변수 선언부는 모두 삭제합니다.

        try:
            # 2. 창고지기(Repo)를 호출하여 데이터를 가져옵니다.
            # [수정됨] 이제 메모지(인자) 없이 가볍게 빈 괄호로만 호출합니다.
            inventory_data = self.repo.get_inventory_highlight()
            
        except Exception as e:
            # [핵심] 에러가 났을 때 원인을 파악하기 위해 터미널에 프린트합니다.
            print(f"🚨 생산/재고 DB 조회 에러 원인: {e}")
            return 500, "DB_ERROR", "재고 데이터를 불러오는 중 DB 연결 오류가 발생했습니다.", None

        if not inventory_data:
            return 404, "NOT_FOUND", "해당 기간의 생산/재고 데이터가 존재하지 않습니다.", None

        # 3. 데이터가 무사히 도착했다면, API(카운터 직원)에게 넘겨줄 규격에 맞춰 포장합니다.
        return 200, "SUCCESS", "생산/재고 하이라이트 데이터를 성공적으로 불러왔습니다.", inventory_data