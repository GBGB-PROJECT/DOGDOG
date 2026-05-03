import datetime
import flet as ft
import flet_charts as fch
from api_client import ApiClient


class LogStatisticsController:
    def __init__(self, page: ft.Page):
        self.page = page
        self.pet_id = page.session.store.get("pet_id") or 1
        self.weekly_data = []
        self.current_category = "water"

    async def fetch_weekly_data(self, category="water"):
        """API 데이터를 가져와 요일별로 합산하고 상세 로그를 남깁니다."""
        self.current_category = category
        now = datetime.datetime.now()
        # 최근 7일 날짜 리스트 (YYYY-MM-DD)
        date_list = [
            (now - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            for i in range(6, -1, -1)
        ]
        daily_sums = {date: 0 for date in date_list}

        print(
            f"\n[DEBUG] 🔍 1. 통계 데이터 요청 시작: /api/v1/logs/{self.pet_id} (Category: {category})"
        )

        # API 호출
        response = await ApiClient.get(f"/api/v1/logs/{self.pet_id}")

        if not response:
            print("[DEBUG] ❌ 에러: API 응답이 None입니다.")
            return []

        # 데이터 리스트 추출 (구조적 유연성 확보)
        data_list = []
        if isinstance(response, dict):
            status = response.get("status")
            data_list = response.get("data", [])
            print(
                f"[DEBUG] 📥 2. 응답 수신 (Dict): Status={status}, 전체 데이터={len(data_list)}개"
            )
        elif hasattr(response, "json"):
            res_json = response.json()
            status = res_json.get("status")
            data_list = res_json.get("data", [])
            print(
                f"[DEBUG] 📥 2. 응답 수신 (Response Obj): Status={status}, 전체 데이터={len(data_list)}개"
            )

        match_count = 0
        for log in data_list:
            raw_ts = log.get("timestamp", "")
            if not raw_ts:
                continue

            # [날짜 매핑] T를 기준으로 분리하여 YYYY-MM-DD 추출
            log_date = raw_ts.split("T")[0]

            if log_date in daily_sums:
                domain = log.get("domain")
                log_cat = log.get("category")
                amount = float(log.get("amount", 0))

                # 카테고리별 필터링 조건 검증
                is_match = False
                if category == "feeding" and domain == "feeding":
                    is_match = True
                elif category == "water" and domain == "numeric" and log_cat == "water":
                    is_match = True
                elif category == "walk" and domain == "numeric" and log_cat == "walk":
                    is_match = True

                if is_match:
                    daily_sums[log_date] += amount
                    match_count += 1

        print(
            f"[DEBUG] 📊 3. 필터링 결과: 카테고리 '{category}'와 일치하는 데이터 {match_count}개 발견"
        )

        # 결과 조립
        weekdays = ["월", "화", "수", "목", "금", "토", "일"]
        result = []
        for d in date_list:
            dt = datetime.datetime.strptime(d, "%Y-%m-%d")
            result.append((weekdays[dt.weekday()], daily_sums[d]))

        self.weekly_data = result
        print(f"[DEBUG] ✅ 4. 최종 차트 데이터 구성 완료: {self.weekly_data}")
        return result

    def get_chart_points(self):
        """fch 전용: 툴팁 중복 방지를 위해 tooltip 인자를 제거한 데이터 포인트 생성"""
        return [
            fch.LineChartDataPoint(
                x=i, 
                y=val
            )
            for i, (_, val) in enumerate(self.weekly_data)
        ]

    def get_bottom_labels(self):
        """fch 규격 하단 요일 라벨 구성"""
        return [
            fch.ChartAxisLabel(
                value=i, label=ft.Text(day, size=11, weight="bold", color="#9E9E9E")
            )
            for i, (day, _) in enumerate(self.weekly_data)
        ]

    def format_value(self, val):
        """천 단위 콤마 포맷팅"""
        try:
            return f"{int(float(val)):,}"
        except:
            return "0"
