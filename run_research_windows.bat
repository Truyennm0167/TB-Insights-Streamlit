@echo off
setlocal
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo [TB Insights] Creating virtual environment...
    py -3.11 -m venv .venv
    if errorlevel 1 exit /b 1
)
call .venv\Scripts\activate.bat

echo [TB Insights] Installing research dependencies...
python -m pip install -r requirements-research.txt
if errorlevel 1 (
    echo Research dependency installation failed.
    pause
    exit /b 1
)

echo [TB Insights] Rebuilding clean data and EDA outputs...
python src\run_eda.py
if errorlevel 1 exit /b 1

echo [TB Insights] Re-running K-means experiments...
python src\run_kmeans.py
if errorlevel 1 exit /b 1

echo [TB Insights] Validating outputs...
python scripts\validate_data.py
python -m unittest discover -s tests -v
pause
