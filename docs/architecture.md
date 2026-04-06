# 🏗️ DOGDOG 아키텍처 가이드

## 🌐 서버 구조
- **언어 및 프레임워크**: Python 3.10+ & FastAPI
- **데이터베이스 (DB)**: PostgreSQL (v15+)
  - **파티셔닝**: `pet_food` 테이블은 `feeding_date` (날짜)를 기준으로 파티셔닝됩니다.
- **ORM**: SQLAlchemy

## 📁 디렉토리 구조 (Backend)
도메인 중심의 계층형 아키텍처를 따릅니다.
```
backend/
└── app/
    ├── main.py        # 엔트리 포인트
    ├── db.py          # 데이터베이스 연결 및 설정
    └── domains/       # 도메인 기반 모듈
        └── logs/      # 로그 도메인 (Feeding Log, Intake 등)
            ├── api/   # API 라우터 (FastAPI Endpoint)
            ├── service/  # 비즈니스 로직
            ├── repository/ # 데이터 접근 계층 (SQLAlchemy)
            └── models.py # SQLAlchemy 모델 (Entity)
```

## 🔐 보안 및 인증
- **JWT (Json Web Token)**: `Authorization` 헤더의 `Bearer {token}`에서 `customer_id`를 추출합니다.

## ⚙️ 주요 설계 원칙
- **트랜잭션 관리**: 급여 기록 (`pet_food`) 등록과 재고 (`customer_food`) 업데이트는 반드시 한 트랜잭션으로 처리합니다.
- **칼로리 자동 계산**: 사료 1g당 열량 정보를 기반으로 서버에서 자동 계산합니다.
- **재고 데이터 신뢰성**: 모든 급여 작업은 `customer_food` 테이블의 누적량 (`total_intake`)과 잔량 (`left_intake`)을 즉각 반영해야 합니다.
