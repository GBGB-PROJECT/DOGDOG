import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# .env 파일에서 환경 변수 로드
load_dotenv()

# DATABASE_URL을 .env에서 가져옴
DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy 엔진 생성
# PostgreSQL 연결 시 커넥션 풀 및 기본 검색 경로(schema)를 설정합니다.
engine = create_engine(
    DATABASE_URL, 
    connect_args={"options": "-csearch_path=dog_5,public"}
)

# 세션 생성기 설정
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델 정의 시 사용할 기본 클래스
Base = declarative_base()

# FastAPI 의존성 주입을 위한 DB 세션 생성 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()