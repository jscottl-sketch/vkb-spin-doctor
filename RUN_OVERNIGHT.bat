@echo off
cd /d "%~dp0"
set PYTHON=C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe
echo.
echo ==========================================
echo   RUN OVERNIGHT  %DATE%  %TIME%
echo ==========================================
echo.

echo [1/5] Starting LM Studio...
call "%~dp0START_LMSTUDIO.bat"
if %ERRORLEVEL% NEQ 0 echo WARNING: LM Studio failed to start — continuing anyway.

echo.
echo [2/5] Health check...
"%PYTHON%" "%~dp0health_check.py"
if %ERRORLEVEL% NEQ 0 echo WARNING: health_check.py exited with errors.

echo.
echo [3/5] Loop manager...
"%PYTHON%" "%~dp0loop_manager.py"
if %ERRORLEVEL% NEQ 0 echo WARNING: loop_manager.py exited with errors.

echo.
echo [4/5] Stopping LM Studio...
call "%~dp0STOP_LMSTUDIO.bat"

echo.
echo [5/5] Archiving old logs...
"%PYTHON%" "%~dp0archive_logs.py"
if %ERRORLEVEL% NEQ 0 echo WARNING: archive_logs.py exited with errors.

echo.
echo ==========================================
echo   RUN OVERNIGHT COMPLETE  %TIME%
echo ==========================================
