from datetime import date
from app.home.repository.dashboard_repository import DashboardRepository
from app.calc_feeding.cal_guideIntake_service import get_feeding_guide_summary_service

class DashboardService:
    """홈 화면 대시보드의 비즈니스 로직을 처리합니다."""

    def __init__(self, repository: DashboardRepository):
        self.repo = repository

    def get_dashboard_summary(self, pet_id: int, target_date: date):
        """메인 대시보드 화면을 위한 일일 급여 요약 정보를 생성하여 반환합니다."""
        
        # 1. 일일 급여 통계 (SUM 연산 결과) - 사료 등록 여부와 무관하게 pet_food 테이블 기준
        daily_stats = self.repo.get_daily_feeding_stats(pet_id, target_date)
        current_kcal = daily_stats.get("total_calories", 0)
        current_amount = daily_stats.get("total_amount", 0)

        # 2. 목표 섭취량 및 칼로리 산출 (타 도메인 서비스 호출)
        guide_summary = get_feeding_guide_summary_service(self.repo.db, pet_id)
        
        target_kcal = 0
        guide_intake = 0
        if guide_summary:
            target_kcal = int(guide_summary.get("daily_total_kcal", 0))
            guide_intake = guide_summary.get("guide_intake", 0)
        else:
            # 가이드 정보가 없을 경우 리포지토리에서 기본 급여량이라도 시도
            guide_intake = self.repo.get_target_calories(pet_id)
        
        # 현재 급여 중인 사료 정보 조회 (없을 수 있음)
        info = self.repo.get_active_feeding_info(pet_id)
        cal_per_gram = float(info.one_gram_calories) if info and info.one_gram_calories else 0
        
        # 방어적 사료 정보 조립 (사용자 요청: current_food_info)
        current_food_info = None
        if info:
            product_name = "정보 없음"
            if info.product and info.product.product_detail:
                product_name = info.product.product_detail.product_name

            current_food_info = {
                "product_id": info.product_id,
                "product_name": product_name,
                "one_gram_calories": cal_per_gram
            }

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

        # 기본값 설정 (사료 정보가 없을 때 대비)
        food_inventory = {
            "left_percent": 0,
            "left_intake": 0,
            "total_weight": 0,
            "left_food_count": 0,
            "expected_exdate": None,
        }

        if gauge_data:
            customer_food, product = gauge_data
            
            product_weight = product.weight if product and product.weight else 0
            left_intake = customer_food.left_intake if customer_food and customer_food.left_intake is not None else 0
            left_food_count = (
                customer_food.left_food_count
                if customer_food and hasattr(customer_food, "left_food_count") and customer_food.left_food_count is not None
                else 0
            )

            left_percent = 0
            if product_weight and product_weight > 0:
                left_percent = round((left_intake / product_weight) * 100)

            food_inventory.update({
                "left_percent": left_percent,
                "left_intake": float(left_intake),
                "total_weight": float(product_weight),
                "left_food_count": float(left_food_count),
                "expected_exdate": (
                    customer_food.expected_exdate.strftime("%Y-%m-%d")
                    if customer_food and hasattr(customer_food, "expected_exdate") and customer_food.expected_exdate
                    else None
                ),
            })

        # 4. 반려동물 프로필 정보 조회
        DEFAULT_PROFILE_IMAGE = "app/assets/dogclay.png"
        pet = self.repo.get_pet_profile(pet_id)
        pet_info = {
            "nickname": pet.nickname if pet else "알 수 없음",
            "profile_image": (
                pet.profile_image if pet and pet.profile_image else DEFAULT_PROFILE_IMAGE
            ),
        }

        # 5. 오늘자 활동량 통계 (물, 산책) 집계
        activity_stats = self.repo.get_daily_activity_stats(pet_id, target_date)

        return {
            "query_date": target_date.strftime("%Y-%m-%d"),
            "pet_info": pet_info,
            "feeding_stats": feeding_stats,
            "food_inventory": food_inventory,
            "activity_stats": activity_stats,
            "current_food_info": current_food_info
        }
