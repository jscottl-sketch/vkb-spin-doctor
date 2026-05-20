# VKB Spin Doctor — Project Handover v44 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** AAFL Control Panel built (MCC tab 6). Chief Scout + MCC Mega-Upgrade specced in Chat. aafl_wccs.py = Job 1 next session. MCC-to-.exe plan confirmed (Electron wrapper).
**Last updated:** 2026-05-19
**Consolidates:** v43

---

## WHO IS SCOTT — READ THIS FIRST

- **Brain injury (BI) 2023** — ONE STEP AT A TIME. No exceptions. Never stack steps.
- **Beginner with code** — explain what's being built as you go
- **Always expand acronyms** on first use
- **Always include keyboard shortcuts inline** (e.g. Windows key + X)
- **Tables preferred** for structured info
- **Number all options** — Scott replies with just a number
- **No bullshit** — if something's hard or slow, say so upfront
- **DSP rule** — Before giving ANY CLAC (Claude Code) block, ALWAYS ask: "DSP? (claude --dangerously-skip-permissions)" — every session, no exceptions

---

## ACCA CODE

| Code | Meaning |
|---|---|
| DRR | Don't require response |
| DWR | Don't want response |
| YO | Scott asking for Claude's opinion |
| AIO | Claude giving its AI opinion |
| SIB | Summarise in brief |
| SIF | Summarise In Full |
| CR | Confidence rating 1–10 |
| WMBW | Why might be wrong |
| WCBB | What could be better |
| NRM | No-repeat mode |
| BI | Brain injury |
| SFL | Screenshot Feedback Loop |
| SS | Screenshot |
| WS | Web Search |
| WSF | Web Search Finding |
| CA | Completely Automate |
| AAFL | AI Agent Feedback Loop |
| ALP | Allowance Preservation |
| WYM | What You Mean |
| WENTO | Whatever Else Not Thought Of |
| CLAC | Claude Code |
| WCCS | Write Claude Code Save |
| DSP | Dangerously Skip Permission |
| AFNA | Attack From New Angle |
| PROF | Project Files |
| WRS | Write Software |
| MCU | Mission Control Update |
| WRC | Write-Run-Check (mini dev cycle: write code, run it, check output) |
| MCC | Mission Control Center (Central Command dashboard) |
| CAWPA | Completely Automate Whats Possible by AI |
| + | Combine codes |
| = | Define a new code |

Modes: TBLM (troubleshoot), DDM (deep dive), BGM (beginner), BPM (battle plan), NRM (no-repeat), EM (evidence)

---

## CURRENT PROJECT STATUS

