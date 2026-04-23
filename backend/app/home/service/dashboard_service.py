from datetime import date
from app.home.repository.dashboard_repository import DashboardRepository

class DashboardService:
    """홈 화면 대시보드의 비즈니스 로직을 처리합니다."""

    def __init__(self, repository: DashboardRepository):
        self.repo = repository

    def get_dashboard_summary(self, pet_id: int, target_date: date):
        """메인 대시보드 화면을 위한 일일 급여 요약 정보를 생성하여 반환합니다."""
        
        # 1. 일일 급여 통계 (SUM 연산 결과)
        daily_stats = self.repo.get_daily_feeding_stats(pet_id, target_date)
        current_kcal = daily_stats.get("total_calories", 0)
        current_amount = daily_stats.get("total_amount", 0)

        # 2. 목표 섭취량 대비 달성률 계산
        guide_intake = self.repo.get_target_calories(pet_id)
        
        info = self.repo.get_active_feeding_info(pet_id)
        cal_per_gram = float(info.one_gram_calories) if info and info.one_gram_calories else 0
        target_kcal = int(guide_intake * cal_per_gram)
        
        progress_rate = 0
        if target_kcal > 0:
            progress_rate = round((current_kcal / target_kcal) * 100)

        feeding_stats = {
            "current_kcal": current_kcal,
            "target_kcal": target_kcal,
            "current_amount": current_amount,
            "target_amount": guide_intake,
            "progress_rate": progress_rate
        }

        # 3. 사료 잔여량/재고율 등 조회
        gauge_data = self.repo.get_food_inventory_gauge(pet_id)

        if not gauge_data:
            raise ValueError(
                f"반려동물(ID:{pet_id})의 사료 재고 또는 급여 중인 제품 정보를 찾을 수 없습니다."
            )

        customer_food, product = gauge_data

        product_weight = product.weight if product and product.weight else 0
        left_intake = customer_food.left_intake if customer_food.left_intake is not None else 0
        left_food_count = (
            customer_food.left_food_count
            if hasattr(customer_food, "left_food_count") and customer_food.left_food_count is not None
            else 0
        )

        left_percent = 0
        if product_weight and product_weight > 0:
            left_percent = round((left_intake / product_weight) * 100)

        food_inventory = {
            "left_percent": left_percent,
            "left_intake": float(left_intake) if left_intake else 0,
            "total_weight": float(product_weight) if product_weight else 0,
            "left_food_count": float(left_food_count) if left_food_count else 0,
        }

        return {
            "query_date": target_date.strftime("%Y-%m-%d"),
            "feeding_stats": feeding_stats,
            "food_inventory": food_inventory
        }
