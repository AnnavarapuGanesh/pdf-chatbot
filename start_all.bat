@echo off
title PDF QA Chatbot - Launcher
echo ============================================================
echo Starting PDF QA Chatbot (Backend + Frontend + Ollama)
echo ============================================================

cd /d "%~dp0"

echo Launching Backend server in new window...
start "PDF QA Backend" cmd /k "run_backend.bat"

timeout /t 3 /nobreak >NUL

echo Launching Frontend server in new window...
start "PDF QA Frontend" cmd /k "run_frontend.bat"

timeout /t 3 /nobreak >NUL

echo Opening application in default browser...
start http://localhost:5173

echo ============================================================
echo PDF QA Chatbot is now running!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://localhost:8000/docs
echo ============================================================
