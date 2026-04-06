# 🎨 DOGDOG 코딩 컨벤션

## 🐍 Python 스타일 (PEP 8+)
- **들여쓰기**: 공백 4칸
- **네이밍**:
  - `class`: CamelCase (예: `FeedingLog`)
  - `function`, `variable`: lower_case_with_underscores (예: `calculate_calories`)
  - `constant`: UPPER_CASE_WITH_UNDERSCORES (예: `MAX_MEMO_LENGTH`)
- **타입 힌트**: 모든 함수 인자와 반환 타입에 명시 (예: `def save_log(log: FeedingLog) -> bool:`)

## 📝 Docstrings (Google 스타일)
모든 주요 기능과 클래스에 `docstring`을 포함합니다.
```python
def create_feeding_log(pet_id: int, amount: int) -> dict:
    """새로운 급여 기록을 생성하고 재고 정보를 업데이트합니다.

    Args:
        pet_id: 대상 반려견 ID
        amount: 급여량 (g)

    Returns:
        성공 시 저장된 로그와 재고 정보를 포함한 딕셔너리
    """
```

## 📦 폴더 구조 컨벤션
도메인별로 `api`, `service`, `repository` 폴더를 엄격히 분리하여 사용합니다.
- `api/`: FastAPI `APIRouter` 객체를 관리하고 스키마 (Request/Response 모델)를 정의합니다.
- `service/`: 비즈니스 로직을 집약하며, 여러 리포지토리/서비스 간 조율을 수행합니다.
- `repository/`: SQLAlchemy를 통해 데이터베이스에 직접 접근하는 레이어입니다.

## 🚀 워크플로우 규칙
- **TDD (Test Driven Development)**: 가능한 경우 테스트 코드를 먼저 작성하거나, 작성 후 즉시 검증합니다.
- **오케스트레이터 규칙**: 모든 코드 변경은 `Generator`가 수행하며, `Planner`의 실행 계획에 기반합니다.
