# VKB Spin Doctor — Project Handover v43 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** WCCS Reliability Upgrade designed — 3-stage plan (Mini-Save Protocol, aafl_wccs.py, Chrome extension). New ACCA code CAWPA. aafl_wccs.py queued for next CLAC session.
**Last updated:** 2026-05-20 (WCCS automation)
**Consolidates:** v42

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
meta_loop.bat --apply                  # runs meta-loop with code changes enabled
```

---

## MISSION CONTROL CENTER (MCC)

MCC is the single-pane-of-glass for all project activity — the cross-cutting cockpit layer across all 6 projects. Two files on Desktop:
- `mission_control.html` — Central Command dashboard (dark theme, 4 tabs, auto-refresh 10s, mobile-responsive)
- `mission_control_tasks.json` — Kanban task data (Backlog | Up Next | In Progress | Blocked | Done)

MCC reads `dashboard_data.json` (written by dashboard_builder.py) for all non-Kanban tabs.

### Central Command — 5 Tabs

| Tab | Data source | What it shows |
|---|---|---|
| Kanban | mission_control_tasks.json | Task board — drag & drop, click to edit |
| Activity Feed | loop_output/ + session_logs/ | Last 50 events with timestamps |
| AAFL Runs | knowledge_engine.db (solution_log) | Last 50 runs: goal, score, provider, cost, pass/fail |
| Costs | cost_log.txt | Total spent, avg per run, runs today |
| Scout Control | mcc_server.py /run-scout | Goal input, 5 strategy toggles, sliders, 3 presets, live results, run history |
| AAFL Control | mcc_server.py /run-aafl | Goal control, provider dropdowns (14), loop settings, goal queue, live terminal output, run history |

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
| Handover injection | Loads VKB_SpinDoctor_Handover_v43.md into system prompt on startup |
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
├── set_goal.bat                       # Usage: set_goal.bat "your goal here"
├── aafl_doctor.bat                    # Pre-flight check: last score, providers, DB rows, current goal
├── regression_test.bat                # Runs loop --once with known goal, prints PASS/FAIL
├── queue_runner.bat                   # Thin wrapper — runs queue_runner.py
├── meta_loop.bat                      # Meta-loop launcher — runs meta_loop.py --once by default
├── run_aafl.bat                       # One-click full launch: LM Studio → wait port 1234 → aafl_doctor → queue_runner → dashboard_builder
├── RUN_VKB.bat                        # Double-click GUI launcher
├── GIT_BACKUP.bat                     # git add -A + commit + push
├── Universal_Input_Device_Database.md # 44 problems, all hardware types
├── Knowledge_Engine_Schema_v1.md      # DB schema reference
├── VKB_SpinDoctor_Handover_v43.md     # This file — read by sfl_agent on startup
├── problems/
│   ├── __init__.py
│   ├── conductor.py                   # Module 04 ✅ 619 lines
│   ├── ed_bind_reset.py               # ED Bind Reset prevention ✅
│   └── win_hardener.py                # Module 05 ✅ 9 problems W-001→W-009
├── data/
│   ├── devices.json                   # 98 devices with VID/PID lookup
│   ├── knowledge_engine.db            # SQLite — knowledge, solution_log, source_reputation
│   ├── cost_log.txt                   # CostGuard event log
│   └── dashboard_data.json            # MCC data — written by dashboard_builder.py
├── loop_output/                       # Loop reports: YYYY-MM-DD_HH-MM_<goal-slug>.md
├── meta_proposals/                    # Meta-loop proposals: YYYY-MM-DD_<slug>.md (max 200 lines each)
├── backups/                           # Auto-snapshots (vNN_<slug>/ naming + meta_YYYYMMDD_HHMMSS/)
├── sfl_logs/                          # SFL agent session logs
├── session_logs/                      # WCCS session logs
└── archive_dead/                      # Archived obsolete files

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

## ELITE DANGEROUS — KEY NOTES

- Spin bug already fixed at hardware level via VKB DevConfig. No .binds edit needed for spin.
- No custom .binds file exists yet — game uses built-in "KeyboardMouseOnly" default.
- .binds file is only created once Scott launches ED and customises one binding.
- When fixing spin via file: set `<MouseXMode Value="Bindings_MouseRoll" />` and `<MouseYMode>` to `Value=""`.
- ED Bind Reset prevention: rename the .binds file — ED never overwrites renamed files.

---

## KEYBINDING PROFILE LIBRARY (for v0.5)

### Ready to use

| Game | Source | Notes |
|---|---|---|
| Star Citizen | SubliminalsTV GitHub (github.com/SubliminalsTV/Subs-Curated-Bindings) | Free, updated every patch. Latest: 4.4 LIVE |
| Star Citizen Enhanced | Gumroad (subliminalstv.gumroad.com/l/Enhanced_VKB_NXT) | Requires Joystick Gremlin. Patch 4.5 PTU |
| War Thunder | WT Live community (live.warthunder.com/post/1112657/en) | Single stick simulator preset |
| DCS World | DCS file repo (digitalcombatsimulator.com/en/files — filter: VKB NXT) | Multiple aircraft |
| X4: Foundations | Built into game (in-game preset menu) | Zero install — added in 7.0 update |
| Falcon BMS | BMS forum (forum.falcon-bms.com/topic/26999) | F-16 focused |
| Arma Reforger | Workshop (reforger.armaplatform.com/workshop/660604C2DBCF99E2) | Helicopter only |
| Elite Dangerous | Frontier Forums (forums.frontier.co.uk/threads/618833) | USB device ID needs auto-fix |

---

## COMPETITIVE LANDSCAPE

| Tool | Problem |
|---|---|
| Joystick Gremlin | Complex, requires vJoy driver, power-users only |
| VKB DevConfig | Brand-locked to VKB, "obscure and arcane" |
| TARGET (Thrustmaster) | Thrustmaster hardware only |
| devreorder | Solves device order only, no GUI |
| antimicro | Generic, no game awareness, no auto-detect |

---

## FUTURE MODULES (Toggleable — build when needed)

| # | Module | Best free tool | Purpose |
|---|---|---|---|
| 1 | Gaming AI | Tryll Engine | On-device AI, detects GPU/VRAM |
| 2 | Hardware Detection | LocalAI | Auto-detects GPU backend |
| 3 | OCR / Screenshot | Tesseract + OCR.Space | Local free + 500 req/day API |
| 4 | Speech / Voice | Whisper (local) | Unlimited free, 99 languages |
| 5 | Agent Frameworks | LangGraph / CrewAI | Open-source, production-grade |
| 6 | Embeddings / Search | Cohere + ChromaDB | Cohere in .env, ChromaDB local |
| 7 | Community Data | Reddit PRAW API | Scrapes joystick fix threads |
| 8 | Code AI | Fireworks / Cerebras | Fastest free for code |
| 9 | Windows System AI | Ollama local | Zero cost on RTX 5090 |
| 10 | Device / IoT | LiteRT (Google) | Cross-platform acceleration |

---

## FULL ROADMAP

| Phase | Version | What gets built |
|---|---|---|
| ✅ Done | v0.1 | Spin bug fix — War Thunder |
| ✅ Done | v0.3-alpha | Engine architecture, 4 modules, 98 VID/PID devices, win_compat shim |
| ✅ Done | v0.3-alpha | Knowledge Base tab in GUI (War Thunder, ED, Star Citizen cards) |
| ✅ Done | v0.3-alpha | Conductor module (22 problems), ACP v1, 3-tab GUI |
| ✅ Done | v0.3-alpha | AAFL loop engine (aafl_core, loop_manager, evaluator, researcher) |
| ✅ Done | v0.3-alpha | Phases B+C+D — learning DB, scout agent, source reputation, tag taxonomy |
| ✅ Done | v0.3-alpha | win_hardener module (9 problems), bat utilities, loop improvements |
| ✅ Done | v0.3-alpha | AAFL loop 4 bugs fixed, AGENT_SYSTEM, Mission Control board, run_aafl.bat |
| ✅ Done | v0.3-alpha | AAFL self-improving meta-loop (meta_loop.py + meta_queue.txt + meta_loop.bat) |
| ✅ Done | v0.3-alpha | meta_loop.py real data injection fixed — full files + real DB rows + loop reports |
| ✅ Done | v0.3-alpha | mcu_optimizer.py — free-LLM board optimizer, WCCS step 6 |
| ✅ Done | v0.3-alpha | Central Command (MCC) — dashboard_builder.py + 4-tab mission_control.html |
| Next | v0.2 | Star Citizen full support |
| Soon | v0.3 | LM Studio + local AI wired in (Gemma 4 / Qwen2.5-VL) |
| Soon | v0.4 | ChromaDB vector memory — AI learns your setup |
| Future | v0.5 | Keybinding profile library — detect game, auto-install community profile |
| Future | v0.6 | AI learns preferences, builds custom profiles, warns about patch breakage |
| Future | v1.0 | Public release — any hardware, any game. Package as .exe (no Python needed). |

---

## HARDWARE & STACK

| Item | Detail |
|---|---|
| Joystick | VKB Gladiator NXT EVO (Right-hand), arrived 25 April 2026 |
| GPU | NVIDIA RTX 5090 (32GB VRAM) |
| RAM | 48GB DDR5 |
| OS | Windows 11 |
| Python | 3.14 at `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| Terminal | Run as Admin — Windows key + X → Terminal (Admin) |
| Claude Code | v2.1.119 — installed, working |
| LM Studio | v0.4.12 — models dir `D:\lm-models` |
| Gemma 4 | Loaded, Think mode OFF |
| Qwen2.5-VL-72B | 44GB on `D:\lmstudio-community\Qwen2.5-VL-72B-Instruct-GGUF` |
| Packages | mss, lmstudio, Pillow, anthropic, litellm, python-dotenv, langgraph, ddgs |
| API key | Windows environment variable `ANTHROPIC_API_KEY` |
| API model | claude-sonnet-4-6 |
| API cost | ~$0.003/screenshot (SFL agent). Claude Code much cheaper (text only). |
| Balance | $20.00 loaded 12/05/2026 — check console.anthropic.com for current balance |
| Console | https://console.anthropic.com/settings/billing |

