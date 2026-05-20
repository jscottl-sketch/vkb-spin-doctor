# v45 Reference Sections — VKB Spin Doctor
*Extracted from VKB_SpinDoctor_Handover_v45.md on 2026-05-20. Read-only archive.*

---

## HOW TO RUN

### Claude Code
Admin terminal (Windows key + X → Terminal (Admin)):
```
cd "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor"
```
```
claude
```

### SFL Agent
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\sfl_agent.py"
```

With token budget (for long tasks):
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\sfl_agent.py" --budget 30k
```

### Loop Manager (one iteration test)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\loop_manager.py" --once
```

### Meta-Loop (dry-run)
```
meta_loop.bat
```
Or with --apply to write code changes:
```
meta_loop.bat --apply
```

### MCU Optimizer (standalone)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\mcu_optimizer.py"
```

### Dashboard Builder (standalone)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\dashboard_builder.py"
```
Dry-run (no write):
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\dashboard_builder.py" --dry-run
```

### GUI
Double-click `RUN_VKB.bat`

### Full AAFL Launch (one click)
Double-click `run_aafl.bat` — starts LM Studio if not running, waits for port 1234, runs aafl_doctor + queue_runner.

### Bat Utilities
```
set_goal.bat "your goal here"         # writes goal.txt
aafl_doctor.bat                        # pre-flight health check
regression_test.bat                    # runs loop --once with known goal, PASS/FAIL
queue_runner.bat                       # runs all goals in goal_queue.txt
run_aafl.bat                           # one-click full launch (LM Studio + queue)
meta_loop.bat                          # runs meta-loop --once (dry-run, no code changes)
meta_loop.bat --apply                  # runs meta-loop with code changes enabled
```

---

## ENGINE ARCHITECTURE — MICROKERNEL

Drop a .py file into `/problems/` — engine picks it up automatically. No registration needed.

| Module ID | Name | Problems covered | Status |
|---|---|---|---|
| spin_fix | Spin Bug (Mouse Axis) | Removes mouse double-bind from flight axes | Working (War Thunder) |
| usb_power_saver | USB Power Saver | Disables Windows USB port power-off mid-session | Built |
| steam_input_conflict | Steam Input Conflict | Turns Steam Input OFF for WT, ED, MSFS, DCS, IL-2, AC7 | Built |
| conductor | Process Conductor | 22 problems — companion software, input mappers, overlays, launch order | Built |
| win_hardener | Windows Hardener | 9 problems W-001→W-009 — USB power, polling rate, registry, HID errors | Built — wired into Fix tab |
| ed_bind_reset | ED Bind Reset prevention | Prevents Elite Dangerous from resetting custom bindings | Built |
| identity | Device Identity | 7 problems (device naming, VID/PID, config name mismatch) | v0.3 |
| config | Config Mediator | 6 problems (game config files — WT spin fix lives here) | v0.2 |
| physical | Physical Diagnostics | 5 problems (USB port, hub, power — detect only) | v0.4 |

---

## PROJECT FILES

