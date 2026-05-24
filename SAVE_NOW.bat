@echo off
cd /d "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor"
if not exist chat_latest.txt (
    echo Auto-save %date% — no chat summary provided > chat_latest.txt
    echo [SAVE_NOW] Created minimal chat_latest.txt
)
echo [SAVE_NOW] Running aafl_wccs.py...
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe aafl_wccs.py
echo.
echo [SAVE_NOW] DONE.
pause
