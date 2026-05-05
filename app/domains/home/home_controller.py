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

    def _safe_remove_session(self, keys: list):
        """세션 스토리지를 안전하게(KeyError 없이) 정리합니다."""
        storage = self.page.session.store
        for key in keys:
            if storage.contains_key(key):
                storage.remove(key)

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
                    # [해결] 404 또는 에러 응답 시 빈 객체로 안전하게 처리
                    pet_food_data = {}
                    if res_food.status_code == 200:
                        try:
                            pet_food_data = res_food.json().get("data", {})
                        except Exception:
                            pet_food_data = {}
                    
                    storage.set("pet_food_detail", pet_food_data)
                except Exception as fe:
                    print(f"[HomeController] 사료 상세 정보 동기화 중 에러: {fe}")

                # 3. 기존 세션 데이터 업데이트 (기존 customer_detail 데이터 보존)
                customer_detail = storage.get("customer_detail") or {}
                if not isinstance(customer_detail, dict):
                    customer_detail = {}
                customer_detail["dashboard_sync"] = dash_data
                storage.set("customer_detail", customer_detail)

                # 4. 실시간 UI 반영을 위한 페이지 갱신
                self.page.update()
                # for i, view in enumerate(self.page.views):
                #     if view.route == "/home":
                #         self.page.views.remove(view)
                #         print("home_view 제거 완료 (임시 해결 방안)") #사이드이펙트

                print(f"[HomeController] 대시보드 및 제품 정보 동기화 완료 (Overwritten): {pet_id}")
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

    def safe_float(self, value, default=0.0):
        """문자열이나 None 값을 안전하게 float으로 변환합니다."""
        if value is None or value == "?" or value == "None":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def get_today_record_stats(self):
        """
        오늘의 기록 상단 통계(급여량, 음수량, 산책시간) 및 목표 칼로리 진행률을 계산하여 반환합니다.
        """
        storage = self.page.session.store
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}

        feeding_stats = dash_data.get("feeding_stats") or {}
        activity_stats = dash_data.get("activity_stats") or {}

        current_amount = self.safe_float(feeding_stats.get("current_amount"))
        water_total = self.safe_float(activity_stats.get("water_total"))
        walk_total = self.safe_float(activity_stats.get("walk_total"))

        current_kcal = self.safe_float(feeding_stats.get("current_kcal"))
        target_kcal = self.safe_float(feeding_stats.get("target_kcal"))
        progress_rate = self.safe_float(feeding_stats.get("progress_rate"))

        kcal_progress_value = (
            progress_rate / 100.0 if progress_rate > 1.0 else progress_rate
        )

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
        [보정] 홈 대시보드의 사료 잔여량 데이터를 가공하여 반환합니다.
        - 분모(UI 오른쪽): 백엔드의 product_total_weight (상품 원본 규격)
        - 분자(UI 왼쪽 큰 글씨): 백엔드의 left_intake (보정된 잔여량)
        """
        storage = self.page.session.store
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}
        current_food_info = dash_data.get("current_food_info")

        # 1. 원본 데이터 추출 (기획 의도에 따른 매핑 수정)
        # product_total_weight: 상품 원본 규격 (UI 분모/규격용)
        # customer_food_total_weight: 유저가 수정한 현재 무게
        total_weight_g = self.safe_float(inventory.get("product_total_weight"))
        # left_intake: 백엔드에서 보정된 잔여량 (UI 분자용)
        left_intake = self.safe_float(inventory.get("left_intake"))
        # left_percent: 백엔드에서 계산된 진행률
        progress_rate = self.safe_float(inventory.get("left_percent"))

        # 2. 무게 단위 변환 (UI 분모용: 원본 규격 표시)
        total_weight_kg = round(total_weight_g / 1000, 1) if total_weight_g > 0 else 0.0
        
        # Flet ProgressBar용 진행률 (원본 규격 대비 잔여량)
        progress_value = progress_rate / 100.0 if progress_rate > 0 else 0.0

        # 3. 기타 정보 가공
        left_days = inventory.get("left_food_count")
        expected_exdate = inventory.get("expected_exdate")
        expected_exdate_formatted = (
            str(expected_exdate).replace("-", ".") if expected_exdate else "정보 없음"
        )

        # 사료 정보가 없는 경우 방어적 매핑
        # current_food_info가 존재해야 실제로 사료가 등록된 상태임
        is_food_registered = current_food_info is not None and isinstance(current_food_info, dict)
        product_name = "등록된 사료 없음"
        if is_food_registered:
            product_name = current_food_info.get("product_name", "사료 정보 없음")

        return {
            "product_name": product_name,
            "left_intake": left_intake,
            "total_weight_kg": total_weight_kg,
            "left_days": round(self.safe_float(left_days), 1) if left_days not in [None, "?", "None"] else "?",
            "progress_value": progress_value,
            "expected_exdate_formatted": expected_exdate_formatted,
            "is_food_registered": is_food_registered
        }

    async def get_feeding_detail_data(self):
        """
        [리팩터링] 급여 상세 페이지를 위한 데이터 Fetch 로직
        """
        storage = self.page.session.store

        pet_id = (
            storage.get("pet_id")
            or storage.get("customer_pet_id")
            or storage.get("current_pet_id")
        )

        if pet_id:
            await self.fetch_dashboard_data(pet_id)
        
        customer_detail = storage.get("customer_detail") or {}
        dash_data = customer_detail.get("dashboard_sync") or {}
        inventory = dash_data.get("food_inventory") or {}
        pet_food_detail = storage.get("pet_food_detail") or {}
        current_food_info = dash_data.get("current_food_info")

        # 데이터 병합 (최신 API 필드 누락 방지)
        feeding_data = {**pet_food_detail, **inventory}
        if current_food_info and isinstance(current_food_info, dict):
            feeding_data.update(current_food_info)
        
        # [해결] 사료 정보(current_food_info)가 없으면 세션 안전하게 비우고 None 반환
        is_food_registered = current_food_info is not None and isinstance(current_food_info, dict)
        if not is_food_registered:
            self._safe_remove_session(["select_feeding_data", "select_customer_food_id"])
            return None

        try:
            # 백엔드에서 보정된 left_intake 우선 사용
            left_intake = self.safe_float(
                feeding_data.get("left_intake")
                or feeding_data.get("left_weight")
                or feeding_data.get("amount")
            )
            # 분모(규격)는 무조건 상품 원본 규격인 product_total_weight 참조
            total_weight_g = self.safe_float(
                feeding_data.get("product_total_weight")
                or feeding_data.get("total_weight")
                or feeding_data.get("product_weight")
            )
            total_weight_kg = round(total_weight_g / 1000, 1) if total_weight_g > 0 else 0.0

            # 백엔드에서 계산된 진행률 사용
            left_percent = self.safe_float(
                feeding_data.get("left_percent") or feeding_data.get("percent")
            )
            progress_value = left_percent / 100.0 if left_percent > 0 else 0.0

            left_days = (
                feeding_data.get("left_food_count")
                or feeding_data.get("expected_left_days")
                or feeding_data.get("left_days")
            )
            expected_exdate = (
                feeding_data.get("expected_exdate")
                or feeding_data.get("expected_last_day")
                or feeding_data.get("last_date")
            )
            expected_exdate_formatted = (
                str(expected_exdate).replace("-", ".") if expected_exdate else "정보 없음"
            )

            brand = (
                feeding_data.get("product_brand")
                or feeding_data.get("brand_name")
                or feeding_data.get("brand")
                or "정보 없음"
            )
            product_name = feeding_data.get("product_name") or "알 수 없는 상품"
            
            thumbnail = (
                feeding_data.get("product_thumbnail")
                or feeding_data.get("thumbnail")
                or feeding_data.get("image_url")
                or "food_default.png"
            )

            feeding_start = current_food_info.get("feeding_start") if current_food_info else None
            
            result_data = {
                "raw_data": feeding_data,
                "left_intake": left_intake,
                "total_weight_kg": total_weight_kg,
                "left_days": round(self.safe_float(left_days), 1) if left_days not in [None, "?", "None"] else "?",
                "progress_value": progress_value,
                "expected_exdate_formatted": expected_exdate_formatted,
                "brand": brand,
                "product_name": product_name,
                "thumbnail": thumbnail,
                "feeding_start": feeding_start # [Step 1] 급여 시작일 추가
            }

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
