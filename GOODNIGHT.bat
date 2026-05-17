@echo off
cd /d "%~dp0"
echo.
echo ==========================================
echo   GOODNIGHT  %DATE%  %TIME%
echo ==========================================
echo.

echo [Phase 1 of 2] Ending session...
call "%~dp0END_SESSION.bat"

echo.
echo [Phase 2 of 2] Overnight run...
call "%~dp0RUN_OVERNIGHT.bat"

echo.
echo ==========================================
echo   ALL DONE.  Sleep well.  %TIME%
echo ==========================================
