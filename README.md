# 🐶 똑똑! (DDOG DDOG)
> **"고객의 일상 기록이 기업의 생산 지표가 되는 통합 솔루션"**
>
> *“똑똑! 우리집 강아지가 마지막 한 알을 먹기 전에 문 앞에 사료가 도착합니다.”*

[![Tech Stack](https://img.shields.io/badge/Stack-Python_%7C_FastAPI_%7C_Flet_%7C_PostgreSQL-blue)](#)
#라이프로그 #D2C_소비기반_구독 #재고관리_최적화 #B2B_ERP_연동

---

## 🌟 프로젝트 요약 (Summary)
**똑똑!**은 보호자의 번거로운 기록을 '가치 있는 데이터'로 변환합니다. 
반려견 맞춤형 **라이프로그 앱(B2C)**을 통해 간편하게 식사를 기록하면, 시스템이 사료 소진일을 예측하여 **자동 배송(Subscription)**을 실행합니다. 이 데이터는 즉시 사료 공장의 **스마트 생산 시스템(B2B ERP)**으로 연결되어 재고 최적화와 효율적인 생산 계획을 지원합니다.

- **귀찮은 기록** → 버튼 하나로 간편하게!
- **깜박하기 쉬운 사료 주문** → 데이터 기반 예측으로 알아서 빠르게!
- **우리아이 상태 공유** → 가족 및 공동 집사와 쉽게 공유! (Ph 2 예정)

---

## 🚩 프로젝트 배경 (Background)

### 1. 펫 휴머니제이션의 가속
2027년 6조 원 규모의 성장이 전망되는 반려동물 시장에서, 반려동물을 가족으로 여기는 ‘초개인화 맞춤형 돌봄’에 대한 니즈가 급증하고 있습니다.

### 2. MZ 보호자의 페인 포인트
온라인 펫푸드 소비의 주축인 2030 가구는 바쁜 일상 속에서 사료 잔량을 체크하고 주기적으로 구매하는 것에 번거로움을 느낍니다. 특히 초보 견주는 정확한 급여량 정보 부재로 어려움을 겪습니다.

### 3. 기업의 운영 비효율
사료 제조사는 여전히 단편적인 판매량 데이터에 의존해 생산 계획을 수립하여, 재고 관리의 비효율과 폐기 비용 손실이 발생하고 있습니다.

---

## 🎯 프로젝트 목적 (Purpose)

- **고객 경험 개선:** 실시간 섭취 데이터 기반 맞춤형 급여량 계산 및 자동 배송 서비스로 편리함 제공.
- **기업 운영 효율화:** 수요 예측 모델을 통해 적정 재고를 유지하고, 원가 및 수수료 관리가 포함된 ERP 시스템으로 수익성 제고.

---

## ✨ 핵심 차별점 (Differentiation)

기존 서비스들이 기록, 정보, 구매의 여정이 파편화되어 있었다면, **똑똑!**은 이 모든 경험을 하나로 통합합니다.

1. **간편한 동적 구독:** 기계적인 주기가 아닌, 유저의 실제 ‘로깅(기록)’ 데이터를 분석해 사료가 떨어지는 날(D-3)을 예측하여 배송합니다.
2. **강력한 락인(Lock-in) 효과:** 매일 켜야 하는 라이프로그 기능을 통해 커머스 앱의 최대 과제인 재방문율을 극대화합니다.
3. **B2C-ERP 파이프라인:** 단순 쇼핑몰을 넘어 고객 데이터가 백오피스의 생산/재고 지표로 직결되는 진정한 데이터 아키텍처를 구축합니다.

---

## 🛠 주요 기능 (Key Features)

### 📱 [B2C] 똑똑! App
* **개인화 온보딩:** 견종, 생애주기, 활동량에 따른 일일 권장 칼로리 계산. (사료큐레이션-Ph 2)
* **원터치 급여 로깅:** 메인 대시보드에서 터치 한 번으로 권장량 차감 기록 및 실시간 사료 잔량 확인.
* **스마트 동적 구독:** 축적된 급여 패턴을 분석하여 예상 소진일 전 자동 결제 및 배송 지시.
* **공동 집사 관리 (Ph2):** 가족 간 실시간 기록 공유 및 소통 기능.

### 🏢 [B2B] 개밥개밥 ERP
* **재고 및 유통기한 관리:** 출고 및 잔여 재고를 실시간 트래킹하여 재고 최적화.
* **AI 수요 예측 대시보드:** 소비 데이터를 분석하여 품목별 판매 예상치를 산출, 선제적 생산 계획 수립 지원.(Ph2)

---

## 🏗 기술 스택 및 아키텍처
* **Backend:** FastAPI (Domain-Driven Design)
* **Frontend:** Flet (Python-based Framework)
* **Database:** PostgreSQL v26
* **Logic:** 백엔드 트랜잭션과 DB 트리거를 활용한 데이터 무결성 확보

---

## ⚙️ 환경 설정 및 시작 가이드 (Installation)

### 1. 저장소 복제 (Clone the repository)
```bash
git clone [https://github.com/GBGB-PROJECT/DOGDOG.git](https://github.com/GBGB-PROJECT/DOGDOG.git)
cd DOGDOG
```


### 2. 파이썬 가상환경 생성 및 활성화 (Virtual Environment)
```bash
python -m venv .venv
```
#### Windows:
```bash
.venv\Scripts\activate
```
#### Mac/Linux:
```bash
source .venv/bin/activate
```


### 3. 필수 라이브러리 설치 (Install dependencies)
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (Environment Variables)
프로젝트 실행에 필요한 보안 및 설정 정보는 `.env` 파일에서 관리합니다. 
프로젝트 루트 폴더에 `.env` 파일을 생성하고 아래 내용을 팀 환경에 맞게 수정하여 입력하세요.

> **⚠️ 주의:** `.env` 파일에는 데이터베이스 비밀번호 등 민감한 정보가 포함되므로 절대 Git에 커밋하지 마세요. (이미 `.gitignore`에 포함되어 있습니다.)

```text
# Database 설정
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD="[PASSWORD]"
DB_NAME=dogdog_db

# Auth 설정 (JWT 등)
SECRET_KEY=임의의_복잡한_문자열
```

### 5. 실행 명령어
```bash
# uvicorn을 사용하여 서버 가동 (main.py 위치 기준)
uvicorn main:app --reload

# Flet 앱 실행
flet run main.py

# Flet 브라우저 실행
flet run --web main.py
```