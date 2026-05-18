@echo off
cd /d "%~dp0"
echo ============================================================
echo  AAFL Full Launch
echo ============================================================

:: ── Step 1: Start LM Studio if not already listening ─────────────────────────
echo [1/4] Checking LM Studio (127.0.0.1:1234)...
powershell -NoProfile -Command "try { $t = New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',1234); $t.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
if errorlevel 1 (
    echo        Not running -- launching LM Studio...
    start "" "%LOCALAPPDATA%\Programs\LM Studio\LM Studio.exe"
) else (
    echo        Already running.
    goto :wait_done
)

:: ── Step 2: Wait for port 1234 to respond (90 s timeout) ─────────────────────
echo [2/4] Waiting for LM Studio to load (up to 90 s)...
set /a _tries=0
:wait_loop
    set /a _tries+=1
    if %_tries% gtr 45 (
        echo        TIMEOUT -- LM Studio did not respond after 90 s. Continuing anyway.
        goto :wait_done
    )
    powershell -NoProfile -Command "Start-Sleep -Milliseconds 2000" >nul 2>&1
    powershell -NoProfile -Command "try { $t = New-Object Net.Sockets.TcpClient; $t.Connect('127.0.0.1',1234); $t.Close(); exit 0 } catch { exit 1 }" >nul 2>&1
    if errorlevel 1 goto :wait_loop
    echo        LM Studio ready (attempt %_tries%).

:wait_done

:: ── Step 3: Pre-flight health check ──────────────────────────────────────────
echo [3/4] Running pre-flight check...
call "%~dp0aafl_doctor.bat"

:: ── Step 4: Run the goal queue ────────────────────────────────────────────────
echo [4/4] Starting queue runner...
call "%~dp0queue_runner.bat"

:: ── Step 5: Update Central Command dashboard data ──────────────────────────
echo [5/5] Updating dashboard data...
"C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe" "%~dp0dashboard_builder.py"

echo.
echo ============================================================
echo  AAFL run complete.
echo ============================================================
pause