---

## GITHUB

| Item | Detail |
|---|---|
| Account | jscottl-sketch |
| Repo | vkb-spin-doctor |
| Status | Private backup only — no auto-commit |

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
| Agent guesses wrong path | Path injection is in v3 — if broken, check VKB_SpinDoctor_Handover_v43.md is present |
| Task into PS prompt wrong order | Run agent first, THEN paste task at the `>` prompt |
| Claude Code auth conflict | Detected both claude.ai token + API key — uses API key. Working fine. |
| Cerebras model fails | Use cerebras/gpt-oss-120b in aafl_core.py — llama-3.3-70b deprecated. Fixed in v33. |
| Cerebras returns empty content | reasoning_content fallback in aafl_core.py handles this automatically |
| loop_manager --once stops mid-loop | Normal: LLM call count hit cap. Fixed: max_loop_iters/max_llm_calls are now separate. |
| Tags always empty in solution_log | infer_tags_from_keywords() keyword fallback handles this automatically |
| Groq auth fails | Needs GROQ_API_KEY in .env — get from console.groq.com → API Keys tab |
| Cloudflare key missing | Needs CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID in .env — dash.cloudflare.com |
| DB cache hit blocks test | Expected behaviour — delete data/knowledge_engine.db or test provider directly via aafl_core.py |
| win_hardener not showing in GUI | Check problems/win_hardener.py exists and WinHardenerCard is imported in spin_doctor.py |
| Models asking follow-up questions | Fixed — AGENT_SYSTEM constant injected into all LLM calls in loop_manager.py |
| Plan truncates mid-sentence | Fixed — plan max_tokens raised to 1024 |
| Web search results not reaching work step | Fixed — briefing_data["results"] guard, context now injected into both plan and work prompts |
| Mission Control board won't load | Open in Chrome/Edge (not Firefox). Click Connect board → pick mission_control_tasks.json from Desktop. |
| Gemini 503 Service Unavailable | Transient outage — Gemini will retry on next run. OpenRouter or Mistral will handle it in the meantime. |
| meta_loop proposal FLAGGED | Scores below 8.5 threshold — safe to review as advisory. Run again or pass --apply at your own judgement. |
| meta_loop --apply restores snapshot | Regression test failed — changes reverted. Check regression_test.bat output for clues. |
| meta_loop AI fabricates data | Fixed in v34 — real file content + DB rows + loop reports now injected into work prompt. |
| mcu_optimizer JSON parse error | LLM returned non-JSON — check raw response printed. Try again; Mistral is reliable for this. |
| mcu_optimizer drops tasks | Safety net re-adds any task the LLM drops. Check [SAFETY] lines in output. |
| dashboard_data.json empty/missing | Run dashboard_builder.py manually. Check data/ folder for knowledge_engine.db and cost_log.txt. |
| MCC tab shows no data | Confirm dashboard_data.json exists on the correct path. Check browser console for load errors. |

