@echo off
echo ===================================================
echo Stopping Fake Profile Detector (Port 5000)...
echo ===================================================

setlocal enabledelayedexpansion
set "FOUND=0"

for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    set "FOUND=1"
    echo Terminating process PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)

if "!FOUND!"=="1" (
    echo [OK] Fake Profile Detector has been stopped.
) else (
    echo [INFO] No server was running on port 5000.
)

pause
