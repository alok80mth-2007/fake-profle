@echo off
title Fake Profile Detector
echo ===================================================
echo Starting Fake Profile Detector...
echo ===================================================
cd /d "%~dp0"

:: Check if port 5000 is in use and free it if necessary
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5000" ^| findstr "LISTENING"') do (
    echo Terminating stale process on port 5000 - PID %%a
    taskkill /F /PID %%a >nul 2>&1
)

:: Automatically open browser once server is up
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Select python executable
set "PYTHON_EXE=python"
if exist "fake-profile-detector-main\venv\Scripts\python.exe" (
    set "PYTHON_EXE=fake-profile-detector-main\venv\Scripts\python.exe"
) else if exist "venv\Scripts\python.exe" (
    set "PYTHON_EXE=venv\Scripts\python.exe"
)

echo Using Python: %PYTHON_EXE%
echo Web App will open at: http://127.0.0.1:5000
echo Press Ctrl+C in this window to stop the server.
echo ===================================================

%PYTHON_EXE% run.py

pause
