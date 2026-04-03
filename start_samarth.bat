@echo off
title Samarth AI Project Runner
echo ===================================================
echo   Starting Samarth AI Project Services...
echo ===================================================

echo Starting Python Backend Server...
start /b "Samarth Backend" cmd /c "call .venv\Scripts\activate && python -m uvicorn backend.main:app --reload"

:: Wait a brief moment before starting frontend
timeout /t 2 /nobreak > nul

echo Starting Next.js Frontend...
start /b "Samarth Frontend" cmd /c "cd frontend && npm run dev"

:: Wait a few seconds for the Next.js server to initialize
timeout /t 5 /nobreak > nul

echo Opening Web Browser...
start http://localhost:3000

echo.
echo ===================================================
echo All services have been launched in THIS single window!
echo - Frontend: http://localhost:3000
echo - Backend:  http://localhost:8000
echo ===================================================
echo DO NOT CLOSE THIS WINDOW.
echo If you close this window, the servers will shut down.
echo (Or press Ctrl+C to terminate)
echo.
pause
