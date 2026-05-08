@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo ---------------------------------------------------
echo 🚀 Fast API
echo [Swagger UI] http://localhost:8000/docs
echo ---------------------------------------------------
echo start http://localhost:8000/docs
".venv\Scripts\python.exe" dogdog_app_api_py/backend/main.py
pause
