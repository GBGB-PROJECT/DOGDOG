@echo off


set PYTHONPATH=%~dp0

echo ---------------------------------------------------
echo 🚀 Flet Hot Reload
echo [Web Mode] http://localhost:34636
echo ---------------------------------------------------

start http://localhost:34636
set FLET_NO_BROWSER=1

"venv\Scripts\python.exe" -m watchfiles "venv\Scripts\python.exe erp/main.py"

pause
