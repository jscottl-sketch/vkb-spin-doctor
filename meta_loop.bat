@echo off
cd /d "%~dp0"
echo ============================================================
echo  AAFL Meta-Loop
echo  Dry-run by default. Pass --apply to write code changes.
echo ============================================================
echo.
python meta_loop.py --once %*
echo.
pause
