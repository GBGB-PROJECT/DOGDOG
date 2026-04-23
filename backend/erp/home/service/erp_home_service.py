from sqlalchemy.orm import Session
from backend.erp.home.repository.erp_home_repository import DashboardRepo

class DashboardService:
  def __init__(self, db: Session):
    self.repo = DashboardRepo(db)

  def get_dashboard_hightlight(self, target_year: int):
    try:
      highlight_data = self.repo.get_sale_hightlight(target_year)
    except Exception as e:
      print(f"DB 조회 원인: ", e)
      return 500, "DB_ERROR", "DB 연결에 오류가 발생하였습니다.", None

    if not highlight_data:
      return 404, "NOT_FOUND", "2026 년도의 데이터가 존재하지 않습니다.", None

    return 200 ,"SUCCESS", f"{target_year}년도 매출 현황을 성공적으로 불러왔습니다.", highlight_data