---

## WHAT NOT TO DO

- Don't rebuild anything marked ✅ — it exists, find the file
- Don't add multiple games at once — one game, test fully, then next
- Don't use external packages unless absolutely necessary (Tkinter is sufficient for now)
- Don't commit to GitHub without Scott's explicit decision
- Don't auto-flash firmware — warn and guide only, never auto-flash
- Don't rebuild from scratch — extend what's there
- API credits can burn completely in one bad loop — dead-end detector in loop_manager is the safeguard. Never run long loops without cost_guard active.
- Don't pass --apply to meta_loop without reading the proposal first

---

## NEXT PRIORITIES

1. Build database-backed handover (handover.db SQLite + migration from v45)
2. File cleanup caps (loop_output 50 max)
3. Provider keys (Gemini/Mistral dead)
4. MCC Watchdog+Rewind tab
5. START_MCC.bat rename

### 5-Project Split Plan
| Project | What goes in it |
|---|---|
| AAFL Engine | aafl_core.py, loop_manager.py, evaluator.py, researcher.py, memory_bank.py, meta_loop.py |
| VKB Spin Doctor | spin_doctor.py, problems/, sfl_agent.py, game configs, keybinding library |
| Mission Control | dashboard_builder.py, mcu_optimizer.py, mission_control.html, wccs_runner.py, mcc_server.py |
| Promo + Business | README, Ko-fi/Itch.io links, monetisation notes, roadmap |
| ACCA Database | ALP_Database.md, ACCA codes, v42 handover pinned |

