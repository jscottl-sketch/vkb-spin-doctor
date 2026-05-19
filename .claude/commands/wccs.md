# WCCS — Write Claude Code Save

Run all 7 WCCS steps automatically at the end of this session. No prompts. Do ALL steps.

## Steps

**STEP 1 — Determine new version number**
Read the filename of the latest `VKB_SpinDoctor_Handover_v*.md` in the project root. Increment the version number by 1. Call the new file `VKB_SpinDoctor_Handover_vNN.md`.

**STEP 2 — Write new handover file**
Copy `VKB_SpinDoctor_Handover_v(N-1).md` in full to `VKB_SpinDoctor_Handover_vNN.md`. Update the header:
- Version number in title and filename
- **Status:** line — summarise this session's key changes in one sentence
- **Last updated:** today's date
- **Consolidates:** previous version number

Update the `## CURRENT PROJECT STATUS` table — add any new components built this session, update statuses.

Update the `## PROJECT FILES` tree — add any new files created this session.

**STEP 3 — Append to CHAT LOG**
At the bottom of `## CHAT LOG` in the new handover, append a new entry:

```
### YYYY-MM-DD (Claude Code session N)
**Key decisions:** 
**New ACCA codes:** 
**Bugs fixed:** 
**Ideas discussed:** 
**Next priorities:**
1. 
```

Fill every field from this session's actual work. Never leave a field blank — write "None" if nothing applies.

**STEP 4 — Update wccs_log.md**
Append one row to `wccs_log.md`:
```
| vNN | YYYY-MM-DD | <one-line session summary> |
```

**STEP 5 — Write session log**
Write `session_logs/YYYY-MM-DD-ccN.md` with:
- Date, version, session number
- What was built / changed (bullet list)
- Bugs fixed (bullet list, or "None")
- Next priorities (numbered list)

**STEP 6 — Run mcu_optimizer**
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe mcu_optimizer.py
```
Print the diff output. If it errors, note the error but continue.

**STEP 7 — Update sfl_agent.py**
In `sfl_agent.py`, find the line containing `HANDOVER_FILENAME` and update the filename to point to the new handover version.

---

## Rules
- DSP: Before this command gives any CLAC block to Scott, always ask "DSP? (claude --dangerously-skip-permissions)"
- Never delete the CHAT LOG — only append
- Never change the version number to anything other than N+1
- If mcu_optimizer fails, log the error and continue — do not abort WCCS
- Git commit at the end: `git add -A` and commit `vNN: <session summary>`
