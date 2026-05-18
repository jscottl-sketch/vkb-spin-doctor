@echo off
if "%~1"=="" (
    echo Usage: set_goal "your goal here"
    exit /b 1
)
set "_GOAL=%~1"
powershell -NoProfile -Command "Set-Content -Path '%~dp0goal.txt' -Value $env:_GOAL -Encoding UTF8"
echo Goal set: %~1
