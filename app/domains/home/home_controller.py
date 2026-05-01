from api_client import ApiClient
import datetime

class HomeController:
    """
    [Controller] HomeController
    역할: 홈 도메인의 데이터를 관리하고 비즈니스 로직을 처리합니다.
    - View(UI)에서 직접 API를 호출하지 않도록 하여 코드의 결합도를 낮춥니다.
    - 서버의 복잡한 데이터를 View가 사용하기 편한 형태로 가공(Formatting)합니다.
    """
    def __init__(self, page):
        self.page = page
        self.api_client = ApiClient(page)

    async def fetch_pets_data(self):
        """
        서버에서 강아지 목록(Pets)을 가져와서 앱 레이아웃에 맞는 형식으로 변환합니다.
        
        가공 전 (API): [{"pet_id": 1, "nickname": "초코", ...}, ...]
        가공 후 (Return): {1: {"nickname": "초코", "birth_day": "2023-01-01", ...}, ...}
        """
        try:
            # 1. API 호출 (GET /api/v1/pets)
            # ApiClient가 기본적으로 /api/v1을 포함하고 있으므로 엔드포인트는 /pets만 사용합니다.
            response = await self.api_client.get("/pets")
            
            if response.status_code == 200:
                # 2. 서버 응답 데이터 추출
                raw_data = response.json().get("data", [])
                
                # 3. 레이아웃(home_layout.py)이 사용하는 딕셔너리 구조로 변환
                pet_dict = {}
                for pet in raw_data:
                    pet_id = pet.get("pet_id")
                    pet_dict[pet_id] = {
                        "nickname": pet.get("nickname"),
                        "birth_day": pet.get("birth_day"),
                        "sex": str(pet.get("sex")), # 성별 정보는 문자열로 통일
                        "profile_image": pet.get("profile_image")
                    }
                
                # 4. 변환된 데이터를 세션 스토리지에 저장하여 다른 화면에서도 공유 가능하게 함
                self.page.session.store.set("pet_list", pet_dict)
                return pet_dict
            else:
                print(f"[HomeController] API 호출 실패: {response.status_code}")
                return {}
        except Exception as e:
            print(f"[HomeController] fetch_pets_data 중 예외 발생: {e}")
            return {}

    async def fetch_dashboard_data(self, pet_id: int):
        """
        특정 반려동물의 대시보드 요약 데이터를 가져와 세션에 업데이트합니다.
        (급여량, 음수량, 산책량, 사료 잔여량 등)
        """
        try:
            # 1. API 호출 (GET /api/v1/home/dashboard/{pet_id})
            response = await self.api_client.get(f"/home/dashboard/{pet_id}")
            
            if response.status_code == 200:
                # 2. 데이터 추출
                dash_data = response.json().get("data", {})
                
                # 3. 기존 세션의 customer_detail을 가져와서 dashboard_sync 부분만 업데이트
                storage = self.page.session.store
                customer_detail = storage.get("customer_detail") or {}
                customer_detail["dashboard_sync"] = dash_data
                
                # 4. 세션 덮어쓰기
                storage.set("customer_detail", customer_detail)
                print(f"[HomeController] 대시보드 데이터 세션 업데이트 완료: {pet_id}")
                return dash_data
            else:
                print(f"[HomeController] 대시보드 API 호출 실패: {response.status_code}")
                return None
        except Exception as e:
            print(f"[HomeController] fetch_dashboard_data 중 예외 발생: {e}")
            return None

    def get_formatted_history(self, count=3):
        """
        최근 활동 기록을 사용자 친화적인 문자열로 변환하여 반환합니다.
        - UI가 복잡한 날짜 계산이나 조건문을 처리하지 않도록 컨트롤러에서 가공합니다.
        """
        raw_history = self.page.session.store.get("history") or {}
        logs = []
        
        # 최신 순으로 정렬되어 있다고 가정
        for _, details in list(raw_history.items())[:count]:
            log_date = details.get("log_date", "")
            if not log_date or " " not in log_date:
                time_str = datetime.datetime.now().strftime("%H:%M")
            else:
                try:
                    time_str = log_date.split()[1][:5] # HH:MM 만 추출
                except (IndexError, AttributeError):
                    time_str = datetime.datetime.now().strftime("%H:%M")
            
            category = details.get("category")
            status = details.get("log_status")
            
            if category == "음수량":
                msg = f"물을 {status}ml 마셨습니다."
            elif category == "급여량":
                msg = f"사료를 {status}g 먹었습니다."
            else:
                msg = f"{category} 활동을 완료했습니다."
                
            logs.append({"message": msg, "time": time_str})
        return logs

    def get_today_record_stats(self):
        """
        오늘의 기록 상단 통계(급여량, 음수량, 산책시간) 및 목표 칼로리 진행률을 계산하여 반환합니다.
        (home.py에서 추출된 로직)
        """
        storage = self.page.session.store
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}

        feeding_stats = dash_data.get("feeding_stats") or {}
        activity_stats = dash_data.get("activity_stats") or {}

        current_amount = feeding_stats.get("current_amount", 0)
        water_total = activity_stats.get("water_total", 0)
        walk_total = activity_stats.get("walk_total", 0)

        current_kcal = feeding_stats.get("current_kcal", 0)
        target_kcal = feeding_stats.get("target_kcal", 0)
        progress_rate = feeding_stats.get("progress_rate", 0)

        try:
            progress_val = float(progress_rate)
            kcal_progress_value = (
                progress_val / 100.0 if progress_val > 1.0 else progress_val
            )
        except (ValueError, TypeError, ZeroDivisionError):
            kcal_progress_value = 0.0

        return {
            "current_amount": current_amount,
            "water_total": water_total,
            "walk_total": walk_total,
            "current_kcal": current_kcal,
            "target_kcal": target_kcal,
            "kcal_progress_value": kcal_progress_value
        }

    def get_food_inventory_stats(self):
        """
        홈 대시보드의 사료 잔여량 데이터를 가공하여 반환합니다.
        (home.py에서 추출된 로직)
        """
        storage = self.page.session.store
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}

        left_intake = inventory.get("left_intake", 0)
        total_weight_g = inventory.get("total_weight", 0)
        total_weight_kg = round(float(total_weight_g) / 1000, 1) if total_weight_g else 0.0

        left_percent = inventory.get("left_percent", 0)
        progress_value = (
            float(left_percent) / 100 if float(left_percent) > 1 else float(left_percent)
        )

        left_days = inventory.get("left_food_count", 0)
        expected_exdate = inventory.get("expected_exdate", "????-??-??")
        expected_exdate_formatted = str(expected_exdate).replace("-", ".")

        return {
            "left_intake": left_intake,
            "total_weight_kg": total_weight_kg,
            "left_days": round(float(left_days), 1) if left_days else "?",
            "progress_value": progress_value,
            "expected_exdate_formatted": expected_exdate_formatted
        }

    def get_feeding_detail_data(self):
        """
        급여 상세 페이지(feeding.py)를 위한 사료 잔여량 및 상세 스펙 병합 데이터를 제공합니다.
        """
        storage = self.page.session.store
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}
        pet_food_detail = storage.get("pet_food_detail") or {}

        # 데이터 병합
        feeding_data = {**inventory, **pet_food_detail}

        if not feeding_data:
            return None

        # 가공
        left_intake = feeding_data.get("left_intake") or feeding_data.get("left_weight", 0)
        total_weight_g = feeding_data.get("total_weight", 0)
        total_weight_kg = round(float(total_weight_g) / 1000, 1) if total_weight_g else 0.0

        left_percent = feeding_data.get("left_percent", 0)
        progress_value = (
            float(left_percent) / 100 if float(left_percent) > 1 else float(left_percent)
        )

        left_days = feeding_data.get("left_food_count") or feeding_data.get("expected_left_days", 0)
        expected_exdate = feeding_data.get("expected_exdate") or feeding_data.get("expected_last_day", "????-??-??")
        expected_exdate_formatted = str(expected_exdate).replace("-", ".")

        brand = feeding_data.get("product_brand") or feeding_data.get("brand") or ""
        product_name = feeding_data.get("product_name") or feeding_data.get("name") or ""
        thumbnail = feeding_data.get("product_thumbnail") or feeding_data.get("thumbnail") or "dogbowl.png"

        return {
            "raw_data": feeding_data,
            "left_intake": left_intake,
            "total_weight_kg": total_weight_kg,
            "left_days": round(float(left_days), 1) if left_days else "?",
            "progress_value": progress_value,
            "expected_exdate_formatted": expected_exdate_formatted,
            "brand": brand,
            "product_name": product_name,
            "thumbnail": thumbnail
        }

    async def get_today_timeline_logs(self, pet_id: int):
        """
        오늘의 기록 타임라인 팝업에 표시할 로그 데이터를 서버에서 가져옵니다.
        API: GET /api/v1/logs/{pet_id}
        """
        try:
            response = await self.api_client.get(f"/logs/{pet_id}")
            if response.status_code == 200:
                data = response.json().get("data", [])
                return data
            else:
                print(f"[HomeController] 타임라인 API 호출 실패: {response.status_code}")
                return []
        except Exception as e:
            print(f"[HomeController] get_today_timeline_logs 중 예외 발생: {e}")
            return []