Pin in each project: ALP_Database.md + latest handover (v42). MCC still reads same local files regardless of which project chat is open.

### 8 Providers Still to Sign Up
| Provider | URL |
|---|---|
| xAI Grok | x.ai/api |
| NVIDIA NIM | build.nvidia.com |
| SambaNova | cloud.sambanova.ai |
| GitHub Models | github.com/marketplace/models |
| Ollama | ollama.com |
| Together AI | together.ai |
| Fireworks AI | fireworks.ai |
| DeepSeek | platform.deepseek.com |

---

## WCCS PROTOCOL

**RULE: Always ask Scott "DSP? (claude --dangerously-skip-permissions)" before giving any CLAC block, every session, no exceptions.**

**WCCS = Write Claude Code Save.** Run at the end of every Claude Code session.

**Steps every WCCS must do:**
1. Write a new handover file (`VKB_SpinDoctor_Handover_vNN.md`) — increment the version number
2. Copy the entire `## CHAT LOG` section verbatim from the previous handover into the new one
3. Append one new entry to `## CHAT LOG` using the format below
4. Add a row to `wccs_log.md`
5. Write a session log to `session_logs/YYYY-MM-DD-ccN.md`
6. Run `python mcu_optimizer.py` — reads new handover + last 3 session logs + mission_control_tasks.json, updates board with optimal task ordering, prints diff of changes
7. Update `HANDOVER_FILENAME` in `sfl_agent.py` to point to the new version

**Mini-Save Protocol (Chat sessions):** Every ~10 exchanges, drop a 5-line MINI-SAVE block summarising key decisions so far. Passive capture — Scott does nothing. If Chat dies mid-session, latest mini-save is recent enough to recover from.

**Recovery Path (when WCCS fails mid-save):** Open new Chat → "Search past chats from last 24 hours and regenerate the WCCS summary that was lost." Claude uses conversation_search tool to rebuild.

**Pre-flight ALP check:** Before WCCS, if Claude detects allowance is low, skip full handover rewrite. Only do session log + chat log append. Light save.

**aafl_wccs.py (Stage 2 — planned):** Free LLM (Mistral) writes the new handover .md, not CLAC. Reads chat_latest.txt + current handover, writes new version. Zero Claude allowance burn for the write step.

**Chat log entry format:**
```
### YYYY-MM-DD
**Key decisions:** 
**New ACCA codes:** 
**Ideas discussed:** 
**Next priorities:** 
```

---

## RESUME COMMAND

> "Continuing VKB Spin Doctor. Read VKB_SpinDoctor_Handover_v43.md. MAJOR REFRAME: AAFL IS the project. Spin Doctor is the benchmark. Master + 5 sub-projects confirmed. MCC is cross-cutting cockpit layer — 5 new features planned (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue). WCCS Reliability Upgrade designed (3 stages: Mini-Save, aafl_wccs.py, Chrome extension). aafl_wccs.py not yet built (DSP required). merge_sessions.py not yet built (DSP pending). New ACCA code: CAWPA = Completely Automate Whats Possible by AI. AAFL competes with LangGraph/CrewAI/AutoGPT. Star Citizen v0.2 = first public benchmark + post trigger. ALP at 17 entries. Next: build aafl_wccs.py, build merge_sessions.py + .bat, execute 5-project split, build 5 MCC features, run Star Citizen benchmark, post when it passes."

---

## CHAT LOG
<!-- Append new entries below. Never delete. Never overwrite. -->