```
VKB-SpinDoctor/
├── spin_doctor.py                     # ~1057 lines. Tabs: Fix / Conductor / Knowledge Base.
├── sfl_agent.py                       # v3 — ~920 lines. ACP v1 + handover injection + call_aafl()
├── aafl_core.py                       # Provider routing — 14 providers, cheapest-first. Cerebras = gpt-oss-120b.
├── loop_manager.py                    # Loop engine — Phases B+C+D. AGENT_SYSTEM. Plan 1024 tokens.
├── evaluator.py                       # Result scorer 0-10. Pure logic.
├── researcher.py                      # research() + scout(). ddgs. Source reputation filtering.
├── memory_bank.py                     # SQLite store — knowledge, solution_log, source_reputation.
├── cost_guard.py                      # Cost + iteration brake
├── model_router.py                    # Model routing helpers
├── free_providers.py                  # Free provider list
├── control_panel.py                   # Control panel utility
├── meta_loop.py                       # AAFL self-improving meta-loop — real data injection fixed in v34
├── mcu_optimizer.py                   # Mission Control board optimizer — WCCS step 6
├── dashboard_builder.py               # MCC data builder — reads all sources, writes dashboard_data.json
├── task_router.py                     # Task classifier — routes to AAFL/CLAC/SONNET/OPUS
├── chief_scout.py                     # Parallel scout orchestrator — 5 strategies, Mistral synthesis, config-aware
├── afna_strategies.json               # 5 AFNA scout strategies: ddg, reddit, github, youtube, forum
├── chief_scout_config.json            # Scout Control config — 10 fields, 3 built-in presets
├── aafl_control_config.json           # AAFL Control Panel config — 14 providers, all loop settings
├── scout_output/                      # Scout run output — latest.txt written by mcc_server.py
├── aafl_output/                       # AAFL run output — latest.txt streamed by mcc_server.py /run-aafl
├── goal.txt                           # Current loop goal
├── goal_queue.txt                     # Queue of goals — one per line, # = comment
├── meta_queue.txt                     # Meta-loop goal queue — all 3 starter goals # DONE
├── queue_runner.py                    # Reads goal_queue.txt, runs loop --once per goal
├── chat_latest.txt                    # Latest Chat session summary — feeds into next WCCS
├── set_goal.bat                       # Usage: set_goal.bat "your goal here"
├── aafl_doctor.bat                    # Pre-flight check: last score, providers, DB rows, current goal
├── regression_test.bat                # Runs loop --once with known goal, prints PASS/FAIL
├── queue_runner.bat                   # Thin wrapper — runs queue_runner.py
├── meta_loop.bat                      # Meta-loop launcher — runs meta_loop.py --once by default
├── run_aafl.bat                       # One-click full launch: LM Studio + aafl_doctor + queue_runner + dashboard_builder
├── RUN_VKB.bat                        # Double-click GUI launcher
├── GIT_BACKUP.bat                     # git add -A + commit + push
├── ALP_Database.md                    # ALP savings — 17 entries. Grow it, never delete.
├── Universal_Input_Device_Database.md # 44 problems, all hardware types
├── Knowledge_Engine_Schema_v1.md      # DB schema reference
├── problems/
│   ├── __init__.py
│   ├── conductor.py                   # Module 04 — 619 lines
│   ├── ed_bind_reset.py               # ED Bind Reset prevention
│   └── win_hardener.py                # Module 05 — 9 problems W-001→W-009
├── data/
│   ├── devices.json                   # 98 devices with VID/PID lookup
│   ├── knowledge_engine.db            # SQLite — knowledge, solution_log, source_reputation
│   ├── cost_log.txt                   # CostGuard event log
│   └── dashboard_data.json            # MCC data — written by dashboard_builder.py
├── loop_output/                       # Loop reports: YYYY-MM-DD_HH-MM_<goal-slug>.md
├── meta_proposals/                    # Meta-loop proposals: YYYY-MM-DD_<slug>.md (max 200 lines each)
├── backups/                           # Auto-snapshots
├── sfl_logs/                          # SFL agent session logs
├── session_logs/                      # WCCS session logs
└── archive_dead/                      # Old handovers + obsolete files — NEVER deleted, only archived here

Desktop (C:\Users\jscot\Desktop\):
├── mission_control.html               # Central Command (MCC) — 4 tabs, auto-refresh 10s, mobile-responsive
└── mission_control_tasks.json         # Kanban data — 32 tasks, updated by mcu_optimizer on every WCCS
```

---

## GAME CONFIG FILE PATHS

