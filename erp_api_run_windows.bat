@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONPATH=%~dp0
echo ---------------------------------------------------
echo 🚀 Fast API
echo [Swagger UI] http://localhost:8001/docs
echo ---------------------------------------------------
start http://localhost:8001/docs
".venv\Scripts\python.exe" -m watchfiles ".venv\Scripts\python.exe dogdog_erp_api_py/backend/main.py" dogdog_erp_api_py
pause