### 2026-05-17
**Key decisions:** Cerebras model chain llama3.1-70b → llama-3.3-70b (both deprecated) → gpt-oss-120b (current stable). reasoning_content fallback for all reasoning models. Cloudflare needs two env vars (CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID). Groq auth is API key only. win_hardener follows conductor.py API contract. Queue runner uses separate .py file to avoid batch special-character issues.
**New ACCA codes:** None
**Ideas discussed:** CHAT LOG section for permanent handover history. goal_queue.txt for overnight batch runs. Completion notification via stdlib winsound + ctypes MessageBoxW.
**Next priorities:** Star Citizen full support. Add GROQ_API_KEY to .env. Add Cloudflare keys to .env. Verify 6 skills toggles at claude.ai/customize/skills.

---

### 17 May 2026

**Key decisions:**
- AAFL first successful run confirmed — proof of concept PASSED. Cost £0.0027. Gemini planned, Mistral worked.
- Cerebras fixed: llama3.1-70b → llama-3.3-70b → gpt-oss-120b (final correct model, confirmed PASS 0.54s)
- All 7 CA tasks completed this session (verify fix, Groq prep, Cloudflare prep, goal queue, tag fallback, completion notification, win_hardener)
- AAFL will handle all game-specific tasks (Star Citizen etc) once fully autonomous
- Chat WCCS process agreed: WCCS in Chat → I generate Chat Summary → Scott pastes into CLAC → appends to CHAT LOG
- PROF added as ACCA Shorthand for Project Files — new Shorthand section created in ACCA

**New ACCA codes:**
- DSP = Dangerously Skip Permission
- AFNA = Attack From New Angle
- PROF = Project Files (Shorthand section)

**Ideas discussed:**
- Monetization: Ko-fi, Itch.io PWYW, GitHub Sponsors (immediate, zero work), Patreon, YouTube, Freemium £5 Pro, hardware manufacturer deal, AAFL as consulting service (long term)
- Fastest path to first £: Itch.io + Ko-fi link in README — 30 minutes work
- Consulting viable in 6 months once AAFL proven on own project first
- pin ACCA = command to show ACCA table in Chat right panel anytime
- Dedicated CHAT LOG section in handover so Chat content never gets lost
- PROF file concept: separate lightweight file Claude reads for reference, cheaper on ALP than full handover

**Blockers still open:**
- Verify step empty responses — loop scores blind (HIGH priority)
- Groq auth — email magic link needed in Edge at console.groq.com
- Cloudflare key — regenerate at dash.cloudflare.com
- Goal queue not yet tested end-to-end

**Next priorities:**
1. Fix verify step
2. Fix Groq auth
3. Test queue_runner.bat with 3 goals overnight
4. Get Spin Doctor public on GitHub when ready
5. Add Ko-fi + Itch.io links to README

---

### 2026-05-18
**Key decisions:** AAFL first real autonomous runs confirmed working. 4 bugs fixed in loop_manager.py: web search not firing (briefing_data fix), plan truncating (512→1024 tokens), chatbot follow-up questions (AGENT_SYSTEM constant), goal queue cleanup. Mission Control board built (mission_control.html + mission_control_tasks.json on desktop). run_aafl.bat built — one-click LM Studio + queue launcher. LM Studio server must be running before AAFL fires — now automated.
**New ACCA codes:** None this session
**Ideas discussed:** Xbox + VKB dual input in Star Citizen — AAFL can invent solutions from first principles. Workflow tracker as local HTML file updated by AAFL via JSON. Pinning chats as superpower.
**Next priorities:** 1. Fix scout web search quality 2. Run Star Citizen job with fixes applied 3. Test run_aafl.bat end to end 4. Open mission_control.html and connect to JSON

---

### 2026-05-18 (Chat session 2)
**Key decisions:** Mission Statement formalised — 9 rules, ALP is Rule No.1 absolute. SuperClaude concept defined (Claude at 90% ALP triggers emergency stop). AAFL confirmed as workhorse strategy — free providers do heavy lifting, Claude for big brain only. Tasks 5+6 (API keys) must always be manual — security rule, no exceptions.
**New ACCA codes:** WRS = Write Software. MCU = Mission Control Update (implied this session).
**Ideas discussed:** Full project philosophy locked — proof of concept first, money follows. AAFL reusable across any project. Claude can pay for itself if AAFL works. WS conflict resolved — WRS chosen for Write Software.
**CLAC block ready:** Tasks 1-4 automated (scout fix, Star Citizen AAFL job, run_aafl.bat test, Mission Control open). Tasks 5-6 manual (credentials).
**MCU updates:** No board changes made in Chat. CLAC block will trigger tasks 1-4 which may update mission_control_tasks.json directly.
**Next priorities:** 1. Paste tasks 1-4 CLAC block 2. Add GROQ key manually 3. Add Cloudflare keys manually

