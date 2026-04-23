import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# backend/main.py 상단
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../backend
project_root = os.path.abspath(os.path.join(current_dir, "../")) # .../dogdog-project (부모 폴더)

# 이 project_root가 sys.path의 0번(최우선) 순위로 잘 들어가 있어야 합니다.
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# [2] 라우터 임포트 (건형님의 파일명에 맞게 조정했습니다)
try:
    from backend.erp.auth.api.erp_signinup_api import router as auth_router
except ImportError:
    # 혹시 폴더 구조가 다를 경우를 대비해 erp를 뺀 경로도 시도합니다.
    from backend.erp.auth.api.erp_signinup_api import router as auth_router

# [3] FastAPI 앱 초기화
app = FastAPI(
    title="개밥개밥 ERP API",
    description="사원 관리 및 인증 시스템을 위한 백엔드 서버",
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

# [5] 라우터 등록
app.include_router(auth_router)

# [6] 서버 정상 작동 확인용 엔드포인트
@app.get("/")
def read_root():
    return {
        "message": "개밥개밥 ERP 백엔드 서버가 정상 작동 중입니다.",
        "status": "online"
    }

# [7] 실행 블록: 터미널에서 python main.py 로 직접 실행 가능하게 합니다.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)