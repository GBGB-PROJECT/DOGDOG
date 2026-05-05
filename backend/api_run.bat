@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHONPATH=%~dp0

echo ---------------------------------------------------
echo 🚀 Fast API Load
echo ---------------------------------------------------

"C:\Lustiora\DOGDOG\.venv\Scripts\python.exe" -m watchfiles "C:\Lustiora\DOGDOG\.venv\Scripts\python.exe main.py"

pause