---

### 2026-05-18 (Claude Code session 2)
**Key decisions:** AAFL self-improving meta-loop built. meta_loop.py (dry-run default, --apply for code changes), meta_queue.txt (3 starter goals), meta_loop.bat (launcher). Cerebras model bug found and fixed — aafl_core.py still had `llama-3.3-70b` (deprecated) despite handover v32 saying it was fixed. Corrected to `gpt-oss-120b`. Mission Control updated with 2 new tasks (meta-loop dry-run review, Task Scheduler setup). First dry-run successful — proposal written to meta_proposals/.
**New ACCA codes:** None
**Ideas discussed:** Meta-loop uses second-opinion mechanism (task_type="batch" → Mistral vs task_type="reason" → Cerebras for genuine different-provider comparison). Both scores must be ≥ 8.5 for APPROVED status. --apply: snapshot → apply → regression test → restore if fail. Hard cap 3 meta-goals per invocation. Proposal is always written (FLAGGED vs APPROVED status). Goal queue comments out processed goals automatically.
**Bugs fixed:** Cerebras model in aafl_core.py was still `llama-3.3-70b` (deprecated) — fixed to `gpt-oss-120b`.
**Next priorities:** 1. Review meta_proposals/2026-05-18_compare_langgraph_120_vs_current.md 2. Run meta_loop.bat again for goal 2 (bottleneck finder) 3. Add GROQ_API_KEY to .env 4. Add Cloudflare keys to .env 5. Star Citizen full support

---

### 2026-05-18 (Claude Code session 3)
**Key decisions:** meta_loop.py work-step real-data injection fixed. Root cause: (1) _inject_file_context only read first 100 lines — raised to 600-line cap, full file. (2) _inject_db_context only triggered for 4 narrow keywords — expanded to 14 keywords including "bottleneck", "loop_manager", "identify", "improve". (3) DB query missing columns — now selects all solution_log columns. (4) New _inject_loop_reports() function added — injects last 3 loop_output report texts (80 lines each) for bottleneck/performance goals.
**New ACCA codes:** None
**Bugs fixed:** meta_loop.py _inject_file_context (100 → 600 lines), _inject_db_context (4 → 14 keywords, all columns), new _inject_loop_reports function wired into work prompt.
**Next priorities:** 1. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat 2. Add GROQ_API_KEY to .env 3. Add Cloudflare keys to .env 4. Star Citizen full support

---

### 2026-05-18 (Claude Code session 4)
**Key decisions:** mcu_optimizer.py built and tested. Reads latest handover (Next Priorities + Status) + last 3 session logs + mission_control_tasks.json (non-Done tasks), sends context to AAFLCore (task_type="batch" → Mistral), LLM returns reorganised JSON array, script diffs and writes back. Safety rules: never invents tasks, never deletes tasks, never touches Done column. Tested: Mistral responded in 22s, $0.0058, 0 changes (board already optimal — correct). JSON updated_by set to "mcu_optimizer". Fix 3: mcu_optimizer.py added to WCCS protocol as step 7 in handover. Three encoding bugs fixed during test (cost attribute name, arrow characters → ASCII).
**New ACCA codes:** None
**Bugs fixed:** mcu_optimizer.py: result.cost → result.cost_usd; unicode arrows → ASCII for Windows cp1252 console.
**Next priorities:** 1. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat 2. Add GROQ_API_KEY to .env 3. Add Cloudflare keys to .env 4. Star Citizen full support

---

### 2026-05-18 (Claude Code session 5)
**Key decisions:** Central Command (MCC — Mission Control Center) designed and built. dashboard_builder.py reads all data sources (DB, tasks JSON, cost log, loop_output/, session_logs/) and writes dashboard_data.json with atomic write + backup. mission_control.html upgraded to 4-tab Central Command: Kanban | Activity Feed | AAFL Runs | Costs. Auto-refresh every 10s. Mobile-responsive via OneDrive. Undo button reverts from backup. WCCS protocol updated: mcu_optimizer moved to step 6, sfl_agent update moved to step 7. dashboard_builder.py wired into run_aafl.bat and WCCS.
**New ACCA codes:** WRC = Write-Run-Check. MCC = Mission Control Center.
**Ideas discussed:** MCC as single pane of glass — one URL, all project state, works on phone via OneDrive share. Dashboard auto-refresh means no manual refresh needed during AAFL overnight runs.
**Next priorities:** 1. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat 2. Add GROQ_API_KEY to .env 3. Add Cloudflare keys to .env 4. Star Citizen full support

---

