@echo off
echo ============================================
echo   Updating wccs-generator skill
echo ============================================
echo.

set SKILL_DIR=C:\Users\jscot\Downloads\files claude-skilllsx2\wccs-generator
set ZIP_OUT=C:\Users\jscot\Downloads\files claude-skilllsx2\wccs-generator-UPDATED.zip

REM Write the new SKILL.md
(
echo ---
echo name: wccs-generator
echo description: Generate the ready-to-paste Claude Code ^(CLAC^) instruction block for end-of-session handover saving. Use this skill immediately whenever the user types "WCCS" - no other output, no chat, just the block. Also trigger on "write the save block", "generate the CLAC save", "end of session save".
echo ---
echo.
echo # WCCS Generator Skill
echo.
echo When triggered, output ONLY this block inside triple backticks. No preamble. No chat. No explanation.
echo.
echo ## The block to output
echo.
echo Read chat_latest.txt in this folder. Read the latest handover .md file and note its version number. Then do ALL of the following in order:
echo 1. Create a NEW handover file with version number incremented by 1. Update ONLY sections with new information. Never delete ACCA codes, provider status, or key file entries unless confirmed obsolete.
echo 2. Add any new ALP savings found to ALP_Database.md.
echo 3. Write a session log under 30 lines in session_logs/ named session_YYYY-MM-DD.md.
echo 4. Append one entry to wccs_log.md - record: date, old version, new version, sections changed, ALP entries added, files created, files deleted. Never overwrite wccs_log.md - always append.
echo 5. Delete the previous version handover file.
echo 6. Delete chat_latest.txt.
echo 7. Print a final summary: new handover filename, session log filename, wccs_log entry written yes/no.
) > "%SKILL_DIR%\SKILL.md"

echo SKILL.md updated.

REM Re-zip the folder
powershell -Command "Compress-Archive -Path '%SKILL_DIR%' -DestinationPath '%ZIP_OUT%' -Force"

echo.
echo ============================================
echo   DONE. New zip: wccs-generator-UPDATED.zip
echo   Location: Downloads\files claude-skilllsx2\
echo.
echo   2 manual steps left in Claude:
echo   1. claude.ai/customize/skills
echo      Click ... next to wccs-generator, Delete
echo   2. Click + and upload wccs-generator-UPDATED.zip
echo ============================================
pause
