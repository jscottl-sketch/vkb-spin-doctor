@echo off
echo === START LM STUDIO ===
echo.

:: Try default install locations
set LMS_EXE=%LOCALAPPDATA%\Programs\LM Studio\LM Studio.exe
if not exist "%LMS_EXE%" set LMS_EXE=%APPDATA%\LM Studio\LM Studio.exe
if not exist "%LMS_EXE%" (
    echo ERROR: LM Studio not found.  Edit the LMS_EXE path in START_LMSTUDIO.bat.
    exit /b 1
)

echo Starting LM Studio...
start "" "%LMS_EXE%"

echo Waiting for local server on port 1234 (max 120 s)...
set ATTEMPTS=0

:wait_loop
set /a ATTEMPTS+=1
if %ATTEMPTS% GTR 60 (
    echo TIMEOUT — server did not start within 120 seconds.
    exit /b 1
)
timeout /t 2 /nobreak >nul
curl -s --max-time 2 http://localhost:1234/v1/models >nul 2>&1
if %ERRORLEVEL%==0 (
    echo LM Studio server ready  ^(poll %ATTEMPTS%^).
    exit /b 0
)
goto :wait_loop
