@echo off
cd /d "%~dp0"
echo ============================================================
echo  AAFL Regression Test
echo ============================================================
powershell -NoProfile -Command "Set-Content -Path '%~dp0goal.txt' -Value 'Confirm the AAFL loop is operational and at least one LLM provider responds' -Encoding UTF8"
echo [TEST] Goal set. Running loop_manager.py --once ...
python loop_manager.py --once
if errorlevel 1 (
    echo.
    echo [RESULT] FAIL -- loop_manager.py exited with an error.
    exit /b 1
) else (
    echo.
    echo [RESULT] PASS -- loop_manager.py completed without error.
)
