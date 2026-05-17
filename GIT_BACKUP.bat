@echo off
cd /d "%~dp0"
echo === GIT BACKUP ===
echo.

if not exist ".git" (
    echo No git repo found.  Run GIT_INIT.bat first.
    pause
    exit /b 1
)

:: Build timestamp  YYYY-MM-DD HH:MM:SS
for /f "tokens=1-4 delims=/ " %%a in ("%DATE%") do set D=%%c-%%b-%%a
for /f "tokens=1-3 delims=:. " %%a in ("%TIME: =0%") do set T=%%a:%%b:%%c
set STAMP=%D% %T%

git add -A
git diff --cached --quiet
if %ERRORLEVEL%==0 (
    echo Nothing new to commit.
    goto :push
)

git commit -m "Backup %STAMP%"
echo Committed: Backup %STAMP%

:push
git remote | findstr /r "." >nul 2>&1
if %ERRORLEVEL%==0 (
    echo Pushing to remote...
    git push
    if %ERRORLEVEL%==0 (
        echo Push OK.
    ) else (
        echo Push failed — check remote / credentials.
    )
) else (
    echo No remote configured — skipping push.
)

echo.
echo Backup complete.
