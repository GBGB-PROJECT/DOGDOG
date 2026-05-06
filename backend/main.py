import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 프로젝트 루트 디렉토리를 sys.path에 추가하여 db 패키지를 찾을 수 있게 합니다.
# 현재 파일 위치: backend/main.py -> 부모가 프로젝트 루트
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# backend 폴더 자체도 path에 추가하여 app.logs... 임포트가 가능하게 합니다.
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import backend.app as backend

app = FastAPI(
    title="DOGDOG API",
    description="반려견 일상 기록 및 사료 관리 서비스를 위한 API",
    version="1.0.0",
)

# CORS 설정 (모든 허용)
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
    }


# ----------------------------------------------------
# API Router 중앙화 및 버저닝 계층화 (API V1)
# ----------------------------------------------------
# (참고: 각 라우터 파일에 /api/v1 접두사가 포함되어 있으므로 이곳에서 이중으로 주입할 필요 없이 논리적 계층별로 결합합니다)

# 1. Auth & Users 도메인
app.include_router(backend.auth_router)
app.include_router(backend.users_router)

# 2. Pets 도메인
app.include_router(backend.pets_router)

# 3. Onboarding 도메인
app.include_router(backend.onboarding_router)

# 4. Logs & Dashboard 도메인
app.include_router(backend.dashboard_router)
app.include_router(backend.logs_router)
app.include_router(backend.feeding_router)
app.include_router(backend.numeric_router)

# 5. calc_feeding 도메인
app.include_router(backend.calc_feeding_router)

# 6. Products 도메인
app.include_router(backend.products_router)

# 7. Notifications 도메인
app.include_router(backend.notifications_router)

# 8. Subscriptions 도메인
app.include_router(backend.subscriptions_router)

# 0. 이미지 프록시
app.include_router(backend.images_router)


if __name__ == "__main__":
    import uvicorn

    """
    ========================================================================
    [실행 가이드]
    - DB 폴더 및 서버 파일들이 backend/ 안으로 일원화되었습니다.
    - 터미널(터미널 창)을 열고, 최상위 루트가 아닌 반드시 'backend/' 폴더 경로로 이동(cd)한 후 
    - 아래 명령어를 통해 서버를 실행해주세요.
    
    실행 명령어: uvicorn main:app --reload
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
    ========================================================================
    """
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
