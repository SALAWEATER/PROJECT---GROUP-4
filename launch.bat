@echo off
SETLOCAL

:: 1. Set project root path
set "PROJECT_ROOT=%~dp0"
set "PYTHON_EXEC=python"

:: 2. Start backend in new window
start "MentalHealth Backend" cmd /k "%PYTHON_EXEC% -m uvicorn mentalhealth_app.business.app:app --reload --app-dir "%PROJECT_ROOT%mentalhealth_app""

:: 3. Wait for backend to initialize
timeout /t 5 /nobreak >nul

:: 4. Start frontend in new window
start "MentalHealth Frontend" cmd /k "%PYTHON_EXEC% "%PROJECT_ROOT%mentalhealth_app\presentation\frontend.py""

:: 5. Keep main window open
echo Application launched in separate windows
pause