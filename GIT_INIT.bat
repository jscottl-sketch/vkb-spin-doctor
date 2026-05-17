@echo off
cd /d "%~dp0"
echo === GIT INIT ===
echo.

if exist ".git" (
    echo Git repo already initialised in this folder.
    pause
    exit /b 0
)

git init
echo.

(
echo # Python cache
echo __pycache__/
echo *.py[cod]
echo *.pyo
echo.
echo # Environment / secrets
echo .env
echo .env.*
echo !.env.example
echo.
echo # Large model files
echo *.gguf
echo *.bin
echo *.safetensors
echo *.pt
echo *.pth
echo.
echo # Logs ^& generated files
echo health_log.json
echo session_logs/archive/
echo *.log
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
) > .gitignore

echo .gitignore written.
echo.

git add .gitignore
git commit -m "Initial commit — add .gitignore"

echo.
echo Done.  Run GIT_BACKUP.bat any time to save progress.
pause