| Component | Status |
|---|---|
| v0.1 spin fix — War Thunder | ✅ Working |
| usb_power_saver.py | ✅ Built |
| steam_input_conflict.py | ✅ Built |
| core/win_compat.py (pywin32 shim) | ✅ Built |
| data/devices.json (98 VID/PID devices) | ✅ Built |
| Universal_Input_Device_Database.md (44 problems) | ✅ In folder |
| problems/conductor.py (619 lines, 22 problems) | ✅ Built — 3 live conflicts found on Scott's machine |
| spin_doctor.py — 3 tabs (Fix / Conductor / KB) | ✅ ~1057 lines, all tabs confirmed working |
| sfl_agent.py v3 — ACP v1 + handover injection | ✅ ~920 lines, call_aafl() added |
| Claude Code v2.1.119 | ✅ Installed, working |
| Elite Dangerous spin fix | ✅ Fixed at hardware level via VKB DevConfig |
| GUI visual check (RUN_VKB.bat) | ✅ Done |
| ED Bind Reset prevention | ✅ Built as problems/ed_bind_reset.py, wired into GUI Fix Mouse Spin tab |
| aafl_core.py — provider routing | ✅ reasoning_content fallback, extra_env support, Cloudflare provider added |
| loop_manager.py — loop engine | ✅ 4 bugs fixed: web search, plan tokens, AGENT_SYSTEM, queue cleanup |
| evaluator.py — result scorer | ✅ Built — completeness/clarity/accuracy, 0-10, pure logic |
| researcher.py — DuckDuckGo search + scout() | ✅ research() + scout() with source reputation filtering |
| afna_strategies.json — 5 scout strategies | ✅ Built — ddg, reddit, github, youtube, forum |
| chief_scout_config.json — Scout Control config | ✅ Built — 10 fields, 3 presets (SC Keybinds / WT Bug Fix / ED Setup) |
| chief_scout.py — parallel scout orchestrator | ✅ Built — fires all 5 strategies simultaneously, Mistral synthesis, config-aware |
| Scout Control tab (MCC) | ✅ Built — goal input, 5 strategy toggles, sliders, presets, live results, run history |
| AAFL Control tab (MCC) | ✅ Built — goal control, provider dropdowns, loop settings, queue manager, live terminal, run history |
| memory_bank.py — Phases B+C+D | ✅ infer_tags_from_keywords() fallback added |
| Phase B — DB cache + reflection loop | ✅ search_solution, search_failures, store_solution. Cache hit confirmed. |
| Phase C — Scout agent + source reputation | ✅ scout(), update_source, get_top/blocked_sources |
| Phase D — Extended DB + tag taxonomy | ✅ TAGS constant (23), extended solution_log columns, tag inference |
| problems/win_hardener.py — 9 problems | ✅ W-001→W-009 built, WinHardenerCard wired into Fix tab |
| Cerebras provider fix | ✅ Fixed AGAIN: aafl_core.py updated to gpt-oss-120b (was still llama-3.3-70b in code) |
| set_goal.bat | ✅ Built — writes goal.txt via PowerShell |
| aafl_doctor.bat | ✅ Built — pre-flight check: last score, providers, DB row count, current goal |
| regression_test.bat | ✅ Built — sets known goal, runs --once, prints PASS/FAIL |
| goal_queue.txt + queue_runner.py/.bat | ✅ Built — reads queue, runs loop per goal, logs results |
| run_aafl.bat | ✅ Built — one-click: starts LM Studio if not running, waits port 1234, aafl_doctor, queue_runner |
| AAFL AGENT_SYSTEM constant | ✅ Injected into all LLM calls — no more chatbot follow-up questions |
| Mission Control board | ✅ mission_control.html + mission_control_tasks.json on Desktop — 32 tasks |
| AAFL autonomous runs confirmed | ✅ 4 goals processed, scores 8.07–9.33, DB cache hit working |
| Regression test PASS (8.83/10) | ✅ Gemini planned, Mistral worked |
| LangGraph 1.2.0 | ✅ Installed |
| Mission Statement (9 rules) | ✅ Formalised — ALP is Rule No.1 absolute |
| meta_loop.py — AAFL self-improving meta-loop | ✅ Built — dry-run default, --apply writes code changes |
| meta_queue.txt — 3 starter goals | ✅ All 3 processed (# DONE) — re-add to re-run with real data injection |
| meta_loop.bat — meta-loop launcher | ✅ Built — runs --once by default, passes extra args through |
| meta_proposals/ — proposal output directory | ✅ 3 proposals written (goals 1-3 all ran) |
| meta_loop.py work-step data injection | ✅ Fixed — full source files (600-line cap), real DB rows (all columns), loop_output report text |
| mcu_optimizer.py — Mission Control Optimizer | ✅ Built + tested — reads handover+session logs+board, LLM reorganises, writes JSON, prints diff |
| dashboard_builder.py — MCC data builder | ✅ Built — reads DB/tasks/costs/loop_output/session_logs, writes dashboard_data.json |
| task_router.py — task classifier | ✅ Built — classifies AAFL/CLAC/SONNET/OPUS, 88 lines |
| mission_control.html — Central Command (MCC) | ✅ Upgraded — 4 tabs (Kanban/Activity Feed/AAFL Runs/Costs), auto-refresh 10s, mobile-responsive |
| ALP_Database.md | ✅ 17 entries — consolidated this session (11 outdated removed, 4 Master Plan entries added) |
| WCCS Reliability Upgrade — 3-stage plan | ✅ Designed: Mini-Save Protocol, aafl_wccs.py, Chrome extension |
| aafl_wccs.py — AAFL-powered handover writer | ⏸ Planned — DSP confirmed required, next CLAC session |
| Throttle slider in War Thunder | ⏸ Open (likely PS5/Xbox conflict — unplug and retry) |
| Star Citizen full support | ⏸ Next up |
| merge_sessions.py + .bat | ⏸ Planned — DSP not yet confirmed |
| 5 new MCC features | ⏸ Planned — Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue |

---

## BIG VISION

**THE AAFL IS THE PROJECT NOW.** Spin Doctor is the benchmark and test subject — the first proof AAFL works. AAFL competes with LangGraph, CrewAI, AutoGPT as a self-improving AI agent framework. Story angle: *"beginner with BI builds self-improving AI agent."* Target communities: r/LocalLLaMA, GitHub, HackerNews. Post trigger: AAFL passes Star Citizen v0.2 benchmark via autonomous run.

Not a VKB-specific tool. A **universal input device assistant** — any hardware, any game, one tool.

> *"The tool that should have existed the moment the first joystick was ever plugged into a PC."*

**MCC is the cross-cutting cockpit layer** across all 6 projects — bidirectional, AAFL-powered. Reads same local files regardless of which Claude Project chat is open.

For each game the tool provides:
- Top 10 most common + least common problems and fixes
- Most popular community keybind preferences
- Downloadable keybind profiles stored locally
- Visual keybinding maps stored locally
- All accessible from the GUI Knowledge Base tab

**The core product:** Steam "Generic Gamepad Configuration Support" is silently breaking joysticks and wheels for millions of players. Fix = uncheck one box. Nobody has built a tool that does this automatically. That's Spin Doctor.

---

## TWO-TOOL STRATEGY

| Tool | Best for | Cost |
|---|---|---|
| Claude Code | Code jobs — reads files as text, edits directly | API credits, very efficient |
| SFL Agent (sfl_agent.py) | Visual tasks — game UIs, screen diagnosis | ~$0.003/screenshot |

**Rule:** Code jobs → Claude Code. Eyes-on-screen → SFL Agent.

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
```

---

## MISSION CONTROL CENTER (MCC)

MCC is the single-pane-of-glass for all project activity — the cross-cutting cockpit layer across all 6 projects. Two files on Desktop:
- `mission_control.html` — Central Command dashboard (dark theme, 7 tabs, auto-refresh 10s, mobile-responsive)
- `mission_control_tasks.json` — Kanban task data (Backlog | Up Next | In Progress | Blocked | Done)

MCC reads `dashboard_data.json` (written by dashboard_builder.py) for all non-Kanban tabs.

### Central Command — 7 Tabs

| Tab | Data source | What it shows |
|---|---|---|
| Kanban | mission_control_tasks.json | Task board — drag & drop, click to edit |
| Activity Feed | loop_output/ + session_logs/ | Last 50 events with timestamps |
| AAFL Runs | knowledge_engine.db (solution_log) | Last 50 runs: goal, score, provider, cost, pass/fail |
| Costs | cost_log.txt | Total spent, avg per run, runs today |
| Scout Control | mcc_server.py /run-scout | Goal input, 5 strategy toggles, sliders, 3 presets, live results, run history |
| AAFL Control | mcc_server.py /run-aafl | Goal control, provider dropdowns (14), loop settings, goal queue, live terminal output, run history |
| WCCS | mcc_server.py /wccs | Real-time WCCS status, logs, capture timer (green/yellow/red) |

### Scout Control — MCC Endpoints (mcc_server.py)

| Endpoint | Method | What it does |
|---|---|---|
| /run-scout | POST | Accepts JSON config overrides, saves merged config, spawns chief_scout.py subprocess |
| /scout-result | GET | Returns scout_output/latest.txt + running status |
| /scout-config | GET | Returns current chief_scout_config.json |
| /scout-config | POST | Saves config updates without running a scout |
| /scout-presets | GET | Returns presets array from chief_scout_config.json |

### AAFL Control — MCC Endpoints (mcc_server.py)

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

### Planned Next Features (5)

| Feature | What it does |
|---|---|
| Stuck Inbox | Captures stuck.md files from each sub-project — shows blockers in one view |
| Run Now button | One-click AAFL job trigger from MCC — no terminal needed |
| Cost Predictor | Estimates cost before running a goal — based on past run averages |
| Memory Inspector | Shows current knowledge_engine.db entries — browse/delete stale entries |
| Promotion Queue | Drafts external posts (r/LocalLLaMA etc.) — AAFL writes copy, Scott approves |

### Dashboard Builder (dashboard_builder.py)
Standalone script — no dependencies beyond stdlib + sqlite3.
- Reads: knowledge_engine.db, mission_control_tasks.json, cost_log.txt, last 10 loop_output/ files, last 5 session_logs/
- Writes: dashboard_data.json (atomic write via .tmp + rename)
- Backup: copies previous dashboard_data.json to dashboard_data_backup.json before write
- Flags: --dry-run (prints what would change, no write)
- Cap: 50 entries max per section
- Each section has last_updated timestamp
- Wired into: run_aafl.bat (after queue_runner), WCCS step 6 (after mcu_optimizer)

### Undo button
MCC has an Undo button that reverts dashboard_data.json from dashboard_data_backup.json — one click rollback.

### MCU Optimizer (mcu_optimizer.py)
Standalone tool that uses a free LLM to keep the Kanban board current after every session.
- Reads: latest handover (Next Priorities + Status), last 3 session logs, mission_control_tasks.json
- Sends to AAFLCore (cheapest free provider — Mistral by default)
- LLM reorganises Up Next (max 4), Backlog priority order, column moves
- Safety rules: never invents tasks, never deletes tasks, never moves out of Done
- Prints diff of column/priority changes
- Runs as WCCS step 6 automatically after every session save

---

## META-LOOP — AAFL SELF-IMPROVEMENT

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
Before the LLM receives the work prompt, meta_loop.py injects:
- **Full source file** for any file named in the goal (e.g. loop_manager.py) — up to 600 lines (full file)
- **Real solution_log rows** from knowledge_engine.db — all columns (id, problem, worked, ai_score, tags, iterations, game, hardware, created_at)
- **Real loop_output report text** — last 3 reports, up to 80 lines each
- **Provider metadata** from knowledge table if available
DB injection now triggers on broad keywords: bottleneck, loop_manager, latency, tier, score, performance, analyse, identify, improve

### Dry-run vs apply
- **Dry-run (default):** proposal-only — no files changed
- **--apply:** snapshots backups/, applies CHANGE FILE blocks from proposal, runs regression_test.bat, restores from snapshot if regression fails

### meta_queue.txt goals
| Status | Goal |
|---|---|
| # DONE | Compare LangGraph 1.2.0 vs loop_manager.py — keep, migrate, or hybrid? |
| # DONE | Identify single biggest bottleneck in loop_manager.py — propose fix with file + line numbers |
| # DONE | Score each provider in aafl_core.py on success rate, latency, cost, quality — recommend new tier ordering |

All 3 starter goals processed. Goals 2+3 ran FLAGGED (AI hallucinated data — fixed in v34). Re-add to meta_queue.txt to re-run with real data injection.

### Proposal format
Proposals in `meta_proposals/` include: goal, scores (primary + second opinion), approval status, loop stats table, full analysis, and (when relevant) a CHANGE FILE block for --apply to act on.

---

## SFL AGENT — KEY FEATURES

sfl_agent.py is reusable on any project — copy it to a new folder and create a PROJECT_HANDOVER.md there.

| Feature | What it does |
|---|---|
| Path injection | Project folder injected into every Claude message |
| Running memory | Claude sees all previous commands + outputs each loop |
| Extend at limit | At 50 iterations asks "keep going?" instead of stopping |
| Ask user | Claude can pause mid-task and ask Scott a question |
| Log file | Every session saves to `sfl_logs/` |
| Safe-op allow-list | Fewer Y/N prompts for obvious read-only ops |
| Flags | `--note`, `--folder`, `--budget` flags available |
| Handover injection | Loads VKB_SpinDoctor_Handover_v44.md into system prompt on startup |
| call_aafl(prompt) | Convenience wrapper — routes any prompt through AAFLCore |

### Autonomy Control Panel v1 (built into sfl_agent)

| Feature | What it does |
|---|---|
| Heartbeats | Prints one-line status every 30s. No per-step approvals needed. |
| Safe-op allow-list | Whitelist: reads, --help, --dry-run, --check, py_compile, git status. >5 files or wildcard = always asks. |
| Auto-snapshot | Copies .py/.json/.xml to backups/auto_YYYYMMDD_HHMMSS/ before any edit. Keeps last 20. |
| Token budget | Soft cap 80% = finish current task, stop new ones. Hard cap 100% = kill. |

---

## AAFL — PROVIDER ROUTING

aafl_core.py routes all LLM calls cheapest-first. Loop engine: loop_manager.py.

### Provider Status (as of 19 May 2026)

| Provider | Model | Tier | Status |
|---|---|---|---|
| LM Studio Coder 32B | openai/qwen2.5-coder-32b-instruct | 1 (local) | ✅ When LM Studio running |
| LM Studio VL 32B | openai/qwen2.5-vl-32b-instruct | 1 (local) | ✅ When LM Studio running |
| LM Studio DeepSeek R1 | openai/deepseek-r1-70b | 1 (local) | ✅ When LM Studio running |
| LM Studio Phi-4 14B | openai/phi-4-14b | 1 (local) | ✅ When LM Studio running |
| Cerebras GPT-OSS 120B | cerebras/gpt-oss-120b | 2 (free) | ✅ Fixed in aafl_core.py — was still llama-3.3-70b (deprecated) |
| Groq Llama 3.3 70B | groq/llama-3.3-70b-versatile | 2 (free) | ⚠️ Needs GROQ_API_KEY in .env — get from console.groq.com → API Keys |
| Groq DeepSeek R1 | groq/deepseek-r1-distill-llama-70b | 2 (free) | ⚠️ Needs GROQ_API_KEY in .env |
| Gemini 2.5 Flash | gemini/gemini-2.5-flash | 2 (free) | ⚠️ Working normally — occasional 503s (transient) |
| Mistral Codestral | mistral/codestral-latest | 2 (free) | ✅ Working — confirmed mcu_optimizer test run |
| Cloudflare Workers AI | cloudflare/@cf/meta/llama-3.1-8b-instruct | 2 (free) | ⚠️ Needs CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID in .env |
| OpenRouter Auto | openrouter/openrouter/auto | 3 (fallback) | ✅ Working — 23–34s but reliable |
| HuggingFace Mistral-7B | huggingface/mistralai/Mistral-7B-Instruct-v0.3 | 3 (fallback) | Key needed |
| Cohere Embeddings | cohere/embed-english-v3.0 | 3 (embed) | Key needed |
| Claude Sonnet (PAID) | claude-sonnet-4-6 | 99 (paid) | Blocked unless allow_paid=True |

### Loop Engine Components

| File | Role |
|---|---|
| aafl_core.py | Provider routing, LiteLLM wrapper, cheapest-first. reasoning_content fallback. extra_env support. |
| loop_manager.py | Plan→Work→Verify→Store loop. Phases B+C+D wired. --once flag. AGENT_SYSTEM injected. Web context to work step. Plan max_tokens=1024. |
| evaluator.py | Scores results 0-10 (completeness/clarity/accuracy). Pure logic. |
| researcher.py | research() + scout(). DuckDuckGo via ddgs. Source reputation filtering. |
| memory_bank.py | SQLite store — knowledge, solution_log, source_reputation. infer_tags_from_keywords() fallback. |
| cost_guard.py | Cost + iteration brake. Raises CostGuardError before cap exceeded. |
| meta_loop.py | AAFL self-improving meta-loop. Real data injection fixed in v34. |
| mcu_optimizer.py | Mission Control board optimizer. Reads context, sends to free LLM, rewrites JSON. WCCS step 6. |
| dashboard_builder.py | MCC data builder. Reads all sources, writes dashboard_data.json. Atomic write. --dry-run flag. |

### loop_manager.py — 4 Bug Fixes (18 May 2026)

| Bug | Fix |
|---|---|
| Web search not reaching work step | `briefing_data["results"]` guard — web context now injected into both plan AND work prompts |
| "No web context" string poisoning prompts | Changed `if briefing_text:` → `if briefing_data["results"]:` — empty-result string no longer injected |
| Plan truncating mid-sentence | `max_tokens=512` → `max_tokens=1024` on plan call |
| Models asking follow-up questions | `AGENT_SYSTEM` constant injected via `system=` on all LLM calls — explicit autonomous agent instruction |

### Phase B — Learning DB (solution_log)

Loop manager now:
1. Checks DB for past solution before any LLM call — prints `[DB] Past solution found (score X)` and exits early
2. Injects past failure_reasons into plan prompt if any failed attempts exist
3. Calls store_solution() after every iteration with problem, approach, worked, ai_score, tags, iterations, game, hardware

### Phase C — Scout Agent (source_reputation)

Loop manager now:
1. Calls scout(goal) before planning — prints `[SCOUT] Briefing ready — N source(s) found`
2. Injects web briefing (top 3 sources) into BOTH plan and work prompts (only when results exist)
3. Calls update_source(domain, score) for each source after scoring
4. Scout filters blocked domains (<= 3.0 avg) and prioritises top domains (>= 7.0 avg)

### Phase D — Tag Taxonomy (TAGS constant)

TAGS (23 tags): usb, steam, config_file, spin, bindings, registry, companion_software, polling_rate, axis, overlay, launch_order, firmware, driver, power, war_thunder, elite_dangerous, star_citizen, dcs, joystick, wheel, pedals, mouse, keyboard

Loop manager makes a fast LLM call after scoring to pick up to 5 tags. If LLM call fails/returns empty, `infer_tags_from_keywords()` matches TAGS against goal text as fallback.

---

## ENGINE ARCHITECTURE — MICROKERNEL

Drop a .py file into `/problems/` — engine picks it up automatically. No registration needed.

| Module ID | Name | Problems covered | Status |
|---|---|---|---|
| spin_fix | Spin Bug (Mouse Axis) | Removes mouse double-bind from flight axes | ✅ Working (War Thunder) |
| usb_power_saver | USB Power Saver | Disables Windows USB port power-off mid-session | ✅ Built |
| steam_input_conflict | Steam Input Conflict | Turns Steam Input OFF for WT, ED, MSFS, DCS, IL-2, AC7 | ✅ Built |
| conductor | Process Conductor | 22 problems — companion software, input mappers, overlays, launch order | ✅ Built |
| win_hardener | Windows Hardener | 9 problems W-001→W-009 — USB power, polling rate, registry, HID errors | ✅ Built — wired into Fix tab |
| ed_bind_reset | ED Bind Reset prevention | Prevents Elite Dangerous from resetting custom bindings | ✅ Built |
| identity | Device Identity | 7 problems (device naming, VID/PID, config name mismatch) | ⏸ v0.3 |
| config | Config Mediator | 6 problems (game config files — WT spin fix lives here) | ⏸ v0.2 |
| physical | Physical Diagnostics | 5 problems (USB port, hub, power — detect only) | ⏸ v0.4 |

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
├── chief_scout.py                     # Parallel scout orchestrator — 5 strategies, Mistral synthesis, config-aware (load_config())
├── afna_strategies.json               # 5 AFNA scout strategies: ddg, reddit, github, youtube, forum
├── chief_scout_config.json            # Scout Control config — 10 fields, 3 built-in presets
├── aafl_control_config.json           # AAFL Control Panel config — 14 providers, all loop settings
├── scout_output/                      # Scout run output — latest.txt written by mcc_server.py
├── aafl_output/                       # AAFL run output — latest.txt streamed by mcc_server.py /run-aafl
├── aafl_wccs.py                       # ⏸ Planned — AAFL-powered handover writer (free LLM, zero CLAC burn)
├── HOW_TO_INTEGRATE_DIAGNOSTIC.py     # Integration guide
├── goal.txt                           # Current loop goal
├── goal_queue.txt                     # Queue of goals — one per line, # = comment
├── meta_queue.txt                     # Meta-loop goal queue — all 3 starter goals # DONE
├── queue_runner.py                    # Reads goal_queue.txt, runs loop --once per goal
├── chat_latest.txt                    # Latest Chat session summary — feeds into next WCCS
├── set_goal.bat                       # Usage: set_goal.