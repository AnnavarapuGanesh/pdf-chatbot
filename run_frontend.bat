@echo off
title PDF QA Chatbot - Frontend Server (React + Vite)
echo ============================================================
echo Starting PDF QA Chatbot Frontend Server...
echo ============================================================

cd /d "%~dp0frontend"
echo Starting Vite Dev Server at http://localhost:5173 ...
npm run dev -- --host 127.0.0.1
pause
