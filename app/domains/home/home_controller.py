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
