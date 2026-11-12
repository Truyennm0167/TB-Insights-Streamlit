@echo off
setlocal
cd /d "%~dp0"

if not exist .venv\Scripts\python.exe (
    echo [TB Insights] Creating virtual environment...
    py -3.11 -m venv .venv
    if errorlevel 1 (
        echo Could not create Python 3.11 environment. Check that Python 3.11 is installed.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate.bat
python -c "import streamlit, pandas, numpy, plotly" >nul 2>&1
if errorlevel 1 (
    echo [TB Insights] Installing required packages...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Package installation failed. Check your internet connection and try again.
        pause
        exit /b 1
    )
)

python -m streamlit run streamlit_app.py