| Game | Path | Format |
|---|---|---|
| War Thunder | `C:\Users\jscot\OneDrive\My Documents\My Games\WarThunder\Saves\226494292\production\` | .blk |
| Elite Dangerous | `C:\Users\jscot\AppData\Local\Frontier Developments\Elite Dangerous\Options\Bindings\` | .binds (XML) |
| Star Citizen | `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Controls\Mappings\` | .xml |
| Arma Reforger | `Documents\My Games\ArmaReforger\profile\.save\settings\customInputConfigs\` | .json |

---

## MCC ENDPOINTS (mcc_server.py)

### Scout Control Endpoints

| Endpoint | Method | What it does |
|---|---|---|
| /run-scout | POST | Accepts JSON config overrides, saves merged config, spawns chief_scout.py subprocess |
| /scout-result | GET | Returns scout_output/latest.txt + running status |
| /scout-config | GET | Returns current chief_scout_config.json |
| /scout-config | POST | Saves config updates without running a scout |
| /scout-presets | GET | Returns presets array from chief_scout_config.json |

### AAFL Control Endpoints

| Endpoint | Method | What it does |
|---|---|---|
| /run-aafl | POST | Reads aafl_control_config.json, writes goal.txt, spawns loop_manager.py --once, streams output to aafl_output/latest.txt |
| /set-aafl-goal | POST | Writes goal string to goal.txt and updates current_goal in aafl_control_config.json |
| /aafl-status | GET | Returns last 50 lines of aafl_output/latest.txt + last row from solution_log (score, provider, cost) |
| /aafl-queue | GET | Reads goal_queue.txt, returns array of goals with index and active/commented status |
| /aafl-queue | POST | Appends new goal to goal_queue.txt |
| /aafl-queue | DELETE | Comments out goal at given index in goal_queue.txt |
| /aafl-config | GET | Returns aafl_control_config.json |
| /aafl-config | POST | Saves config updates to aafl_control_config.json (preserves provider_list) |
| /aafl-providers | GET | Returns provider_list from aafl_control_config.json with tier and status |
| /stop-aafl | POST | Terminates running loop_manager.py subprocess |

---

## META-LOOP DETAIL

meta_loop.py analyses the loop's own performance and proposes improvements.

### How it works
1. Reads last 10 reports from `loop_output/` — calculates avg score, common failures, avg cost, slowest provider
2. Reads next uncommented goal from `meta_queue.txt`
3. Runs scout → plan → work → score on that goal (using AAFLCore)
4. Gets a second opinion from a different provider (task_type="batch" → Mistral route)
5. Both scores must be ≥ 8.5 to mark proposal as APPROVED
6. Writes proposal to `meta_proposals/YYYY-MM-DD_<slug>.md` (max 200 lines)
7. Comments out the processed goal in meta_queue.txt

### Data injection in work step (fixed in v34)
- Full source file for any file named in the goal — up to 600 lines
- Real solution_log rows from knowledge_engine.db — all columns
- Real loop_output report text — last 3 reports, up to 80 lines each
- DB injection triggers on: bottleneck, loop_manager, latency, tier, score, performance, analyse, identify, improve

### Dry-run vs apply
- **Dry-run (default):** proposal-only — no files changed
- **--apply:** snapshots backups/, applies CHANGE FILE blocks from proposal, runs regression_test.bat, restores from snapshot if regression fails

### meta_queue.txt goals
| Status | Goal |
|---|---|
| # DONE | Compare LangGraph 1.2.0 vs loop_manager.py — keep, migrate, or hybrid? |
| # DONE | Identify single biggest bottleneck in loop_manager.py — propose fix with file + line numbers |
| # DONE | Score each provider in aafl_core.py on success rate, latency, cost, quality — recommend new tier ordering |

---

## FULL ROADMAP

| Phase | Version | What gets built |
|---|---|---|
| Done | v0.1 | Spin bug fix — War Thunder |
| Done | v0.3-alpha | Engine architecture, 4 modules, 98 VID/PID devices, win_compat shim |
| Done | v0.3-alpha | Knowledge Base tab in GUI (War Thunder, ED, Star Citizen cards) |
| Done | v0.3-alpha | Conductor module (22 problems), ACP v1, 3-tab GUI |
| Done | v0.3-alpha | AAFL loop engine (aafl_core, loop_manager, evaluator, researcher) |
| Done | v0.3-alpha | Phases B+C+D — learning DB, scout agent, source reputation, tag taxonomy |
| Done | v0.3-alpha | win_hardener module (9 problems), bat utilities, loop improvements |
| Done | v0.3-alpha | AAFL loop 4 bugs fixed, AGENT_SYSTEM, Mission Control board, run_aafl.bat |
| Done | v0.3-alpha | AAFL self-improving meta-loop (meta_loop.py + meta_queue.txt + meta_loop.bat) |
| Done | v0.3-alpha | meta_loop.py real data injection fixed |
| Done | v0.3-alpha | mcu_optimizer.py — free-LLM board optimizer, WCCS step 6 |
| Done | v0.3-alpha | Central Command (MCC) — dashboard_builder.py + 4-tab mission_control.html |
| Next | v0.2 | Star Citizen full support |
| Soon | v0.3 | LM Studio + local AI wired in (Gemma 4 / Qwen2.5-VL) |
| Soon | v0.4 | ChromaDB vector memory — AI learns your setup |
| Future | v0.5 | Keybinding profile library — detect game, auto-install community profile |
| Future | v0.6 | AI learns preferences, builds custom profiles, warns about patch breakage |
| Future | v1.0 | Public release — any hardware, any game. Package as .exe (no Python needed). |

---

## TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `python` not found | Use full path: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| `localhost:1234` refused | Use `127.0.0.1:1234` |
| LM Studio server drops | Don't reload models while server is running |
| Gemma 4 empty replies | Think mode eating tokens — Think OFF + MAX_TOKENS = 3000 |
| Model not found (404) | Model string must be `claude-sonnet-4-6` |
| Credits too low (400) | Top up at console.anthropic.com/settings/billing |
| Cerebras model fails | Use cerebras/gpt-oss-120b in aafl_core.py — llama-3.3-70b deprecated |
| Cerebras returns empty content | reasoning_content fallback in aafl_core.py handles this automatically |
| loop_manager --once stops mid-loop | Normal: LLM call count hit cap |
| Tags always empty in solution_log | infer_tags_from_keywords() keyword fallback handles this automatically |
| Groq auth fails | Needs GROQ_API_KEY in .env — get from console.groq.com → API Keys tab |
| Cloudflare key missing | Needs CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID in .env — dash.cloudflare.com |
| DB cache hit blocks test | Expected behaviour — delete data/knowledge_engine.db or test provider directly |
| win_hardener not showing in GUI | Check problems/win_hardener.py exists and WinHardenerCard is imported in spin_doctor.py |
| Models asking follow-up questions | Fixed — AGENT_SYSTEM constant injected into all LLM calls in loop_manager.py |
| Plan truncates mid-sentence | Fixed — plan max_tokens raised to 1024 |
| Web search results not reaching work step | Fixed — briefing_data["results"] guard |
| Mission Control board won't load | Open in Chrome/Edge (not Firefox). Click Connect board → pick mission_control_tasks.json |
| Gemini 503 Service Unavailable | Transient outage — retry on next run |
| meta_loop proposal FLAGGED | Scores below 8.5 threshold — safe to review as advisory |
| meta_loop --apply restores snapshot | Regression test failed — changes reverted |
| meta_loop AI fabricates data | Fixed in v34 — real file content + DB rows + loop reports now injected |
| mcu_optimizer JSON parse error | LLM returned non-JSON — try again; Mistral is reliable for this |
| mcu_optimizer drops tasks | Safety net re-adds any task the LLM drops |
| dashboard_data.json empty/missing | Run dashboard_builder.py manually |
| MCC tab shows no data | Confirm dashboard_data.json exists on the correct path |
| Handover truncated after WCCS | Check line count >= 90% of previous version |
| Multiple CLAC terminals open | ALP-dangerous — parallel terminals share the same quota pool |

<!-- END_OF_FILE -->
