@echo off
echo === STOP LM STUDIO ===
echo.

tasklist /FI "IMAGENAME eq LM Studio.exe" 2>nul | find /I "LM Studio.exe" >nul
if %ERRORLEVEL%==0 (
    taskkill /IM "LM Studio.exe" /F
    if %ERRORLEVEL%==0 (
        echo LM Studio stopped.
    ) else (
        echo WARNING: taskkill failed — process may still be running.
    )
) else (
    echo LM Studio was not running.
)
