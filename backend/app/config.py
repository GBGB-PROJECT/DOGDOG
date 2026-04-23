import os
from dotenv import load_dotenv

# .env 파일을 불러옵니다
load_dotenv()

# JWT Security Settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# 환경 변수는 항상 문자열로 불러와지므로, int()로 명시적 형변환을 합니다
JWT_ACCESS_EXPIRE_MINUTES = int(
    os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "120").strip('"')
)
JWT_REFRESH_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "14").strip('"'))
