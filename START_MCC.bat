@echo off
REM START_MCC.bat -- Start MCC Server + Open Mission Control in Chrome
REM Run this from anywhere. Starts mcc_server.py if not already running.

set "PYTHON=C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe"
set "PROJECT=C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor"
set "HTML=C:\Users\jscot\Desktop\mission_control.html"
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"

echo [WCCS] VKB Spin Doctor -- Mission Control Center
echo.

REM Check if something is already listening on port 8080
netstat -an 2>nul | findstr ":8080" | findstr "LISTENING" >nul 2>&1
if %errorlevel% equ 0 (
    echo [WCCS] MCC Server already running on port 8080.
) else (
    echo [WCCS] Starting MCC Server in background...
    start "MCC Server" /MIN "%PYTHON%" "%PROJECT%\mcc_server.py"
    timeout /t 2 /nobreak >nul
    echo [WCCS] MCC Server started.
)

echo.
echo [WCCS] Opening Mission Control...
if exist "%CHROME%" (
    start "" "%CHROME%" "%HTML%"
) else (
    start "" "%HTML%"
)

echo [WCCS] Done.
echo [WCCS] Server: http://localhost:8080
echo [WCCS] WCCS tab in MCC: capture notes, then Save ^& Run WCCS.
echo.
