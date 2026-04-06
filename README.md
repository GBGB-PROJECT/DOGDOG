# DOGDOG

# 환경설정
# 1. 저장소 복제 (Clone the repository)
git clone https://github.com/GBGB-PROJECT/DOGDOG.git
cd your-repo-name

# 2. 파이썬 가상환경 생성 및 활성화 (Virtual Environment)
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac:
source venv/bin/activate

# 3. 필수 라이브러리 설치 (Install dependencies)
pip install -r requirements.txt

# 실행 명령어
# uvicorn을 사용하여 서버 가동 (main.py 위치 기준)
uvicorn main:app --reload

# Flet 앱 실행
flet run main.py

# Flet 브라우저 실행
flet run --web main.py
