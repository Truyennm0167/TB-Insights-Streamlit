@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    echo Virtual environment not found. Run run_windows.bat first.
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade -r requirements.txt
pause
