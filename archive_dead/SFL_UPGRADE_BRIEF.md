SFL UPGRADE — 3 FEATURES
Rule: build one feature at a time. Test each before moving to next.
Rule: do not modify sfl_agent.py while sfl_agent.py is running.
Rule: no external packages — pure stdlib only.

FEATURE 1 — Named evolution snapshots
Current behaviour: backups/auto_YYYYMMDD_HHMMSS/
New behaviour: before each file edit, save to backups/v01_<task_slug>/, v02_<task_slug>/ etc.
task_slug = first 30 chars of current task, spaces replaced with underscores, lowercased.
Counter resets each new SFL session. Keeps last 20 as before.

FEATURE 2 — Rollback command
At the task prompt, user can type: rollback 3
SFL lists available snapshots with numbers.
User picks a number. SFL copies that snapshot back over the live files.
Confirms what was restored before continuing.

FEATURE 3 — Locked brief
At startup, SFL checks for SFL_UPGRADE_BRIEF.md in project folder.
If found: reads it, prints the plan back to user, asks go/no-go.
If user types go: proceeds.
If user types no: exits cleanly.
If not found: starts normally as today.
