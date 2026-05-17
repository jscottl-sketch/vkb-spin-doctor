@echo off
cd /d "%~dp0"
set PYTHON=C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe
echo.
echo ==========================================
echo   END SESSION  %DATE%  %TIME%
echo ==========================================
echo.

echo [1/3] Running RUN_WCCS.bat...
if exist "%~dp0RUN_WCCS.bat" (
    call "%~dp0RUN_WCCS.bat"
    if %ERRORLEVEL% NEQ 0 echo WARNING: RUN_WCCS.bat exited with errors.
) else (
    echo RUN_WCCS.bat not found — skipping.
)

echo.
echo [2/3] Git backup...
call "%~dp0GIT_BACKUP.bat"
if %ERRORLEVEL% NEQ 0 echo WARNING: GIT_BACKUP.bat exited with errors.

echo.
echo [3/3] Archiving old logs...
"%PYTHON%" "%~dp0archive_logs.py"
if %ERRORLEVEL% NEQ 0 echo WARNING: archive_logs.py exited with errors.

echo.
echo ==========================================
echo   END SESSION COMPLETE  %TIME%
echo ==========================================