### 2026-05-18 (Claude Code session 5)
**Key decisions:** WCCS automation system built with 4 files: wccs_runner.py, mcc_server.py, mission_control.html, WCCS.bat.
**New ACCA codes:** None
**Ideas discussed:** WCCS automation system design, server-client architecture, mission_control.html upgrade.
**Bugs fixed:** None
**Next priorities:**
1. Open mission_control.html in Chrome, confirm 5 tabs + WCCS tab working
2. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat
3. Add GROQ_API_KEY to .env manually
4. Add Cloudflare keys to .env manually
5. Star Citizen full support

---

### 2026-05-18 (Claude Code session 6)
**Key decisions:** WCCS automation system built: wccs_runner.py + mcc_server.py + WCCS.bat + MCC 5th tab. All PASS. v37 written. DSP rule agreed: always ask Scott about --dangerously-skip-permissions before every CLAC block, no exceptions. WCCS fully delegated to AAFL: Chat writes 10-line summary only, AAFL does all file work via free LLM. Capture-as-you-go system designed: MCC captures throughout session so end-of-session summary is just a trigger.
**New ACCA codes:** None
**Ideas discussed:** DSP rule to be added to handover WCCS Protocol section + wccs-generator skill. mcc_server.py bridges MCC HTML to filesystem: POST /wccs, POST /capture, GET /captures, GET /status. MCC redesign brainstormed: Option A (sidebar HUD) vs Option B (single scroll BI-friendly). Decision pending. WCCS must live IN MCC permanently — pinned bottom of every panel, always visible. Capture timer (green/yellow/red) in top stats bar on all panels.
**Bugs fixed:** None
**Next priorities:**
1. Add DSP rule to handover + wccs-generator skill (2 CLAC blocks ready)
2. Scott decides MCC layout: Option A or B, dark or light theme
3. Build MCC redesign in CLAC
4. Delete old handovers v27-v34 from folder
5. Swap v36 for v37 in Project Files

---

### 2026-05-19 (Claude Code session 1)
**Key decisions:** MCC confirmed — still controls all projects after split, reads same local files regardless of which Claude Project chat is open. Full conversation detective search done — 20+ chats combed, full project history April 26 to today reconstructed. task_router.py confirmed built (88 lines) — classifies tasks AAFL/CLAC/SONNET/OPUS — added to v38 handover. 10 niche AI modules section added to v38 as Future Modules. Old handovers v27, v29-v34 deleted (7 files). Mystery files identified and kept: setup_router, full_auto_setup, health_check, quick_fix, archive_logs, task_db.json. Project split plan designed: 5 Claude Projects (AAFL Engine, VKB Spin Doctor, Mission Control, Promo+Business, ACCA Database). ALP_Database.md + v39 to be pinned in relevant projects after split. xAI Grok signup deferred to tomorrow via phone. DSP rule added to WHO IS SCOTT section. /wccs slash command created at .claude/commands/wccs.md.
**New ACCA codes:** None
**Bugs fixed:** None
**Ideas discussed:** 8 providers still to sign up (xAI, NVIDIA NIM, SambaNova, GitHub Models, Ollama, Together AI, Fireworks, DeepSeek). Project split means each project chat only loads its own pinned files — reduces context burn per message.
**Next priorities:**
1. Sign up xAI Grok tomorrow (phone) — add key to .env
2. Upload v39 to Project Files (replace v38)
3. Execute the 5-project split
4. Build MCC redesign (Option A or B — decision pending)
5. Star Citizen full support via AAFL

---

### 2026-05-19 (Chat session — Master Project strategy)
**Key decisions:** MAJOR REFRAME: AAFL IS the project. Spin Doctor is the benchmark/test subject, not the end goal. Master + 5 sub-projects (6 total) confirmed. Master = weekly boardroom (open max 2-3x/week). Sub-projects = daily workshops (lean context, ALP-efficient). merge_sessions.py + .bat chosen (Option 2) — double-click weekly, ~1 min. CLAC block not yet given (WCCS called first). AAFL now competes with LangGraph, CrewAI, AutoGPT. Spin Doctor v0.2 (Star Citizen) = AAFL's first real public demo/benchmark. Split barely affects benchmark (runs locally via Claude Code/AAFL, not Chat). External posting plan: r/LocalLLaMA, GitHub, HackerNews when benchmark passes.
**New ACCA codes:** None
**Ideas discussed:** Master project as boardroom vs sub-projects as workshops. Session logs as glue between all projects. AAFL could auto-merge logs (Option 3) but Scott prefers script (Option 2). Promotional path = AI/agent dev communities not flight sim Discords. Story angle: "beginner with BI builds self-improving AI agent." Scott wants to understand what posting means in practice before committing.
**ALP findings:** Master project open max 2-3x/week saves context vs opening daily. Daily work stays in lean sub-projects.
**Next priorities:**
1. Build merge_sessions.py + .bat (CLAC — DSP not yet confirmed)
2. Execute 5-project split + Master
3. Star Citizen benchmark via AAFL
4. External post when benchmark passes

