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

# 이제 db.db와 app.logs...를 정상적으로 임포트할 수 있습니다.
from app.logs.api.feeding_api import router as feeding_router

app = FastAPI(
    title="DOGDOG API",
    description="반려견 급여 및 사료 관리 서비스를 위한 API",
    version="1.0.0"
)

# CORS 설정 (모든 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(feeding_router, prefix="/api/v1/feeding")

@app.get("/")
def read_root():
    return {"message": "DOGDOG 백엔드 서버가 정상 작동 중입니다.", "schema": "Companion"}

if __name__ == "__main__":
    import uvicorn
    # 실행 시 모듈 경로는 현재 파일(main) 기준입니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
