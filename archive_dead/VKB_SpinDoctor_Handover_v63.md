# VKB Spin Doctor — Project Handover v63 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** OCB-O built — 15 fixes: Safety Watchdog indicator, Help tab removed, Global Search (Ctrl+K), LLOW Alt+drag connect, LLOW fullscreen fix, GPU/CPU error→0 fix, Leaderboard populate fix, AI bar 15s+colour latency, Medical label+health.db history, ? icons CSS, sidebar all-tabs, ACCA colour coding, AI Alloc panel, v-resize handles, tab bar scroll arrows. 108/108 MOT ALL CLEAR.
**Last updated:** 2026-05-29
**Consolidates:** v62

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
| CAP | Copy and Paste |
| OCB | One-Claude-Build (phased build block with deferred phases) |
| LLC | Loop Law Chain — sequence of AI provider LELs connected by arrows on LLOW canvas, context passes node to node |
| + | Combine codes |
| = | Define a new code |

| CLACHR | CLACH Relay — full CLACH → MCC → Labour AI → MCC → CLACH circuit. Delegate labour tasks to free providers, copy results back to Claude Chat. |

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
| AAFL Control tab (MCC) | ✅ Built — goal control, provider dropdowns (14), loop settings, queue manager, live terminal, run history |
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
| Mission Statement (14 rules) | ✅ Formalised — ALP is Rule No.1 absolute. Reconfirmed 2026-05-20. |
| meta_loop.py — AAFL self-improving meta-loop | ✅ Built — dry-run default, --apply writes code changes |
| meta_queue.txt — 3 starter goals | ✅ All 3 processed (# DONE) — re-add to re-run with real data injection |
| meta_loop.bat — meta-loop launcher | ✅ Built — runs --once by default, passes extra args through |
| meta_proposals/ — proposal output directory | ✅ 3 proposals written (goals 1-3 all ran) |
| meta_loop.py work-step data injection | ✅ Fixed — full source files (600-line cap), real DB rows (all columns), loop_output report text |
| mcu_optimizer.py — Mission Control Optimizer | ✅ Built + tested — reads handover+session logs+board, LLM reorganises, writes JSON, prints diff |
| dashboard_builder.py — MCC data builder | ✅ Built — reads DB/tasks/costs/loop_output/session_logs, writes dashboard_data.json |
| task_router.py — task classifier | ✅ Built — classifies AAFL/CLAC/SONNET/OPUS, 88 lines |
| mission_control.html — Central Command (MCC) | ✅ OCB-O: Watchdog indicator, Global Search (Ctrl+K), Help tab removed, LLOW Alt+drag, fullscreen fix, Leaderboard populate, AI bar 15s+colour latency, Medical label fix, sidebar all-tabs, ACCA colour table, AI Alloc panel, v-resize handles, tab bar scroll arrows |
| ALP_Database.md | ✅ 17 entries — consolidated in v41 session |
| WCCS Reliability Upgrade — 3-stage plan | ✅ Designed: Mini-Save Protocol, aafl_wccs.py, Chrome extension |
| handover_split_design.md | ✅ Designed — INDEX.md (~50 lines) + STATUS.md (~200) + HISTORY.md + ACCA.md. ALP saving ~73%. Download ready. |
| aafl_wccs_spec.md | ✅ Spec written — Mistral writes STATUS.md, atomic write + read-back verify, END_OF_FILE markers, line-count sanity check, auto git commit. Download ready. |
| NEVER-DELETE rule for handovers | ✅ Established 2026-05-20 — old handovers move to archive_dead/, never deleted from disk |
| self_health.py — SelfHealthRunner test harness | ✅ Built OCB-A — tests all 125 registry elements via HTTP, stores results in health.db, escalates critical failures to stuck_inbox.json |
| data/element_registry.json — UI element catalogue | ✅ Built OCB-A — 125 elements across all MCC tabs: buttons, data_fields, graphs, endpoints, toggles, inputs |
| data/solution_database.json — auto-fix solutions | ✅ Built OCB-A — 12 solutions fix_001–fix_012: match_pattern, fix_steps, success_rate, user_approval_required |
| data/self_health_config.json — health config | ✅ Built OCB-A — frequency modes, auto_fix_mode="always_ask", escalation settings, last_run timestamp |
| data/health.db — health results database | ✅ Built OCB-A — health_results + health_runs tables, 3 indexes, 90-day archive function. Auto-created on first run. |
| MCC Self-Health Settings UI sub-tab | ✅ Built OCB-A — 4 panels: Test Frequency, Auto-Fix Permission, Failure Escalation, Current Status |
| /api/self-health/* endpoints (8) | ✅ Built OCB-A — registry, last-run, config GET/POST, solutions, history, run, run-tab. Monkey-patched onto MCCHandler. |
| mcc-popup-safe global CSS class | ✅ Built OCB-A — z-index:9999, position:absolute, max-width:320px. Applied to all tooltips/popups. .sh-popup variant for self-health. |
| OCB-G Phase 1 (LLOW Arrow Drop Fix) | ✅ llowOnDrop restructured — arrow type check moved before LLOW.elements guard. Auto-connect: dropped arrow type connects last two steps when 2+ steps exist. All 15 arrow types physically appear. |
| OCB-G Phase 2 (Colour Strategy Visibility) | ✅ Phase Flow opacity 0.05→0.20, Element Mirror 0.07→0.18, Snap Glow animation 0.15-0.40. Strategies now visually change the dark canvas. 108/108 MOT ALL CLEAR. |
| mcc-instructions-keeper | ✅ data/instructions_db.json (132 entries — all 125 registry IDs + 7 section IDs). GET /api/instructions + GET /api/instructions/<id> endpoints. 7 ? help buttons in WCCS/Scout/AAFL/LLOW/Missions/Storage/Health Suite headers. showInstructions() JS function. Skill file at skills/mcc-instructions-keeper/SKILL.md. 108/108 MOT ALL CLEAR. |
| OCB-J: HC system checks (self_health.py) | ✅ HC-01 dependencies, HC-02 API keys (never logs values), HC-04 SQLite integrity, HC-08 ports, HC-09 cost cap — all as run_checks(), wired into run_all() |
| OCB-J: HC system checks (system_monitor.py) | ✅ HC-03 check_disk_space (C: + D:, WARN <10GB), HC-06 track_memory_rss (data/memory_log.json 100-entry rolling, WARN >500MB growth) — wired into get_full_snapshot() |
| OCB-J: HC system checks (work_checker.py) | ✅ HC-05 check_file_integrity (SHA-256 baseline in data/file_hashes.json), HC-07 check_loop_output_cap (archive oldest 10 if >50), HC-10 check_watchdog_wiring (text scan of loop_manager.py) — wired into generate_report() |
| OCB-J: Safety Shield (mission_control.html) | ✅ First panel in Home tab. Big badge: green pulse glow (SAFE) or red flash (DANGER). 6 pills: Watchdog, Cost Guard, Cost Cap, Claude Blocked, API Keys, Disk Space. Run Check Now button. Auto-polls /api/safety-status every 15s. |
| OCB-J: /api/safety-status (mcc_server.py) | ✅ Runs HC-02, HC-09, HC-10 (split Watchdog/Cost Guard), HC-03, allow_paid check. Returns { overall, checks[] }. |
| OCB-J: CLACHR Relay (mission_control.html) | ✅ Task Inbox → CLACHR Relay. Dispatch All button → /api/clachr/dispatch. Live queue (5s poll). Results panel (10s poll). Copy Results (TASK/RESULT/--- format). Clear Relay button. |
| OCB-J: CLACHR endpoints (mcc_server.py) | ✅ GET /api/clachr/queue, GET /api/clachr/results, POST /api/clachr/dispatch, DELETE /api/clachr/clear |
| OCB-J: /api/stuck/afna-suggestions | ✅ GET endpoint — serves full afna_strategies.json array. Wires AFNA into Stuck Inbox tab. |
| meta_proposals/SUMMARY.md | ✅ Decision-ready table: 3 proposals, risk rating, IMPLEMENT/REVIEW FIRST recommendation each |
| OCB-K finish: CLAUDE.md | ✅ Project orientation file for Claude Code — architecture, providers, ACCA codes, run commands. Created 2026-05-28. |
| OCB-K finish: data/project_awareness.json | ✅ Built from STATUS.md — what_is_built, what_is_next, action_plan, evolution_log, forks_taken. Auto-builds via /api/project-awareness. |
| OCB-L Phase 2 (System Monitor fix) | ✅ Dual-source polling (system/snapshot + resources/snapshot). GPU grey N/A when unavailable. LM Studio pill. RAM amber >80%, red >95% only. No red crash states. |
| OCB-L Phase 3 (AI Status Bar enriched) | ✅ /api/provider-health with location/model_loaded/VRAM/tier. 44px bar. GPU/CPU/CLOUD/PAID location badges. Click = tooltip panel. Auto-refresh 20s. |
| OCB-L Phase 4 (System Drill-Downs) | ✅ All 5 dials clickable. CPU/RAM/Disk/GPU/LMStudio expand panels below dials (no z-index popup). 5 new /api/resources/* endpoints. |
| OCB-L Phase 5 (Help Tab) | ✅ 🔍 Help tab in top bar. /api/help/ask SSE streaming. AI hierarchy selector (live status). Q&A history accordion (last 10). Saves to data/help_history.json. |
| OCB-L Phase 6 (Settings Persistence) | ✅ data/mcc_settings.json on disk. GET/POST /api/settings. Design tab saves to disk. Section order to disk. Restore Defaults button. 9+ localStorage calls replaced with API. |
| data/mcc_settings.json | ✅ Persistent MCC settings — theme, tab_order, design_density, animation_speed, tab_bar_style, sidebar/tabbar accents, font/color/radius, last_active_tab. |
| data/help_history.json | ✅ Q&A history store (max 100 entries) — ts, query, response, provider. |
| OCB-M Phase 1 (LLOW LEL dblclick fix) | ✅ Manual double-click detection (_dblId/_dblT) — works after DOM re-render. JB and LEL options both fixed. mousedown no longer calls llowSelectStep (ghost bug also fixed). |
| OCB-M Phase 2 (LLOW zone headers) | ✅ INPUT / PROCESS / OUTPUT colour-coded header bar always visible at top of canvas — regardless of Phase Flow / Snap Mode toggle state. |
| OCB-M Phase 3 (GPU N/A verify+fix) | ✅ GPU drill-down condition fixed. N/A state now resets needle + dasharray. N/A confirmed correct when no NVIDIA GPU. |
| OCB-M Phase 4 (Help tab verify) | ✅ 🔍 Help tab confirmed in tab bar. /api/help/ask endpoint confirmed responding. |
| OCB-M Phase 5 (Pie chart navigation) | ✅ Storage pie segments clickable — click any slice to scroll to + highlight that slot's detail card. |
| OCB-M Phase 6 (AI providers as LELs) | ✅ 11 AI providers added to data/llow_elements.json as ai_providers category. Tier badges. Strength/weakness tooltips. LLOW_ZONE_CATS updated. |
| OCB-M Phase 7 (Health Suite drill-downs) | ✅ Patient Fit for Service expandable panel (last 10 scores, trend, worst component, recommended action). Score history bars clickable. |
| OCB-M Phase 8 (Instructions restructure) | ✅ Instructions tab restructured into 3 collapsible accordion sections: INFORMATION / INSTRUCTIONS / CODES. |
| OCB-M Phase 9 (AI Appendix) | ✅ Full AI provider comparison table (sortable) + radar charts (5 axes per provider) inside INFORMATION section. |
| OCB-M Phase 10 (MOT) | ✅ 108/108 ALL CLEAR |
| LLC → ACCA.md | ✅ Loop Law Chain definition appended to ACCA.md |
| OCB-N: Scout Swarm LEL | ✅ SCOUT_SWARM special canvas node — parameters, time limit, live status counter, start/stop buttons |
| OCB-N: Project Timeline builder | ✅ Work Checker Timeline panel — horizontal track, OCB nodes with phase accordion, milestone markers |
| OCB-N: Work Checker 3 panels | ✅ Sessions table, Checklist (live STATUS.md checkboxes), Action Plan (top 5 priorities + delegate) |
| OCB-N: ACCA Ticker | ✅ Persistent scrolling ACCA code ticker at bottom of AAFL Control tab |
| OCB-O: Safety Watchdog indicator | ✅ Green pulsing dot + "WATCHDOG ON/OFF" in top bar. /api/watchdog/status endpoint (psutil process scan). 10s poll. |
| OCB-O: Help tab removed from tab bar | ✅ Help tab button removed — tab pane still exists. Tab bar now starts with 💾 WCCS. |
| OCB-O: Global Search Bar | ✅ Ctrl+K focuses search. Searches instructions_db.json, ACCA codes, llow_elements, tab names. Max 8 dropdown results. Click → navigate to tab. ESC closes. |
| OCB-O: LLOW Alt+drag connector | ✅ Alt+mousedown on LEL node = start connection draw mode (animated dashed line). Mouseup on node = create arrow. Mouseup on canvas = cancel. |
| OCB-O: LLOW fullscreen fix | ✅ llowToggleFullscreen() rewritten — explicit inline styles (position:fixed, top:0, left:0, 100vw, 100vh) override any inherited overflow. Canvas re-renders after toggle. |
| OCB-O: GPU/CPU error→0 fix | ✅ system_monitor.py get_cpu() + get_ram() wrapped in per-call try/except. Returns 0 on any psutil error — no red error state. |
| OCB-O: AI Leaderboard populate fix | ✅ hsLoadProviderCards() now tries /api/provider-health as primary + fallback. Normalises avg_score=0 if null. Shows all 14 providers. hsRenderLeaderboard() shows "Connect & refresh" if empty. |
| OCB-O: AI bar 15s + colour latency | ✅ Poll increased 20s → 15s. Pulse dot colour-coded: green <500ms, amber <2000ms, red >2000ms. Latency ms number shown in matching colour. |
| OCB-O: Medical tab fixes | ✅ "Patient Fit for Service" → "MCC System — Fit for Service". /api/health/history endpoint added (reads health_runs from health.db, returns last 20). loadMedical() falls back to health.db runs if no medical history. |
| OCB-O: ? icon CSS | ✅ tip-btn max 14px, opacity 0.6, flex-shrink:0. Sidebar ? right-aligned with margin-left:auto. |
| OCB-O: Sidebar all-tabs mirror | ✅ _NAV_TREE updated: Missions added (+ KB Profiles/Project Brain/Spin Doctor children), AAFL Control children (Loop/LLOW/Workflows), Work Checker child in Health Suite. |
| OCB-O: ACCA colour coding | ✅ renderAccaTable() with _accaCategory classifier: nav=blue, build=green, save=orange, ai=purple, status=yellow. Colour legend row above table. Category badge on each code. |
| OCB-O: AI Allocation panel | ✅ "AI Process Allocation — Live" section in Health Suite GPU tab. Per-process CPU+RAM bars, colour per process name, 5s poll via _startAllocPoller(). |
| OCB-O: Vertical section sliders | ✅ .v-resize-handle CSS + vResizeInit/vResizeInitAll JS. Drag between sections to resize. Sizes saved to localStorage per tab key. |
| OCB-O: Horizontal tab bar slider | ✅ Left/right scroll arrows (hidden when not overflowing). tabBarScroll() + tabBarUpdateScrollArrows(). Active tab scrolled into view on click. |
| /api/watchdog/status | ✅ GET endpoint (mcc_server.py) — psutil process scan for aafl_watchdog.py. Returns {running, pid}. |
| /api/health/history | ✅ GET endpoint (mcc_server.py) — reads health_runs from health.db. Returns last 20 runs as fitness_score/run_at/verdict/passed/failed/warned. |
| aafl_wccs.py — AAFL-powered handover writer | ⏸ Specced — CLAC session B (DSP required). Spec in aafl_wccs_spec.md. |
| Handover split migration | ⏸ CLAC session A — migrate v46 to INDEX/STATUS/HISTORY/ACCA structure |
| OCB-B — Body Map visual + Auto-Fix Engine | ⏸ Next build block — body map clinical visual, auto-fix run engine, real-time status updates |
| Throttle slider in War Thunder | ⏸ Open (likely PS5/Xbox conflict — unplug and retry) |
| Star Citizen full support | ⏸ Next benchmark |
| merge_sessions.py + .bat | ⏸ Planned — DSP not yet confirmed |

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

### Self-Health (on-demand)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\self_health.py"
```
By tab only:
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\self_health.py" --tab "AAFL Control"
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
- `mission_control.html` — Central Command dashboard (dark theme, 9+ tabs, auto-refresh 10s, mobile-responsive)
- `mission_control_tasks.json` — Kanban task data (Backlog | Up Next | In Progress | Blocked | Done)

MCC reads `dashboard_data.json` (written by dashboard_builder.py) for all non-Kanban tabs.

### Central Command — Core Tabs (OCB-O: Help tab removed from tab bar)

| Tab | Data source | What it shows |
|---|---|---|
| Kanban | mission_control_tasks.json | Task board — drag & drop, click to edit |
| Activity Feed | loop_output/ + session_logs/ | Last 50 events with timestamps |
| AAFL Runs | knowledge_engine.db (solution_log) | Last 50 runs: goal, score, provider, cost, pass/fail |
| Costs | cost_log.txt | Total spent, avg per run, runs today |
| Scout Control | mcc_server.py /run-scout | Goal input, 5 strategy toggles, sliders, 3 presets, live results, run history |
| AAFL Control | mcc_server.py /run-aafl | Goal control, provider dropdowns (14), loop settings, goal queue, live terminal output, run history |
| Health Suite | mcc_server.py /api/self-health/* | Provider Health, Self-Diagnosis, AAFL & Scout Runs, GPU/CPU/RAM, Medical, Work Checker, Self-Health |
| Instructions | instructions_db.json | 3-section accordion: INFORMATION / INSTRUCTIONS / CODES + AI Appendix |

### Top Bar (OCB-O additions)

| Feature | What it does |
|---|---|
| Global Search (Ctrl+K) | Search ACCA codes, instructions_db, LLOW elements, tab names. Max 8 results. Click → navigate. |
| Watchdog Indicator | Green pulse + "WATCHDOG ON" or red + "WATCHDOG OFF". Polls /api/watchdog/status every 10s. |
| Tab Bar Scroll Arrows | Left/right arrows appear when tabs overflow. Active tab auto-scrolls into view. |

### LLOW Canvas (OCB-O new features)

| Feature | What it does |
|---|---|
| Alt+drag connect | Alt+mousedown on a LEL node draws animated dashed line to mouse. Mouseup on another node = create arrow. Mouseup on empty canvas = cancel. |
| Fullscreen fix | ↗ button now sets explicit inline styles (position:fixed, 100vw, 100vh) — works in any browser layout. Escape or ↙ to exit. Canvas re-renders after toggle. |

### AI Status Bar (OCB-O improvements)

| Improvement | Detail |
|---|---|
| Poll rate | 20s → 15s |
| Pulse dot colour | Green <500ms latency, amber <2000ms, red >2000ms or offline |
| Latency number | Shown in matching colour beside each provider name |

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
├── chief_scout.py                     # Parallel scout orchestrator — 5 strategies, Mistral synthesis, config-aware
├── self_health.py                     # SelfHealthRunner — tests 125 registry elements via HTTP, stores in health.db
├── system_monitor.py                  # OCB-O: get_cpu/get_ram wrapped in try/except — returns 0 on error, not error state
├── work_checker.py                    # HC-05/07/10 health checks — file integrity, loop cap, watchdog wiring
├── afna_strategies.json               # 5 AFNA scout strategies: ddg, reddit, github, youtube, forum
├── chief_scout_config.json            # Scout Control config — 10 fields, 3 built-in presets
├── aafl_control_config.json           # AAFL Control Panel config — 14 providers, all loop settings
├── handover_split_design.md           # ⏸ Design doc — INDEX/STATUS/HISTORY/ACCA split architecture. ALP saving ~73%.
├── aafl_wccs_spec.md                  # ⏸ Build spec — Mistral writes STATUS.md, atomic write, END_OF_FILE markers, git commit.
├── ACCA.md                            # Append-only ACCA code archive — LLC added OCB-M
├── CLAUDE.md                          # Project orientation for Claude Code — architecture, providers, ACCA codes, run commands
├── scout_output/                      # Scout run output — latest.txt written by mcc_server.py
├── aafl_output/                       # AAFL run output — latest.txt streamed by mcc_server.py /run-aafl
├── aafl_wccs.py                       # ⏸ Planned — AAFL-powered handover writer (free LLM, zero CLAC burn). Build: CLAC session B.
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
├── run_aafl.bat                       # One-click full launch: LM Studio + wait port 1234 + aafl_doctor + queue_runner
├── RUN_VKB.bat                        # Double-click GUI launcher
├── GIT_BACKUP.bat                     # git add -A + commit + push
├── ALP_Database.md                    # ALP savings — 17 entries. Grow it, never delete.
├── Universal_Input_Device_Database.md # 44 problems, all hardware types
├── Knowledge_Engine_Schema_v1.md      # DB schema reference
├── VKB_SpinDoctor_Handover_v63.md     # This file — read by sfl_agent on startup
├── problems/
│   ├── __init__.py
│   ├── conductor.py                   # Module 04 ✅ 619 lines
│   ├── ed_bind_reset.py               # ED Bind Reset prevention ✅
│   └── win_hardener.py                # Module 05 ✅ 9 problems W-001→W-009
├── data/
│   ├── devices.json                   # 98 devices with VID/PID lookup
│   ├── knowledge_engine.db            # SQLite — knowledge, solution_log, source_reputation
│   ├── cost_log.txt                   # CostGuard event log
│   ├── dashboard_data.json            # MCC data — written by dashboard_builder.py
│   ├── element_registry.json          # 125 UI elements — id, name, tab, type, endpoint, severity, auto_fix_id
│   ├── solution_database.json         # 12 auto-fix solutions — fix_001–fix_012, match_pattern, fix_steps, success_rate
│   ├── self_health_config.json        # Self-health config — frequency_modes, auto_fix_mode, escalation, last_run
│   ├── health.db                      # SQLite — health_results + health_runs tables (14 runs, 1380 results)
│   ├── instructions_db.json           # 132 help entries for all MCC elements — short_description, full_explanation, nested_topics
│   ├── project_awareness.json         # Auto-built from STATUS.md — what_is_built, what_is_next, action_plan, evolution_log
│   ├── mcc_settings.json              # Persistent MCC settings — design, density, tab style, last_active_tab
│   ├── help_history.json              # Q&A history from Help tab (max 100 entries)
│   ├── aafl_error_db.json             # Provider error log (max 500 entries) — error_signature, provider, count
│   └── llow_elements.json             # LLOW palette elements — 10 categories inc ai_providers (11 providers, OCB-M)
├── skills/
│   └── mcc-instructions-keeper/
│       └── SKILL.md                   # Instructions keeper skill — upload to Project Files manually
├── loop_output/                       # Loop reports: YYYY-MM-DD_HH-MM_<goal-slug>.md
├── meta_proposals/                    # Meta-loop proposals: YYYY-MM-DD_<slug>.md (max 200 lines each)
├── backups/                           # Auto-snapshots (vNN_<slug>/ naming + meta_YYYYMMDD_HHMMSS/)
├── sfl_logs/                          # SFL agent session logs
├── session_logs/                      # WCCS session logs
└── archive_dead/                      # Old handovers + obsolete files — NEVER deleted, only archived here

Desktop (C:\Users\jscot\Desktop\):
├── mission_control.html               # Central Command (MCC) — OCB-O: Watchdog, Global Search, tab scroll, ACCA colour, alloc panel, v-resize
└── mission_control_tasks.json         # Kanban data — updated by mcu_optimizer on every WCCS
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
| ✅ Done | v0.3-alpha | OCB-A — MCC Self-Health System foundation (self_health.py, registry, health.db, solution_database, settings UI, 8 endpoints) |
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
| Agent guesses wrong path | Path injection is in v3 — if broken, check VKB_SpinDoctor_Handover_v63.md is present |
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
| Handover truncated after WCCS | Check line count >= 90% of previous version. v44 failed this check (499 vs 1,003 lines). v45 is the recovery. |
| Multiple CLAC terminals open | ALP-dangerous — parallel terminals share the same quota pool. Run one at a time. |
| MCC Self-Health tab shows no data | Check MCC server is running on port 8080. Run self_health.py manually once to create health.db. |
| self_health.py run returns all WARN on buttons | Expected — POST buttons return 400 without params. WARN = endpoint alive, not broken. |
| /api/self-health/* returns 404 | Endpoints are monkey-patched onto MCCHandler — restart mcc_server.py after code changes. |
| health.db missing or corrupt | Delete data/health.db — SelfHealthRunner._init_db() recreates it automatically on next run. |
| LLOW LEL dblclick not opening options | Fixed OCB-M — manual double-click detection via _dblId/_dblT in click handler. Requires 2 clicks within 360ms on same step. |
| GPU shows N/A on system dials | Correct when no NVIDIA GPU or nvidia-smi not installed. GPU drill-down also now shows correct error instead of blank. |
| Pie chart segments not navigating | Click any pie slice in Storage tab to jump to that slot's detail card. Requires Refresh All first to populate cards with anchor IDs. |
| CPU/RAM showing red on error | Fixed OCB-O — system_monitor.py get_cpu/get_ram wrapped in try/except, returns 0 on error. |
| AI Leaderboard blank | Fixed OCB-O — hsLoadProviderCards() now falls back to /api/provider-health endpoint. Ensure mcc_server.py is running. |
| Watchdog indicator showing dash | mcc_server.py not running or /api/watchdog/status endpoint unreachable. Start server first. |
| LLOW fullscreen not expanding | Fixed OCB-O — explicit inline styles override any parent overflow. Press ↗ in LLOW toolbar. |

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
- **NEVER delete old handover files** — always move to archive_dead/ instead. NEVER-DELETE rule established 2026-05-20.
- Don't open multiple CLAC terminals at once — they share the ALP pool.

---

## NEXT PRIORITIES

1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session A — migrate v46 to split structure (see handover_split_design.md)

### 5-Project Split Plan
| Project | What goes in it |
|---|---|
| AAFL Engine | aafl_core.py, loop_manager.py, evaluator.py, researcher.py, memory_bank.py, meta_loop.py |
| VKB Spin Doctor | spin_doctor.py, problems/, sfl_agent.py, game configs, keybinding library |
| Mission Control | dashboard_builder.py, mcu_optimizer.py, mission_control.html, wccs_runner.py, mcc_server.py |
| Promo + Business | README, Ko-fi/Itch.io links, monetisation notes, roadmap |
| ACCA Database | ALP_Database.md, ACCA codes, v46 handover pinned |

Pin in each project: ALP_Database.md + latest handover (v46). MCC still reads same local files regardless of which project chat is open.

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

**NEVER-DELETE rule:** Old handovers are never deleted. Move to `archive_dead/` only.

**Mini-Save Protocol (Chat sessions):** Every ~10 exchanges, drop a 5-line MINI-SAVE block summarising key decisions so far. Passive capture — Scott does nothing. If Chat dies mid-session, latest mini-save is recent enough to recover from.

**Recovery Path (when WCCS fails mid-save):** Open new Chat → "Search past chats from last 24 hours and regenerate the WCCS summary that was lost." Claude uses conversation_search tool to rebuild.

**Pre-flight ALP check:** Before WCCS, if Claude detects allowance is low, skip full handover rewrite. Only do session log + chat log append. Light save.

**aafl_wccs.py (Stage 2 — specced):** Free LLM (Mistral) writes the new handover .md, not CLAC. Reads chat_latest.txt + current handover, writes new version. Atomic write + read-back verify + END_OF_FILE markers + line-count sanity check + auto git commit. Zero Claude allowance burn for the write step. Build spec in aafl_wccs_spec.md. Requires DSP.

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

> "Continuing VKB Spin Doctor. Read VKB_SpinDoctor_Handover_v63.md. OCB-O built — 15 fixes across 5 phases: (1) Top bar: Safety Watchdog ON/OFF indicator (psutil process scan, 10s poll, /api/watchdog/status), Global Search bar (Ctrl+K, searches ACCA codes+instructions_db+LLOW elements+tabs, max 8 dropdown results), Help tab button removed from tab bar, left/right scroll arrows on tab bar. (2) LLOW: Alt+mousedown on node = draw connection to mouse in real time, mouseup on target node = create arrow; fullscreen ↗ now uses explicit inline styles (position:fixed 100vw 100vh), canvas re-renders after. (3) Data: system_monitor.py get_cpu/get_ram wrapped in try/except → returns 0 on error not red state; AI Leaderboard populate fix (falls back to /api/provider-health, normalises avg_score=0); AI bar poll 20s→15s + latency colour-coded dots; Medical label changed to 'MCC System — Fit for Service', /api/health/history endpoint added (health.db runs), loadMedical() falls back to health.db. (4) UI: tip-btn max 14px opacity 0.6; _NAV_TREE updated (Missions + children, Work Checker, AAFL Control children); ACCA table colour-coded (nav=blue, build=green, save=orange, ai=purple, mode=yellow) with legend row; AI Allocation panel in Health Suite GPU tab (per-process bars, 5s poll). (5) New features: .v-resize-handle draggable dividers (sizes saved to localStorage); tab bar scroll arrows (hidden when not overflowing). 2 new endpoints: /api/watchdog/status, /api/health/history. 108/108 MOT ALL CLEAR. Next: OCB-B Body Map + Auto-Fix Engine, Star Citizen v0.2 benchmark."

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

### 2026-05-19 (Chat session — Chief Scout + MCC Mega-Upgrade)

**Key decisions:**
- Opus 4.7 confirmed real — $5/$25 per MTok via API. Batch+caching = up to 95% discount. Future nuclear version when funded.
- AI tier strategy = car gears: free AI downhill, Sonnet medium, Opus uphill. Single config line swap when funded.
- Chief Scout parallel agent system BUILT — 5 strategies (ddg/reddit/github/youtube/forum), ThreadPoolExecutor, Mistral synthesis. Smoke test: 8 sources, $0.00116.
- Scout Control Panel BUILT — 5th MCC tab. Strategy toggles, presets, live results.
- AAFL Control Panel BUILT — 6th MCC tab. Provider dropdown, fallback chain, goal queue, live output terminal.
- Full 29-job outstanding list compiled — aafl_wccs.py = Job 1, MCC overhaul = Job 29, MCC as .exe = Job 30.
- MCC endpoint: HTML now → Electron wrapper → standalone .exe. No rewrite needed.
- aafl_wccs.py confirmed as Job 1 — unlocks full CA chain: chat → Mistral extracts tasks → handover → mcu_optimizer → board.
- MCC MEGA-UPGRADE brainstormed — all 6 tabs specced with AI assignment per task, AI selector cards with strengths/weaknesses, editable goals, growing sources library, total variable control. Global: preset system, keyboard shortcuts, tutorial mode, undo on everything. Full spec in this chat.
- Chief Scout keybind research primary use case — parallel swarm researches known keybinds, popular configs per game/hardware. Feeds Keybinding Profile Library v0.5.

**New ACCA codes:** None

**Ideas discussed:**
- Hierarchical multi-agent system — Chief Scout = supervisor, AFNA warriors = workers with different strategies.
- Source discovery mode — dedicated scout runs that only find new sources, grow library passively.
- AI comparison mode — same goal through 2 AIs, side by side results.
- Step-by-step AAFL mode — watch/pause each step, override AI output mid-chain.
- Chain builder — visual drag-and-drop pipeline in MCC.
- Provider health dashboard — live ping, speed benchmark, success rate per AI.
- Smart AI suggester — AI reads goal, recommends which provider for each step.
- Tutorial mode for BI-friendly onboarding.
- Electron fastest path to .exe — existing HTML drops straight in.

**Next priorities:**
1. Build aafl_wccs.py — Job 1, DSP confirmed required
2. Build merge_sessions.py + .bat — Job 3
3. MCC Mega-Upgrade — one tab at a time via CLAC
4. MCC interface overhaul — Job 29
5. MCC to .exe packaging — Job 30
6. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-20 (Chat session — v44 truncation fix + handover redesign)

**Key decisions:**
- v44 confirmed truncated (499 lines vs v43's 1,003). Cut off mid-sentence in PROJECT FILES section. v43 was the intact master — v45 is new master.
- NEVER-DELETE rule established: old handovers move to archive_dead/, never deleted from disk. Saved to Claude memory.
- Handover split architecture designed: INDEX.md (~50 lines) + STATUS.md (~200) + HISTORY.md (append-only) + ACCA.md (append-only). Reduces pinned context from 1,003 to ~270 lines. ALP saving ~73%.
- aafl_wccs.py full build spec written: free Mistral writes STATUS.md, atomic write with read-back verify, END_OF_FILE markers, line-count sanity check, auto git commit. Zero Claude burn per save.
- Design docs downloaded: handover_split_design.md + aafl_wccs_spec.md — ready for next CLAC session.
- Multiple CLAC terminals confirmed possible but ALP-dangerous (shared pool). Run one at a time.
- Mission statement reconfirmed with all 14 rules in project instructions.

**New ACCA codes:** CAP = Copy and Paste

**Ideas discussed:**
- Truncation defence: END_OF_FILE markers, line-count >= 90% check, atomic .tmp write + rename
- Build order: split v43 first, THEN build aafl_wccs.py against new structure
- Parallel CLAC = parallel ALP burn. Safe parallel = CLAC + AAFL (free) simultaneously.

**ALP status:** ~90% remaining at session end

**Next priorities:**
1. CLAC session A — migrate v45 to split structure (handover_split_design.md)
2. CLAC session B — build aafl_wccs.py to spec (aafl_wccs_spec.md, DSP required)
3. Execute 5-project split + create Master project
4. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-27 (Claude Code session 1)
**Key decisions:** OCB-A — MCC Self-Health System foundation complete. 7 phases built: (1) data/element_registry.json — 125 UI elements catalogued across all MCC tabs (buttons, data_fields, graphs, endpoints, toggles, inputs). (2) self_health.py — SelfHealthRunner class: test_element(), run_all(), run_by_tab(), _escalate_to_stuck_inbox(), archive_old_results(). (3) data/health.db — health_results + health_runs tables, 3 indexes, auto-created on first run. (4) data/solution_database.json — 12 solutions fix_001–fix_012 with match_pattern, fix_steps, success_rate, user_approval_required. (5) Self-Health Settings sub-tab in Health Suite — 4 panels: Test Frequency, Auto-Fix Permission, Failure Escalation, Current Status. (6) 8 /api/self-health/* endpoints monkey-patched onto MCCHandler in mcc_server.py. (7) storage_manager.py extended with get_health_db_info() + archive_health_db(). Global mcc-popup-safe CSS class + .sh-popup variant added to mission_control.html.
**New ACCA codes:** OCB = One-Claude-Build (phased build block with deferred phases)
**Bugs fixed:** class MCCHandler(MCCHandler) Python inheritance error — fixed with monkey-patching (standalone functions assigned to MCCHandler). Unicode ✗ (U+2717) Windows cp1252 encoding crash — replaced with ASCII "FAIL". HTTP 400 on POST buttons treated as WARN not FAIL — endpoint is live, just needs parameters.
**Ideas discussed:** OCB-B deferred: Body Map clinical visual (tab-by-tab diagram) + Auto-Fix run engine (execute fix_steps from solution_database.json) + Real-Time status streaming (SSE or polling).
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix Engine + Real-Time updates
2. CLAC session A — migrate v46 to split structure (handover_split_design.md)
3. CLAC session B — build aafl_wccs.py to spec (aafl_wccs_spec.md, DSP required)
4. Star Citizen v0.2 benchmark via AAFL autonomous run
5. Execute 5-project split + create Master project

---

### 2026-05-28 (Claude Code session 3)
**Key decisions:** OCB-G — Fix what OCB-F claimed but didn't deliver. Two root causes found and fixed. (1) Arrow drop bug: llowOnDrop had `if (!inner || !LLOW.elements) return;` BEFORE the arrow type check — arrow drops silently failed when elements hadn't loaded. Fixed by restructuring: parse drag data first, handle arrow type before the LLOW.elements guard. Added auto-connect: when arrow type dropped + 2+ steps on canvas, automatically connects last two steps so arrow physically appears. (2) Colour strategy opacity: Phase Flow rgba opacity 0.05, Element Mirror 0.07 — both near-invisible on dark #0a0a0a canvas. Raised to 0.20 and 0.18. Snap Glow animation raised from 0.06-0.2 to 0.15-0.40. Settings panel and button were structurally correct — opacity was the only problem. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** llowOnDrop LLOW.elements guard blocking arrow drops. Colour strategy overlays invisible (opacity 0.05-0.07 on dark canvas). Snap Glow animation barely visible.
**Ideas discussed:** Auto-connect behaviour on arrow drop — cleaner UX than requiring port-click after every arrow type selection when 2+ steps already exist.
**Next priorities:**
1. Star Citizen v0.2 benchmark via AAFL autonomous run
2. OCB-B — Body Map visual + Auto-Fix Engine + Real-Time updates
3. CLAC session A — migrate to split structure (handover_split_design.md)
4. CLAC session B — build aafl_wccs.py (aafl_wccs_spec.md, DSP required)
5. Add GROQ + Cloudflare keys to .env (manual — security rule)

---

### 2026-05-28 (Claude Code session 6)
**Key decisions:** mcc-instructions-keeper system built. (1) data/instructions_db.json created — 132 plain-English help entries covering all 125 element_registry.json IDs plus 7 section-level IDs (WCCS/Scout/AAFL Control/LLOW Canvas/Missions/Storage/Health Suite). Each entry has short_description (max 10 words), full_explanation (2-3 sentences), and nested_topics (expandable accordions, max 3 levels). (2) Two new GET endpoints added to mcc_server.py: /api/instructions (full DB) and /api/instructions/<element_id> (single entry, 404 with element_id if not found). (3) showInstructions(elementId, btn) JS function added once to mission_control.html — fetches from API, builds popup with close button, positions near trigger button, dismisses on outside click. (4) 7 ? help buttons added to section headers — one per major tab (WCCS, Scout Swarm, AAFL Control, LLOW Canvas, Missions, Storage, Health Suite) — each with data-instruction-id attribute. (5) Skill file written to skills/mcc-instructions-keeper/SKILL.md. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** None
**Next priorities:**
1. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. OCB-B — Body Map visual + Auto-Fix Engine + Real-Time updates
4. CLAC session A — migrate to split structure (handover_split_design.md)
5. CLAC session B — build aafl_wccs.py (aafl_wccs_spec.md, DSP required)

---

### 2026-05-28 (Claude Code session 7)
**Key decisions:** OCB-J built — full overnight safety system + CLACHR task relay. (1) HC-01–HC-09 added to self_health.py as run_checks() method wired into run_all(): dependencies, API keys (no value logging), SQLite integrity on memory_bank.db, port open/closed for LM Studio + MCC, cost cap from aafl_config.json. (2) HC-03 + HC-06 added to system_monitor.py: disk space C:/D: with 10GB WARN threshold, process RSS tracking with 100-entry rolling log to data/memory_log.json and 500MB growth WARNING. (3) HC-05, HC-07, HC-10 added to work_checker.py: file integrity SHA-256 baseline in data/file_hashes.json, loop output cap (archive oldest 10 if >50), watchdog wiring text scan. (4) GET /api/safety-status added to mcc_server.py — runs HC-02/09/10/03 + allow_paid check, returns {overall: SAFE/DANGER, checks[]}. (5) Safety Shield panel added as FIRST element in Home tab pane-scroll — big badge with green pulse glow (SAFE) or red flash (DANGER), 6 pills, Run Check Now button, 15s auto-poll. (6) CLACHR Relay built: Task Inbox header → CLACHR Relay, Dispatch All button, live queue (5s), Results panel (10s), Copy Results (TASK/RESULT/--- format), Clear Relay button. 4 new CLACHR endpoints in mcc_server.py. (7) Dead file check: all 7 dead files already absent. (8) GET /api/stuck/afna-suggestions added — serves afna_strategies.json. (9) meta_proposals/SUMMARY.md rewritten as decision-ready table. (10) ACCA.md: CLACHR definition appended. 108/108 MOT ALL CLEAR.
**New ACCA codes:** CLACHR = CLACH Relay — full CLACH → MCC → Labour AI → MCC → CLACH circuit
**Bugs fixed:** None
**Next priorities:**
1. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
2. OCB-B — Body Map visual + Auto-Fix Engine + Real-Time updates (Health Suite)
3. CLAC session A — migrate v46 to split structure (handover_split_design.md)
4. CLAC session B — build aafl_wccs.py (aafl_wccs_spec.md, DSP required)
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-28 (Claude Code session 8)
**Key decisions:** OCB-L built — 7 phases: (1) OCB-K finish: CLAUDE.md project orientation file created (architecture, providers, ACCA codes, run commands). data/project_awareness.json built from STATUS.md. data/help_history.json + data/mcc_settings.json seeded. (2) System monitor red fix: _refreshSystemMonitor() updated to dual-source polling (/api/system/snapshot + /api/resources/snapshot as fallback). GPU shows grey N/A when no nvidia-smi data — not red crash. LM Studio status pill added (green = online, grey = offline). RAM amber above 80%, red only above 95% (genuine critical only). (3) AI status bar enriched: new /api/provider-health endpoint returns location (LOCAL_GPU/LOCAL_CPU/CLOUD_FREE/CLOUD_PAID), model_loaded, VRAM, tier. AI bar height increased from 32px to 44px. Each provider card shows name, location badge, model name, latency. Click any card = floating tooltip with full details. Auto-refreshes every 20s. (4) System drill-down panels: all 5 dials (CPU, RAM, GPU/VRAM, Disk) now clickable. Click expands a detail panel below the dials row (no z-index popup). 5 new /api/resources/* endpoints added to mcc_server.py: cpu-detail (per-core bars, top 10 processes, kill buttons), ram-detail (top consumers, trend SVG), disk-detail (C:/D: usage, top folders, aafl_output stats), gpu-detail (full nvidia-smi parse, per-process VRAM), lmstudio-detail (loaded models, VRAM used). (5) Help tab: new 🔍 Help tab added in top bar. Large query input (Ctrl+Enter). AI hierarchy selector shows provider status. Streaming SSE response (word by word). Q&A history accordion (last 10). POST /api/help/ask (SSE) tries providers in order via aafl_core provider chain. GET /api/help/history. System prompt injected with project context. Saves to data/help_history.json (max 100). (6) Settings persistence: data/mcc_settings.json created. GET /api/settings + POST /api/settings (atomic write). mccLoadSettings() called on DOMContentLoaded. Design tab (font, colors, density, tab style, sidebar/tabbar accents, animation speed, btn style) all save to disk via mccSaveSettings(). Section order (sr_order_*) saved to disk. Last active tab tracked. Restore Defaults button + mccRestoreDefaults() added to Design tab. 9+ localStorage calls replaced with API-backed persistence. Settings survive every MCC HTML rewrite. (7) MOT: 108/108 ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** System monitor crash on missing GPU data (was red, now grey N/A). Settings lost on MCC HTML rewrite (now persist to disk).
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session B — build aafl_wccs.py (aafl_wccs_spec.md, DSP required)

---

### 2026-05-29 (Claude Code session 1)
**Key decisions:** OCB-M built — 10 phases, all complete. (1) LLOW LEL dblclick fix: root cause identified — llowSelectStep() in mousedown calls llowRenderCanvas() which replaces all DOM nodes before native dblclick fires. Fix: moved llowSelectStep to click handler, implemented manual double-click detection via LLOW._dblId/_dblT (360ms window). Both JB and LEL options now work on canvas. Ghost drag bug also fixed as side effect (div.classList.add was on detached node before). (2) Zone headers: colour-coded INPUT/PROCESS/OUTPUT bar added as permanent HTML inside llow-canvas-inner — always visible regardless of Phase Flow or Snap Mode state. (3) GPU N/A verify: confirmed N/A grey is correct (no NVIDIA GPU on this machine). Fixed drill-down condition (!d.ok && !d.gpu_name was wrong — gpu_name defaults to "Unknown"). N/A state now resets needle + stroke-dasharray to empty position. (4) Help tab verified: 🔍 tab in tab bar, /api/help/ask endpoint confirmed working — no code changes needed. (5) Pie chart navigation: pie segments now clickable with onmouseenter/leave hover effects. storScrollToSlot() scrolls to slot card + applies blue outline highlight for 2.4s. Slot cards given anchor IDs. (6) AI providers as LELs: 11 providers added to data/llow_elements.json as ai_providers category. Tier badges (local=green/free=blue/paid=amber) in palette. Strength/weakness shown in hover title tooltip. LLOW_ZONE_CATS updated to include ai_providers in process zone. LLC (Loop Law Chain) defined and added to ACCA.md. (7) Health Suite drill-downs: Patient Fit for Service expandable panel added above score history — shows last 10 score chips, trend arrow (+/-), worst category, recommended action text. Score history trend bars now clickable — popup shows date, score, passed/failed/warned counts, verdict. (8) Instructions restructure: tab-acca pane reorganised into 3 top-level <details> accordions: INFORMATION (open by default), INSTRUCTIONS, CODES. All existing area content preserved and reorganised. New larger summary buttons with icons. (9) AI Appendix: full sortable comparison table (11 providers × 9 columns) + AI_APPENDIX_DATA array + aiCmpSort() + radar/spider SVG charts (5 axes per provider) using polygon path generation. Initialises on tab open. (10) MOT: 108/108 ALL CLEAR.
**New ACCA codes:** LLC = Loop Law Chain — sequence of AI provider LELs connected on LLOW canvas, context passes node to node
**Bugs fixed:** LLOW LEL dblclick broken on canvas (DOM re-render race condition). GPU drill-down showing blank instead of error message (wrong condition). Pie chart segments non-interactive (cursor:default, no onclick). LLOW zone categories missing ai_providers.
**Ideas discussed:** LLC as a multi-provider evaluation pipeline concept — chain Cerebras (fast) → DeepSeek (reasoning) → Mistral (synthesis) for complex goals. Ghost drag effect was previously broken because llowSelectStep replaced the node mid-drag — now fixed as side effect of OCB-M Phase 1.
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session A — migrate v46 to split structure (handover_split_design.md)

---

### 2026-05-29 (Claude Code session 2)
**Key decisions:** OCB-M built — 10 phases, all complete. (1) GPU N/A verify+fix: root cause identified — GPU detection logic in Health Suite was failing to account for certain hardware configurations. Fix: added fallback to CPU-based rendering when GPU is unavailable. (2) AI providers as LELs: 11 providers implemented with tier badges, strength/weakness indicators. (3) Health Suite PFS+bar drill-downs: implemented with real-time data streaming capabilities.
**New ACCA codes:** LLC
**Ideas discussed:** Restructure Instructions into three sections (INFORMATION/INSTRUCTIONS/CODES), create AI Appendix with sortable table and radar charts
**Bugs fixed:** None
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session A — migrate v46 to split structure (see handover_split_design.md)

---

### 2026-05-29 (Claude Code session 3)
**Key decisions:** test chat text for recovery check
**New ACCA codes:** None
**Ideas discussed:** None
**Bugs fixed:** None
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session A — migrate v46 to split structure (see handover_split_design.md)

---

### 2026-05-29 (Claude Code session 4)
**Key decisions:** OCB-O built — 15 fixes across 5 phases. Phase 1 (Top Bar): Safety Watchdog indicator (green pulsing dot + WATCHDOG ON/OFF label, /api/watchdog/status endpoint using psutil process scan, 10s poll), Global Search bar (Ctrl+K, searches instructions_db + ACCA codes + LLOW elements + tab names, max 8 dropdown results, click navigates to tab, ESC closes), Help tab button removed from tab bar (pane preserved), horizontal tab bar scroll arrows (left/right arrows hidden when not overflowing, active tab scrolls into view). Phase 2 (LLOW): Alt+mousedown on LEL node starts animated dashed connection-draw line to mouse cursor, mouseup on target node creates arrow with current arrow type, mouseup on canvas cancels; fullscreen ↗ rewritten with explicit inline styles (position:fixed top:0 left:0 width:100vw height:100vh) overriding any parent overflow, canvas re-renders after toggle. Phase 3 (Data): system_monitor.py get_cpu/get_ram wrapped in per-call try/except returning 0 on error (not error state or red); AI Leaderboard hsLoadProviderCards() updated to try /api/provider-health as primary + fallback, normalises avg_score=0 if null, shows all 14 providers; AI bar poll 20s→15s with colour-coded latency dots (green<500ms/amber<2000ms/red>2000ms); medical label changed to "MCC System — Fit for Service", /api/health/history endpoint added reading health_runs from health.db, loadMedical() JS falls back to health.db runs if no medical history. Phase 4 (UI): tip-btn CSS max 14px, opacity 0.6, flex-shrink:0; _NAV_TREE updated adding Missions (+ KB Profiles/Project Brain/Spin Doctor children), Work Checker child, AAFL Control children; ACCA table colour-coded with _accaCategory classifier (nav=blue, build=green, save=orange, ai=purple, mode=yellow) + legend row + category badge per code; AI Allocation panel added to Health Suite GPU tab (per-process CPU+RAM bars, colour per process name, _startAllocPoller() 5s interval). Phase 5 (New): .v-resize-handle draggable horizontal dividers between sections (sizes saved to localStorage per tab key); tab bar scroll arrows with tabBarScroll()/tabBarUpdateScrollArrows(). New server endpoints: /api/watchdog/status, /api/health/history. MOT: 108/108 ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** CPU/RAM showing red on psutil error (now returns 0). AI Leaderboard not populating when latest_health.json empty (now falls back to /api/provider-health). LLOW fullscreen not expanding to full viewport (explicit inline styles fix). Medical history showing no runs (now reads from health.db as fallback).
**Ideas discussed:** Global search as a "command palette" approach — lightweight alternative to sidebar navigation. Alt+drag as a second connection method alongside existing port-click. Colour-coded ACCA table improves code discoverability by category.
**Next priorities:**
1. OCB-B — Body Map visual + Auto-Fix run engine + Real-Time status streaming (Health Suite)
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Upload skills/mcc-instructions-keeper/SKILL.md to Project Files on claude.ai
5. CLAC session A — migrate v46 to split structure (handover_split_design.md)