---

### 2026-05-19 (Claude Code session 2)
**Key decisions:** WCCS only — no new code built this session. Pre-split assessment Chat session captured from chat_latest.txt. MCC confirmed as cross-cutting cockpit layer across all 6 projects, bidirectional, AAFL-powered. 5 new MCC features planned and documented: Stuck Inbox, Run Now button, Cost Predictor, Memory Inspector, Promotion Queue. ALP memory consolidated (11 outdated entries removed, 4 Master Plan entries added — now 17 entries). Story angle confirmed: "beginner with BI builds self-improving AI agent." merge_sessions.py DSP still pending.
**New ACCA codes:** None
**Bugs fixed:** None
**Ideas discussed:** AAFL opening up to new capabilities: stuck.md blocker files, external RSS/GitHub learning feeds, promotion drafting pipeline. merge_sessions.py still deferred pending DSP confirmation.
**Next priorities:**
1. Build merge_sessions.py + .bat (DSP pending)
2. Execute 5-project split + Master project
3. Build 5 new MCC features (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue)
4. Star Citizen v0.2 benchmark via AAFL autonomous run
5. External post when benchmark passes (r/LocalLLaMA primary)

---

### 2026-05-19 (Claude Code session 4)
**Key decisions:** AAFL Control Panel tab built for MCC. 6 tasks completed autonomously: (1) aafl_control_config.json created — 14 providers with tier/status, all loop settings. (2) mcc_server.py extended — 10 new endpoints (run-aafl, set-aafl-goal, aafl-status, aafl-queue GET/POST/DELETE, aafl-config GET/POST, aafl-providers, stop-aafl). (3) aafl_output/ directory + placeholder created, added to .gitignore. (4) AAFL Control tab added to mission_control.html as 7th tab — dark theme, 6 sections (Goal Control, Provider Control, Loop Settings, Goal Queue, Live Output, Run History). (5) Smoke test PASSED — /aafl-config returns valid JSON, /aafl-queue reads goal_queue.txt, /aafl-providers returns 14 providers. (6) Handover updated.
**New ACCA codes:** None
**Bugs fixed:** None
**Next priorities:**
1. Build aafl_wccs.py (CLAC, DSP confirmed required)
2. Build merge_sessions.py + .bat (DSP confirmed required)
3. Execute 5-project split + create Master project
4. Build 5 new MCC features: Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-19 (Claude Code session 3)
**Key decisions:** WCCS only — capturing Chat session (WCCS Reliability Upgrade design). New ACCA code CAWPA added. WCCS 3-stage reliability upgrade designed in Chat: (1) Mini-Save Protocol every ~10 exchanges, (2) aafl_wccs.py — free LLM writes handover (Stage 2, DSP required, queued for next CLAC session), (3) Chrome extension auto-capture (Stage 3, future). Recovery path confirmed: open new Chat → search past 24h chats → rebuild WCCS summary. Pre-flight ALP check protocol added.
**New ACCA codes:** CAWPA = Completely Automate Whats Possible by AI
**Bugs fixed:** None
**Ideas discussed:** aafl_wccs.py reads chat_latest.txt + current handover, free LLM (Mistral) writes new version — zero Claude allowance burn for the write step. Chrome extension auto-capture is Stage 3 (CA — fully removes manual WCCS trigger from Scott entirely). Mini-Save Protocol: passive capture every ~10 exchanges, Scott never types anything.
**Next priorities:**
1. Build aafl_wccs.py (CLAC, DSP confirmed required)
2. Build merge_sessions.py + .bat (DSP confirmed required)
3. Execute 5-project split + create Master project
4. Build 5 new MCC features (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue)
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-20 (Claude Code session 1)
**Key decisions:** Built aafl_watchdog.py and designed database-backed handover as permanent WCCS fix.
**New ACCA codes:** None
**Ideas discussed:** Scout Control mega-upgrade brainstormed, MCC tabs reorganization discussed.
**Bugs fixed:** None
**Next priorities:** 1. Build database-backed handover (handover.db SQLite + migration from v45). 2. File cleanup caps (loop_output 50 max). 3. Provider keys (Gemini/Mistral dead). 4. MCC Watchdog+Rewind tab. 5. START_MCC.bat rename.
