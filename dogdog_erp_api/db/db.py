from dotenv import load_dotenv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# DB URL
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    # connect_args={"options": "-csearch_path=public,dog_5"},
    echo=os.getenv("SQLALCHEMY_ECHO", "").lower() in {"1", "true", "yes", "on"},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
