@echo off
echo ============================================
echo   CCNSA - Starting Server
echo ============================================
echo.

cd /d "%~dp0"

echo Checking port 8000...
netstat -ano | findstr ":8000" | findstr "LISTENING" >nul 2>&1
if %errorlevel%==0 (
    echo.
    echo Server is already running on port 8000.
    echo Opening browser...
    start http://127.0.0.1:8000
    echo.
    echo If you want to restart the server, close the existing
    echo Python process and run this script again.
    pause
    exit /b 0
)

echo Starting server on http://127.0.0.1:8000
echo Press Ctrl+C to stop the server.
echo.

start /b http://127.0.0.1:8000 2>nul
timeout /t 2 /nobreak >nul
start http://127.0.0.1:8000

python server.py
pause
