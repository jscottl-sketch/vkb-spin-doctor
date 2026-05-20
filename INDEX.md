# VKB Spin Doctor — INDEX
**Owner:** Scott (Croydon, England) | **Last updated:** 2026-05-20
**Files in this split:** INDEX.md (this) | STATUS.md | HISTORY.md | ACCA.md

---

## RESUME COMMAND
> "Continuing VKB Spin Doctor. Read INDEX.md and STATUS.md. HISTORY.md and ACCA.md are append-only archives — read only if asked. AAFL is THE PROJECT, Spin Doctor is the benchmark. ALP is Rule No.1."

---

## HOW TO RUN
| What | Command |
|---|---|
| Claude Code | cd "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor" then claude |
| GUI | Double-click RUN_VKB.bat |
| Full AAFL launch | Double-click run_aafl.bat |
| Meta-loop dry-run | meta_loop.bat (add --apply to write code changes) |
| SFL Agent | python sfl_agent.py (full path: C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe) |

Admin terminal: Windows key + X then Terminal (Admin)

---

## KEY FILE PATHS
| Type | Path |
|---|---|
| Project root | C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\ |
| Python | C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe |
| War Thunder | Documents\My Games\WarThunder\Saves\226494292\production\ (.blk) |
| Elite Dangerous | AppData\Local\Frontier Developments\Elite Dangerous\Options\Bindings\ (.binds XML) |
| Star Citizen | C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Controls\Mappings\ (.xml) |
| Arma Reforger | Documents\My Games\ArmaReforger\profile\.save\settings\customInputConfigs\ (.json) |

---

## HARDWARE & STACK
VKB Gladiator NXT EVO (RH) | RTX 5090 32GB | 48GB DDR5 | Win 11 | Python 3.14 | Claude Code v2.1.119 | LM Studio v0.4.12 (D:\lm-models) | API key in env var ANTHROPIC_API_KEY | model claude-sonnet-4-6 | GitHub: jscottl-sketch/vkb-spin-doctor (private)

---

## WCCS PROTOCOL (post-split)
1. Append entry to HISTORY.md (chat log) — NEVER rewrite, only append
2. Append new ACCA codes to ACCA.md if any — NEVER rewrite, only append
3. Rewrite STATUS.md with current state — ONLY file that gets rewritten
4. aafl_wccs.py does steps 1-3 via free Mistral — zero Claude allowance burn
5. Atomic write + read-back verify + END_OF_FILE check + line-count sanity (>=90% of prev)
6. Auto git commit
7. Old STATUS.md versions go to archive_dead/ — NEVER deleted

NEVER-DELETE rule: Old files move to archive_dead/. Never del or trash.
DSP rule: Before giving ANY CLAC block, ALWAYS ask "DSP? (claude --dangerously-skip-permissions)"

---

## TROUBLESHOOTING QUICK INDEX
- python not found: use full Python path above
- localhost:1234 refused: use 127.0.0.1:1234
- Gemma 4 empty replies: Think mode OFF, MAX_TOKENS=3000
- Cerebras 404: must be cerebras/gpt-oss-120b in aafl_core.py
- Handover truncated: check >= 90% of previous line count

<!-- END_OF_FILE -->
