; SAVE SESSION HOTKEY
; Press Ctrl+Shift+S from anywhere to launch Session Saver.
;
; What it does:
;   - Prompts you to Ctrl+A, Ctrl+C your Claude chat
;   - Saves the chat to chat_logs/
;   - Sends it to Claude Haiku API and generates a handover summary (~1 penny)
;   - Saves handover/LATEST_HANDOVER.md and a timestamped session log
;   - Opens your Claude project upload page with the file path ready to paste
;
; HOW TO ACTIVATE:
;   Double-click this file once — it sits in your system tray.
;   Then press Ctrl+Shift+S at the end of any session.
;
; REQUIRES: AutoHotkey installed (free at autohotkey.com)

#Requires AutoHotkey v2.0
#SingleInstance Force
SetWorkingDir A_ScriptDir

^+s:: Run "SAVE_SESSION_NOW.bat", A_ScriptDir
