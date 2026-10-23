@echo off
title CreditRisk AI - Explainable Credit Delinquency Prediction
echo ========================================================
echo Starting CreditRisk AI Banking Analytics Suite...
echo ========================================================

cd /d "%~dp0"
if exist .venv\Scripts\streamlit.exe (
    echo Activating local virtual environment and launching dashboard...
    .\.venv\Scripts\streamlit.exe run app.py --server.port 8501 --server.headless false
) else (
    echo Python virtual environment not found in .venv. Trying system streamlit...
    streamlit run app.py --server.port 8501
)
pause
