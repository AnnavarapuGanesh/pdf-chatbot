@echo off
title PDF QA Chatbot - Backend Server (FastAPI)
echo ============================================================
echo Starting PDF QA Chatbot Backend Server...
echo ============================================================

cd /d "%~dp0backend"

:: Start Ollama if not already running
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting Ollama background service...
    start "" ollama serve
    timeout /t 2 /nobreak >NUL
)

echo Starting FastAPI server at http://localhost:8000 ...
py -3.10 -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
