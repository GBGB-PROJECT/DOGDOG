import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# backend 폴더 자체도 path에 추가하여 app.logs... 임포트가 가능하게 합니다.
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)
    
import backend.erp as erp


app = FastAPI(
    title="DOGDOG API",
    description="반려견 일상 기록 및 사료 관리 서비스를 위한 API",
    version="1.0.0",
)

# [4] CORS 설정: 프론트엔드(Flet 등)와의 원활한 통신을 위해 모든 접속을 허용합니다.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------
# Health Check 및 Root 엔드포인트
# ----------------------------------------------------
@app.get("/health", tags=["System"])
def health_check():
    """도커 및 로드밸런서의 상태 확인 엔드포인트입니다."""
    return {"status": "ok"}


@app.get("/", tags=["System"])
def read_root():
    return {
        "message": "DOGDOG 백엔드 서버가 정상 작동 중입니다.",
        "schema": "Companion",
    }


# ----------------------------------------------------
# API Router 중앙화 및 버저닝 계층화 (API V1)
# ----------------------------------------------------
# (참고: 각 라우터 파일에 /api/v1 접두사가 포함되어 있으므로 이곳에서 이중으로 주입할 필요 없이 논리적 계층별로 결합합니다)

# 1. erp_employee(auth), home 도메인
app.include_router(erp.erp_employee_router)
app.include_router(erp.erp_home_router)
app.include_router(erp.erp_home_inventory_router)
app.include_router(erp.erp_home_chart_router)

# 🔥🔥🔥 추가: ERP 상품 상세 정보 관리 라우터 등록
app.include_router(erp.erp_merchandise_router)

# 🔥🔥🔥 추가: ERP 고객관리 라우터 등록
app.include_router(erp.erp_customer_router)

# 🔥 추가: 고객 주문 관리 API 등록
app.include_router(erp.customer_order_router)

app.include_router(erp.customer_subscription_router)  # 🔥 추가

app.include_router(erp.erp_supplier_router)  # 🔥 추가: 거래처 관리 API 등록
app.include_router(erp.erp_hr_router)
app.include_router(erp.erp_inbound_router)  # 🔥 추가: 생산입고 API 등록
app.include_router(erp.erp_stock_router)  # 🔥 추가: 상품별 재고 상세 API 등록
app.include_router(erp.erp_purchase_order_router)  # 🔥 추가: 발주관리 API 등록
app.include_router(erp.erp_production_dashboard_router)

app.include_router(erp.stock_dashboard_router)
app.include_router(erp.stock_inout_router)

app.include_router(erp.erp_defective_router)  # 🔥 추가: 불량현황조회 API 등록

# [7] 실행 블록: 터미널에서 python main.py 로 직접 실행 가능하게 합니다.
if __name__ == "__main__":
    import uvicorn

    """
    ========================================================================
    [실행 가이드]
    - DB 폴더 및 서버 파일들이 backend/ 안으로 일원화되었습니다.
    - 터미널(터미널 창)을 열고, 최상위 루트가 아닌 반드시 'backend/' 폴더 경로로 이동(cd)한 후 
    - 아래 명령어를 통해 서버를 실행해주세요.
    
    실행 명령어: uvicorn main:app --host 0.0.0.0 --port 8001 --reload
    ========================================================================
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
