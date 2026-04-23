from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.calc_feeding.calc_feeding_api import router as cal_feeding_router

# Domain Routers
from app.pets.api.pets_api import router as pets_router
from app.users.users_api import router as users_router
from app.auth.api.auth_api import router as auth_router
from app.logs.api.poop_api import router as poop_router
from app.home.api.dashboard_api import router as dashboard_router
from app.logs.api.logs_api import router as logs_router
from app.logs.api.weight_bcs_api import router as weight_bcs_router
from app.logs.api.feeding_api import router as feeding_router

app = FastAPI(
    title="DOGDOG API",
    description="반려견 일상 기록 및 사료 관리 서비스를 위한 API",
    version="1.0.0",
)

# CORS 보안 설정 강화 (운영 환경 및 개발 환경 허용 도메인 명시)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://dogdog-production-domain.com",  # 추후 실 배포 도메인으로 변경 예정
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
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

# 1. Auth & Users 도메인
app.include_router(auth_router)
app.include_router(users_router)

# 2. Pets 도메인
app.include_router(pets_router)

# 3. Logs & Dashboard 도메인
app.include_router(dashboard_router)
app.include_router(logs_router)
app.include_router(feeding_router)
app.include_router(poop_router)
app.include_router(weight_bcs_router)


if __name__ == "__main__":
    import uvicorn

    """
    ========================================================================
    [실행 가이드]
    - DB 폴더 및 서버 파일들이 backend/ 안으로 일원화되었습니다.
    - 터미널(터미널 창)을 열고, 최상위 루트가 아닌 반드시 'backend/' 폴더 경로로 이동(cd)한 후 
    - 아래 명령어를 통해 서버를 실행해주세요.
    
    실행 명령어: uvicorn main:app --reload
    ========================================================================
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
