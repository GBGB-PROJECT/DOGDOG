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
                        "sex": str(pet.get("sex")),  # 성별 정보는 문자열로 통일
                        "profile_image": pet.get("profile_image"),
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
        특정 반려동물의 대시보드 요약 데이터 및 사료 상세 정보를 가져와 세션에 업데이트합니다.
        """
        try:
            # 1. 대시보드 통계 API 호출 (잔여량, 활동량 등)
            response = await self.api_client.get(f"/home/dashboard/{pet_id}")

            if response.status_code == 200:
                dash_data = response.json().get("data", {})
                storage = self.page.session.store

                # 2. 사료 상세 정보 API 호출 (제품명, 브랜드, 썸네일 등)
                try:
                    res_food = await self.api_client.get(f"/pets/{pet_id}/pet_food")
                    pet_food_data = (
                        res_food.json().get("data")
                        if res_food.status_code == 200
                        else {}
                    )
                    storage.set("pet_food_detail", pet_food_data)
                except Exception as fe:
                    print(f"[HomeController] 사료 상세 정보 동기화 중 에러: {fe}")

                # 3. 기존 세션 업데이트
                customer_detail = storage.get("customer_detail") or {}
                customer_detail["dashboard_sync"] = dash_data
                storage.set("customer_detail", customer_detail)

                print(f"[HomeController] 대시보드 및 제품 정보 동기화 완료: {pet_id}")
                return dash_data
            elif response.status_code == 404:
                print(f"[HomeController] 대시보드 데이터 없음 (404): {pet_id}")
                return {} # 데이터가 없는 신규 유저 등 대응
            else:
                print(
                    f"[HomeController] 대시보드 API 호출 실패 ({response.status_code}): {response.text}"
                )
                return {}
        except Exception as e:
            print(f"[HomeController] fetch_dashboard_data 중 예외 발생: {e}")
            return {}

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
                    time_str = log_date.split()[1][:5]  # HH:MM 만 추출
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
            "kcal_progress_value": kcal_progress_value,
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
        total_weight_kg = (
            round(float(total_weight_g) / 1000, 1) if total_weight_g else 0.0
        )

        left_percent = inventory.get("left_percent", 0)
        progress_value = (
            float(left_percent) / 100
            if float(left_percent) > 1
            else float(left_percent)
        )

        left_days = inventory.get("left_food_count", 0)
        expected_exdate = inventory.get("expected_exdate", "????-??-??")
        expected_exdate_formatted = str(expected_exdate).replace("-", ".")

        return {
            "left_intake": left_intake,
            "total_weight_kg": total_weight_kg,
            "left_days": round(float(left_days), 1) if left_days else "?",
            "progress_value": progress_value,
            "expected_exdate_formatted": expected_exdate_formatted,
        }

    async def get_feeding_detail_data(self):
        """
        [리팩터링] 급여 상세 페이지를 위한 데이터 Fetch 로직
        - 세션에서 pet_id를 안전하게 추출
        - 데이터 부재 시 서버 API 재호출 시도
        - 유연한 키 매핑으로 파싱 실패 방지
        """
        storage = self.page.session.store

        # [해결 1] pet_id 세션 추출 로직 강화
        pet_id = (
            storage.get("pet_id")
            or storage.get("customer_pet_id")
            or storage.get("current_pet_id")
        )

        # [해결 2] 상세 페이지 진입 시 데이터 강제 리프레시 (세션 대신 API 우선)
        if pet_id:
            print(f"[DEBUG] 상세 페이지 진입: 최신 데이터 동기화 시도 (pet_id: {pet_id})")
            await self.fetch_dashboard_data(pet_id)
        
        # 최신화된 세션 데이터 다시 가져오기
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}
        pet_food_detail = storage.get("pet_food_detail") or {}

        # 데이터 병합 (우선순위: inventory > pet_food_detail)
        feeding_data = {**pet_food_detail, **inventory}
        print(f"[DEBUG] 상세 페이지 API 응답 데이터: {feeding_data}")

        if not feeding_data:
            print("[DEBUG] 상세 페이지 결과: None (병합된 데이터가 없음)")
            return None

        # [해결 3] 유연한 키 매핑 및 방어 코드 (Key Variant 대응)
        try:
            # 1. 사료 양 관련 (left_intake, left_weight, weight 등)
            left_intake = (
                feeding_data.get("left_intake")
                or feeding_data.get("left_weight")
                or feeding_data.get("amount")
                or 0
            )
            total_weight_g = (
                feeding_data.get("total_weight")
                or feeding_data.get("product_weight")
                or 0
            )
            total_weight_kg = (
                round(float(total_weight_g) / 1000, 1) if total_weight_g else 0.0
            )

            # 2. 진행률 관련
            left_percent = (
                feeding_data.get("left_percent") or feeding_data.get("percent") or 0
            )
            progress_value = (
                float(left_percent) / 100
                if float(left_percent) > 1
                else float(left_percent)
            )

            # 3. 날짜 및 잔여일
            left_days = (
                feeding_data.get("left_food_count")
                or feeding_data.get("expected_left_days")
                or feeding_data.get("left_days")
                or 0
            )
            expected_exdate = (
                feeding_data.get("expected_exdate")
                or feeding_data.get("expected_last_day")
                or feeding_data.get("last_date")
                or "????-??-??"
            )
            expected_exdate_formatted = str(expected_exdate).replace("-", ".")

            # 4. 제품 정보 (Brand, Name, Thumbnail)
            brand = (
                feeding_data.get("product_brand")
                or feeding_data.get("brand_name")
                or feeding_data.get("brand")
                or "정보 없음"
            )
            product_name = (
                feeding_data.get("product_name")
                or feeding_data.get("name")
                or feeding_data.get("product")
                or "알 수 없는 상품"
            )
            thumbnail = (
                feeding_data.get("product_thumbnail")
                or feeding_data.get("thumbnail")
                or feeding_data.get("image_url")
                or "dogbowl.png"
            )

            result_data = {
                "raw_data": feeding_data,
                "left_intake": left_intake,
                "total_weight_kg": total_weight_kg,
                "left_days": round(float(left_days), 1) if left_days else "?",
                "progress_value": progress_value,
                "expected_exdate_formatted": expected_exdate_formatted,
                "brand": brand,
                "product_name": product_name,
                "thumbnail": thumbnail,
            }

            print(f"[DEBUG] 상세 페이지 가공 완료 데이터: {result_data}")
            return result_data

        except Exception as e:
            print(f"[HomeController] get_feeding_detail_data 파싱 에러: {e}")
            return None

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
                print(
                    f"[HomeController] 타임라인 API 호출 실패: {response.status_code}"
                )
                return []
        except Exception as e:
            print(f"[HomeController] get_today_timeline_logs 중 예외 발생: {e}")
            return []
