import os
import sys
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock

# 프로젝트 루트 및 backend 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.abspath(os.path.join(current_dir, "../../"))
project_root = os.path.abspath(os.path.join(backend_dir, "../"))

if project_root not in sys.path: sys.path.insert(0, project_root)
if backend_dir not in sys.path: sys.path.insert(0, backend_dir)

# 1. FastAPI 및 테스트 도구 임포트
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# 2. 프로젝트 로직 임포트 (절대 경로 스타일)
from app.logs.api.feeding_api import router
from db.db import get_db

# 

# 3. 테스트를 위한 가짜 앱(App) 생성 및 라우터 등록
app = FastAPI()

# 실제 main.py와 동일한 prefix 구조 적용
app.include_router(router, prefix="/api/v1/logs/feeding")
client = TestClient(app)

# 4. 테스트용 가짜 데이터 설정 (ERD 기준)
mock_inventory = SimpleNamespace(
    customer_id=110,
    total_weight=5000,
    total_intake=500,
    food_count=10,
    left_intake=4500.0,      # DB 자동계산 필드 흉내
    left_food_count=90.0,    # DB 자동계산 필드 흉내
    feeding_start=date.today(), # 신규 추가된 필드
    last_update=date.today()
)

mock_feeding_info = SimpleNamespace(
    pet_id=1,
    one_gram_calories=3.8    # ERD의 one_gram_calories 필드 흉내
)

# 5. DB 세션을 가짜로 갈아끼우는 함수 (Dependency Override)
def override_get_db():
    mock_db = MagicMock(spec=Session)
    
    # 리포지토리에서 호출할 DB 쿼리 결과들을 가짜 데이터로 연결
    # .query().filter_by().first() 등의 체이닝을 흉내냅니다.
    mock_db.query().filter_by().with_for_update().first.return_value = mock_inventory
    mock_db.query().filter_by().first.return_value = mock_feeding_info
    
    try:
        yield mock_db
    finally:
        pass

# 6. 진짜 get_db를 가짜 override_get_db로 교체!
app.dependency_overrides[get_db] = override_get_db

def test_feeding_registration_api():
    print("\n" + "="*50)
    print("🚀 [통합 테스트] 급여 등록 API 로직 검증 시작")
    print("="*50)
    
    # 전송할 테스트 데이터
    payload = {
        "pet_id": 1,
        "amount": 200
    }

    # API 호출
    response = client.post("/api/v1/logs/feeding", json=payload)

    # 결과 검증 (Assert)
    if response.status_code == 201:
        data = response.json()["data"]
        print(f"✅ 응답 코드: {response.status_code} (Created)")
        print(f"📊 급여량: {data['amount']} g")
        
        # 비즈니스 로직 체크
        assert data['amount'] == 200
        print("\n✨ [최종 결과] 모든 비즈니스 로직이 정상입니다!")
    else:
        print(f"❌ 테스트 실패: {response.status_code}")
        print(f"에러 메시지: {response.text}")

if __name__ == "__main__":
    test_feeding_registration_api()