# VKB Spin Doctor — Project Handover v78 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** Global tooltip/info visibility fix — all tooltip CSS z-index bumped 9999→99999, tab bar z-index:100, positionTooltip() JS function added, all 4 JS tooltip functions wired, [data-tooltip]::after CSS system added, data-tooltip on all 13 tab buttons; 109/109 MOT ALL CLEAR.
**Last updated:** 2026-05-31
**Consolidates:** v77

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
| OCBR | OCB Runner — Lifeguard Protocol tool: snapshots, WAL, recovery, CLAC stubs |
| LLC | Loop Law Chain — sequence of AI provider LELs connected by arrows on LLOW canvas, context passes node to node |
| MCCM | Mission Control Center Master — overseer agent, power levels 1–4, approves AI dispatches |
| RRCLACH | Run Request CLACH — panel that generates rrclach_request.json with OCB block + acceptance criteria |
| HISAV | History + Ideas + Save — the renamed WCCS tab with 11 accordion sections |
| DTA | Data As Truth Architecture — project state in structured JSON files HISAV can read/write without AI |
| STORM | Selective Targeted Output Remove Merge — unified data feed from detective/WCCS/screenshots |
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
| aafl_core.py — provider routing | ✅ v71 — OpenRouter model fixed, 503 retry (3 attempts 2s/4s/8s), provider_timeout from config |
| loop_manager.py — loop engine | ✅ v71 — session_state updates at run start/completion |
| evaluator.py — result scorer | ✅ Built — completeness/clarity/accuracy, 0-10, pure logic |
| researcher.py — DuckDuckGo search + scout() | ✅ research() + scout() with source reputation filtering |
| afna_strategies.json — 5 scout strategies | ✅ Built — ddg, reddit, github, youtube, forum |
| chief_scout_config.json — Scout Control config | ✅ Built — 10 fields, 3 presets (SC Keybinds / WT Bug Fix / ED Setup) |
| chief_scout.py — parallel scout orchestrator | ✅ v69 — get_project_context() + --no-context flag added |
| Scout Control tab (MCC) | ✅ Built — goal input, 5 strategy toggles, sliders, presets, live results, run history |
| AAFL Control tab (MCC) | ✅ Built — goal control, provider dropdowns (14), loop settings, queue manager, live terminal, run history |
| memory_bank.py — Phases B+C+D | ✅ infer_tags_from_keywords() fallback added |
| Phase B — DB cache + reflection loop | ✅ search_solution, search_failures, store_solution. Cache hit confirmed. |
| Phase C — Scout agent + source reputation | ✅ scout(), update_source, get_top/blocked_sources |
| Phase D — Extended DB + tag taxonomy | ✅ TAGS constant (23), extended solution_log columns, tag inference |
| problems/win_hardener.py — 9 problems | ✅ W-001→W-009 built, WinHardenerCard wired into Fix tab |
| Cerebras provider fix | ✅ Fixed AGAIN: aafl_core.py updated to gpt-oss-120b |
| set_goal.bat | ✅ Built |
| aafl_doctor.bat | ✅ Built |
| regression_test.bat | ✅ Built |
| goal_queue.txt + queue_runner.py/.bat | ✅ Built |
| run_aafl.bat | ✅ Built |
| AAFL AGENT_SYSTEM constant | ✅ Injected into all LLM calls |
| Mission Control board | ✅ mission_control.html + mcc_server.py on localhost:8080 |
| AAFL autonomous runs confirmed | ✅ 4 goals processed, scores 8.07–9.33, DB cache hit working |
| Regression test PASS (8.83/10) | ✅ Gemini planned, Mistral worked |
| LangGraph 1.2.0 | ✅ Installed |
| Mission Statement (14 rules) | ✅ Formalised — ALP is Rule No.1 absolute. |
| meta_loop.py — AAFL self-improving meta-loop | ✅ Built — dry-run default, --apply writes code changes |
| meta_queue.txt — 3 starter goals | ✅ All 3 processed (# DONE) |
| meta_loop.bat — meta-loop launcher | ✅ Built |
| meta_proposals/ — proposal output directory | ✅ 3 proposals written |
| meta_loop.py work-step data injection | ✅ Fixed — full source files (600-line cap), real DB rows, loop_output report text |
| mcu_optimizer.py — Mission Control Optimizer | ✅ Built + tested |
| dashboard_builder.py — MCC data builder | ✅ Built |
| task_router.py — task classifier | ✅ Built — classifies AAFL/CLAC/SONNET/OPUS, 88 lines |
| mission_control.html — Central Command (MCC) | ✅ v78 — Global tooltip visibility fix: all z-index 99999, positionTooltip() JS, data-tooltip on all tab buttons |
| ALP_Database.md | ✅ 17 entries |
| WCCS Reliability Upgrade | ✅ Designed: Mini-Save Protocol, aafl_wccs.py, Chrome extension |
| aafl_wccs.py | ✅ v73 — archive_old_handovers() wired, runs on every WCCS save |
| self_health.py — SelfHealthRunner | ✅ Built OCB-A — 125 registry elements, health.db |
| data/element_registry.json | ✅ 125 elements across all MCC tabs |
| data/solution_database.json | ✅ 12 solutions fix_001–fix_012 |
| data/health.db | ✅ health_results + health_runs tables |
| MCC Self-Health Settings UI sub-tab | ✅ Built OCB-A |
| /api/self-health/* endpoints (8) | ✅ Built OCB-A |
| mcc-popup-safe global CSS class | ✅ Built OCB-A |
| OCB-G Phase 1 (LLOW Arrow Drop Fix) | ✅ Arrow type check moved before LLOW.elements guard. Auto-connect on drop. |
| OCB-G Phase 2 (Colour Strategy Visibility) | ✅ Phase Flow 0.05→0.20, Element Mirror 0.07→0.18, Snap Glow 0.15-0.40. |
| mcc-instructions-keeper | ✅ 132 entries, GET /api/instructions, showInstructions() JS. |
| OCB-J: HC system checks | ✅ HC-01–HC-10 across self_health/system_monitor/work_checker |
| OCB-J: Safety Shield | ✅ Big badge green/red, 6 pills, 15s auto-poll |
| OCB-J: CLACHR Relay | ✅ Task Inbox → CLACHR, Dispatch All, 4 endpoints |
| OCB-J: /api/stuck/afna-suggestions | ✅ Serves afna_strategies.json |
| OCB-K finish: CLAUDE.md | ✅ Project orientation for Claude Code |
| OCB-K finish: data/project_awareness.json | ✅ Built from STATUS.md |
| OCB-L Phase 2 (System Monitor fix) | ✅ Dual-source polling, GPU grey N/A, LM Studio pill |
| OCB-L Phase 3 (AI Status Bar enriched) | ✅ 44px bar, location badges, click tooltip, 20s refresh |
| OCB-L Phase 4 (System Drill-Downs) | ✅ All 5 dials clickable, 5 /api/resources/* endpoints |
| OCB-L Phase 5 (Help Tab) | ✅ /api/help/ask SSE streaming, Q&A history |
| OCB-L Phase 6 (Settings Persistence) | ✅ data/mcc_settings.json, GET/POST /api/settings |
| OCB-M Phase 1 (LLOW LEL dblclick fix) | ✅ Manual dblclick detection, ghost drag fix |
| OCB-M Phase 2 (LLOW zone headers) | ✅ INPUT/PROCESS/OUTPUT colour-coded bar |
| OCB-M Phase 3 (GPU N/A verify+fix) | ✅ Correct N/A state, resets needle |
| OCB-M Phase 5 (Pie chart navigation) | ✅ Segments clickable → scroll+highlight slot |
| OCB-M Phase 6 (AI providers as LELs) | ✅ 11 providers in data/llow_elements.json |
| OCB-M Phase 7 (Health Suite drill-downs) | ✅ PFS expandable, score history bars clickable |
| OCB-M Phase 8 (Instructions restructure) | ✅ 3 accordion sections: INFORMATION/INSTRUCTIONS/CODES |
| OCB-M Phase 9 (AI Appendix) | ✅ Sortable table + radar charts (5 axes per provider) |
| OCB-N: Scout Swarm LEL | ✅ SCOUT_SWARM canvas node |
| OCB-N: Project Timeline builder | ✅ Work Checker Timeline panel |
| OCB-N: Work Checker 3 panels | ✅ Sessions, Checklist, Action Plan |
| OCB-N: ACCA Ticker | ✅ Persistent scrolling ACCA code ticker |
| OCB-O: Safety Watchdog indicator | ✅ Green pulsing dot, /api/watchdog/status, 10s poll |
| OCB-O: Global Search Bar | ✅ Ctrl+K, searches instructions/ACCA/elements/tabs |
| OCB-O: LLOW Alt+drag connector | ✅ Alt+mousedown draws animated connection line |
| OCB-O: LLOW fullscreen fix | ✅ Explicit inline styles override parent overflow |
| OCB-O: AI bar 15s + colour latency | ✅ Green<500ms, amber<2000ms, red>2000ms |
| OCB-O: AI Leaderboard populate fix | ✅ Falls back to /api/provider-health |
| OCB-O: ACCA colour coding | ✅ 5 categories, colour legend, category badge |
| OCB-O: AI Allocation panel | ✅ Per-process CPU+RAM bars, 5s poll |
| OCB-O Code Pipeline: Code Editor tab | ✅ Monaco 0.44.0 CDN, file browser, toolbar, output panel |
| OCB-O Code Pipeline: AAFL→Editor bridge | ✅ "Open in Code Editor" when result has code block |
| OCB-O Code Pipeline: CLAC Generator | ✅ Collapsible panel, 1-click copy, last 10 CLACs |
| OCB-O Code Pipeline: LLOW coding workflows | ✅ write_new_feature.json, fix_bug.json, refactor_file.json |
| OCB-O Code Pipeline: /api/code/* endpoints | ✅ files, read, save, run — all 4 monkey-patched |
| OCB-K Build 2 Phase 1 (Kanban B2-01+B2-02) | ✅ Sub-task progress bar. 🔒 icon + muted colour for blocked cards. Dependency chain display. AAFL Goal template. Bulk Archive + Move. |
| OCB-K Build 2 Phase 2 (Activity Feed B2-03) | ✅ 12 filters + Clear button + date range export picker. |
| OCB-K Build 2 Phase 3 (AAFL Runs B2-04+B2-05) | ✅ Checkbox compare, failure analysis, time-of-day success breakdown. |
| MCC freeze fix (v66) | ✅ `?.checked = false` SyntaxError fixed. Permanent ⟳ Reset MCC button. |
| OCB-O: OCB Runner (v67) | ✅ ocb_runner.py (503 lines), OCB Runner panel, 5 /api/ocb/* endpoints. |
| OCBR Lifeguard Protocol v0.1 (v68) | ✅ status_snapshots/, STATUS_MASTER.md, ocb_wal.log, data/ocb_queue.json. |
| wccs_detective.py — Chief Detective | ✅ v69 — scans all sources, writes detective_report_{date}.json. |
| mccm_agent.py — MCCM | ✅ v69 — power levels 1–4, approve/escalate. data/mccm_permissions.json. |
| /api/mccm/* endpoints (3) | ✅ v69 — status, detective, alerts |
| clacker_safety.py — CLACKER Safety Layer | ✅ v70 — pre_run, post_run_success/failure, check_html/py/server |
| clacker_validator.py — Acceptance Criteria Validator | ✅ v70 — validate() → PASS/FAIL/PARTIAL, writes clachr_response.json |
| mcc_server.py | ✅ v77 — +3 OCB-Runner v2 endpoints (rollback, checks, results) |
| RRCLACH panel (WCCS/HISAV tab) | ✅ v71 — classification pill after Generate RRCLACH |
| clacker_router.py | ✅ v71 — classify() + classify_all() |
| data/session_state.json | ✅ v71 — unified state |
| provider_health.py — run_diagnosis() | ✅ v71 — live-tests each provider |
| HISAV tab (replaces WCCS tab label) | ✅ v73 — 11-section accordion |
| HISAV S2: Idea Dump | ✅ v73 — EXPANDED by default, Ctrl+Enter save |
| HISAV S3: Vehicle History | ✅ v74 — PAST/PRESENT/PLANNED zones, TODAY marker (gold pulsing), scroll arrows |
| HISAV S4: Checklist Health | ✅ v73 — data/master_checklist.json, progress bars, click-to-tick |
| HISAV S5: Idea Buffer | ✅ v73 — age-colour cards, done/promote/dismiss buttons |
| HISAV S6: Action Plan | ✅ v73 — top 6 from STATUS.md NEXT PRIORITIES |
| HISAV S7: CLAC Sessions | ✅ v73 — CLAC logger + Screenshot Intake |
| HISAV S8: Screenshots | ✅ v73 — gallery thumbnails |
| HISAV S9: Work Checker | ✅ v73 — incomplete CLAC run tracker |
| HISAV S10: WENTO | ✅ v74 — WENTO queue panel |
| HISAV S11: OCB Runner v2 | ✅ v77 — 3-panel board: Reader (paste+parse), Runner (guards+live log), Results (file deltas+check A/B/C/D+MOT badge+diff+rollback btn) |
| HISAV sticky toolbar post-WCCS checklist | ✅ v75 — 4-step pill row |
| OCB-R1: Global z-index fix | ✅ v76 — all popups/tooltips z-index:99999 + position:fixed |
| OCB-R1: ? button audit | ✅ v76 — 30 tip-btn elements audited, all filled, 0 removed |
| OCB-R1: Post-save SESUM banner | ✅ v76 — green gradient panel, 3-step dismiss flow |
| OCB-Runner v2: parse_ocb() | ✅ v77 — extended parse: files_affected, risk_level (HIGH/MEDIUM/LOW), commands |
| OCB-Runner v2: pre_flight() | ✅ v77 — preview dict: files, risk, html_flag, warnings |
| OCB-Runner v2: run_safe() | ✅ v77 — 4 guards (Lock/Stash/Phases/Rollback) + 4 checks (BS4/JS/Registry/MOT) |
| OCB-Runner v2: read_results() | ✅ v77 — file line deltas, check results, git diff stat |
| OCB-Runner v2: stream_log() | ✅ v77 — timestamped live log with OCB_STATUS_FILE update |
| OCB-Runner v2: _check_js_integrity() | ✅ v77 — BS4-powered: missing functions + missing getElementById targets |
| OCB-Runner v2: _check_element_registry() | ✅ v77 — verifies all element_registry.json IDs exist in DOM |
| /api/ocb/rollback (POST) | ✅ v77 — git stash pop if rollback_available |
| /api/ocb/checks (GET) | ✅ v77 — returns latest check A/B/C/D results |
| /api/ocb/results (GET) | ✅ v77 — enriched run results with file deltas |
| beautifulsoup4 | ✅ v77 — installed (4.14.3) for HTML parsing in JS integrity check |
| Detective Panel A: Progress bars + Queue | ✅ v74 — per-task progress bars, task queue with drag-reorder, 7-strategy selector + WENTO |
| Detective Panel B: Inline drill-downs | ✅ v74 — every finding row clickable → Finding Detail/Evidence/Resolution/Recurrence/Timeline Link |
| Detective Panel A→B cross-link | ✅ v74 — "View findings (N) →" link filters Panel B by task |
| STORM Feed panel (detective section) | ✅ v74 — live 30s auto-refresh, severity + source filters |
| storm_bridge.py | ✅ v74 — StormBridge class: ingest/get_feed/get_summary |
| data/detective_queue.json | ✅ v74 — task queue storage (atomic write) |
| data/storm_feed.json | ✅ v74 — STORM unified data feed (max 1000 entries) |
| Panel E Screenshot rebuilt | ✅ v74 — det-browse-btn, document-level Ctrl+V paste guard |
| Timeline popup position:absolute fix | ✅ v75 — hisav-tl-popup changed from position:fixed to position:absolute |
| Global tooltip visibility fix | ✅ NEW v78 — all tooltip CSS z-index 9999→99999, tab bar z-index:100, positionTooltip() JS function, all 4 JS tooltip functions wired, [data-tooltip]::after CSS system, data-tooltip on all 13 tab buttons |
| aafl_wccs.py — AAFL-powered handover writer | ⏸ Specced — CLAC session B (DSP required) |
| Handover split migration | ⏸ CLAC session A |
| OCB-B — Body Map visual + Auto-Fix Engine | ⏸ Next build block |
| Throttle slider in War Thunder | ⏸ Open |
| Star Citizen full support | ⏸ Next benchmark |
| Wire aafl_wccs.py → STORM → Mission Launcher | ⏸ Next — STORM ↔ MCCM live loop |

---

## BIG VISION

**THE AAFL IS THE PROJECT NOW.** Spin Doctor is the benchmark and test subject — the first proof AAFL works. AAFL competes with LangGraph, CrewAI, AutoGPT as a self-improving AI agent framework. Story angle: *"beginner with BI builds self-improving AI agent."* Target communities: r/LocalLLaMA, GitHub, HackerNews. Post trigger: AAFL passes Star Citizen v0.2 benchmark via autonomous run.

Not a VKB-specific tool. A **universal input device assistant** — any hardware, any game, one tool.

> *"The tool that should have existed the moment the first joystick was ever plugged into a PC."*

**MCC is the cross-cutting cockpit layer** across all 6 projects — bidirectional, AAFL-powered. Reads same local files regardless of which Claude Project chat is open.

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

### MCC Server
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe mcc_server.py
```
Then open: http://localhost:8080

### MOT Test
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe mcc_full_mot.py
```

### MCU Optimizer (standalone)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe mcu_optimizer.py
```

### OCBR Lifeguard CLI
```
python ocb_runner.py --status
python ocb_runner.py --list
python ocb_runner.py --run OCB-K-Build3
python ocb_runner.py --sync-master
python ocb_runner.py --recover
```

### Chief Detective + MCCM CLI
```
python wccs_detective.py --investigate
python wccs_detective.py --propose
python wccs_detective.py --gaps
python mccm_agent.py --run
python mccm_agent.py --overview
python mccm_agent.py --power
python mccm_agent.py --alerts
```

### Bat Utilities
```
set_goal.bat "your goal here"
aafl_doctor.bat
regression_test.bat
queue_runner.bat
run_aafl.bat
meta_loop.bat
meta_loop.bat --apply
```

---

## MISSION CONTROL CENTER (MCC)

MCC is the single-pane-of-glass for all project activity. Served by mcc_server.py on localhost:8080.

### Core Tabs

| Tab | What it shows |
|---|---|
| Home | **Command Bar** (route tasks via CLACKER), **Attention Surface** (5 cards), Safety Shield, system dials, AI status bar |
| Kanban | Task board — B2 enhanced: progress bars, 🔒 deps, AAFL Goal template, bulk archive/move |
| AAFL Runs | Run history — B2 enhanced: checkbox compare, failure analysis, time-of-day success |
| Costs | Budget caps, spend graphs, ROI, currency toggle |
| Scout | Parallel web research — Scout Swarm LEL, presets, live results |
| AAFL Control | Run Now, Step Mode, Pause, Benchmark Runner, Second Opinion AI, Workflow Builder |
| Code Editor | Monaco 0.44.0, file browser, run .py, CLAC generator, AAFL bridge |
| Health Suite | Provider Health (Run Diagnosis + hover error tooltips), Self-Diagnosis, GPU/CPU/RAM, Medical, Work Checker |
| HISAV | **11-section accordion**: Save & Handoff, Idea Dump, Vehicle History, Checklist Health, Idea Buffer, Action Plan, CLAC Sessions, Screenshots, Work Checker, WENTO, OCB Runner v2 |
| Instructions | 3-section accordion: INFORMATION / INSTRUCTIONS / CODES + AI Appendix |
| ACCA | ACCA code table — colour coded by category |

### HISAV Tab — v77

| Section | Default | What it does |
|---|---|---|
| S1 Save & Handoff | Collapsed | All existing WCCS tools — save buttons, session log viewer, diff viewer, rewind, SESUM, RRCLACH, Chief Detective |
| S2 Idea Dump | **EXPANDED** | Large textarea + tags field. Ctrl+Enter saves. POST /api/hisav/idea |
| S3 Vehicle History | Collapsed | PAST/PRESENT/PLANNED zone bands, TODAY marker (gold pulsing), scroll arrows |
| S4 Checklist Health | Collapsed | data/master_checklist.json (5 cats, 25 items). Click cycles status. |
| S5 Idea Buffer | Collapsed | Cards from idea_buffer.json. Age-colour. Done/Promote/Dismiss buttons |
| S6 Action Plan | Collapsed | Top 6 from STATUS.md NEXT PRIORITIES. "Delegate to AAFL" per item |
| S7 CLAC Sessions | Collapsed | CLAC logger (Completed/Stopped, description, reason, version). Timeline integration. |
| S8 Screenshots | Collapsed | Screenshot drag-drop intake, gallery thumbnails, click-to-expand popup |
| S9 Work Checker | Collapsed | Incomplete CLAC run tracker |
| S10 WENTO | Collapsed | Whatever Else Not Thought Of queue panel |
| S11 OCB Runner v2 | Collapsed | v77 — 3-panel board: Reader → Runner → Results |

### HISAV S11 OCB Runner v2 — Architecture

Three sequential panels revealed as the workflow progresses:

| Panel | When visible | What it does |
|---|---|---|
| READER | Always | Paste textarea, Dry Run checkbox, Parse button (→ /api/ocb/parse), Clear button, phase preview table with risk badges |
| RUNNER | After parse | Confirm & Run button (→ /api/ocb/run), 6 guard status indicators (Lock/Stash/BS4/JS/Registry/MOT), live output scrolling log |
| RESULTS | After run | Files changed table (name/+lines/−lines), check results A/B/C/D with detail, MOT score badge (green/red), git diff accordion (50 lines), Rollback button (only if rollback_available) |

### OCB-Runner v2 Guards + Checks

| Guard | When | What it does |
|---|---|---|
| GUARD 1 — Lock | Start | Refuses if .ocb_running exists — prevents concurrent runs |
| GUARD 2 — Stash | Before edits | git status --porcelain; if dirty, git stash push -m OCB-Runner-{ts} |
| GUARD 3 — Phase execution | Per task | Sequential; stop on first fail; 120s timeout per phase |
| GUARD 4 — Rollback | On fail | git stash pop (if stash exists). On success: git stash drop + git commit |

| Check | File type | What it verifies |
|---|---|---|
| A — BS4 structure | .html only | BeautifulSoup parse must succeed without errors |
| B — JS integrity | .html only | Called functions in onclick/onchange attrs must exist as definitions in script blocks; getElementById targets must exist as DOM ids |
| C — Element registry | .html only | Every id in element_registry.json must exist in the HTML DOM |
| D — MOT | Always (if no prior fail) | mcc_full_mot.py must return 109/109 (or current passing count) |

### Global Tooltip Visibility System — v78

All tooltips in MCC now guaranteed to appear above all panels and the tab bar.

| Fix | What changed |
|---|---|
| CSS z-index | All tooltip classes bumped from z-index:9999 → 99999. Tab bar set to z-index:100. |
| positionTooltip() | New global JS function — smart positioning with TAB_BAR_HEIGHT=60 guard, viewport edge detection |
| b3ShowTip() | Wired to positionTooltip(). z-index in cssText 9999→99999. |
| shTip() | window.scrollY bug fixed (invalid for position:fixed). Wired to positionTooltip(). |
| showInstructions() | z-index 9999→99999. Wired to positionTooltip(). |
| _showTip() (BodyMapTracker) | Viewport edge + TAB_BAR_HEIGHT guard added. bm-tooltip CSS z-index 8000→99999. |
| [data-tooltip]::after | New CSS system added. All 13 tab buttons got data-tooltip attributes. |
| .sh-popup | Changed position:absolute → position:fixed in CSS. |
| [class*="tooltip"]/[class*="popup"] | Changed position:absolute → position:fixed in OCB-E CSS block. |

### Detective Status Board — v74

| Panel | What it does |
|---|---|
| Panel A | Progress bars per task, task queue with drag-reorder, 7-strategy selector + WENTO custom text |
| Panel B | Every finding row → inline drill-down (Finding Detail/Evidence/Resolution/Recurrence/Timeline Link) |
| Panel C | Open failures with dismiss button |
| Panel D | Learning database — count + last 5 entries |
| Panel E | Screenshot intake — det-browse-btn, Ctrl+V paste, thought-bubble output |
| STORM Feed | Live scroll of all detective/WCCS/screenshot entries. 30s auto-refresh. |

### New Endpoints (v77 — 3 added)

| Method | Path | Purpose |
|---|---|---|
| POST | /api/ocb/rollback | git stash pop if rollback_available in last run |
| GET | /api/ocb/checks | Latest check A/B/C/D results from _check_results |
| GET | /api/ocb/results | Enriched run results: file deltas, checks, git diff stat |

### Emergency Reset Button
Permanent red **⟳ Reset MCC** button (bottom-left, position:fixed). Closes all overlays, hides floating popups, resets LLOW fullscreen, navigates to HISAV tab.

---

## ENGINE ARCHITECTURE — MICROKERNEL

Drop a .py file into `/problems/` — engine picks it up automatically.

| Module ID | Name | Problems covered | Status |
|---|---|---|---|
| spin_fix | Spin Bug (Mouse Axis) | Removes mouse double-bind from flight axes | ✅ Working (War Thunder) |
| usb_power_saver | USB Power Saver | Disables Windows USB port power-off mid-session | ✅ Built |
| steam_input_conflict | Steam Input Conflict | Turns Steam Input OFF for WT, ED, MSFS, DCS, IL-2, AC7 | ✅ Built |
| conductor | Process Conductor | 22 problems — companion software, input mappers, overlays, launch order | ✅ Built |
| win_hardener | Windows Hardener | 9 problems W-001→W-009 | ✅ Built |
| ed_bind_reset | ED Bind Reset prevention | Prevents Elite Dangerous from resetting custom bindings | ✅ Built |

---

## PROJECT FILES

```
VKB-SpinDoctor/
├── spin_doctor.py
├── sfl_agent.py                       # v3 — HANDOVER_FILENAME → v78
├── aafl_core.py                       # v71 — OpenRouter fix, 503 retry, provider_timeout
├── loop_manager.py                    # v71 — session_state updates
├── evaluator.py
├── researcher.py
├── memory_bank.py
├── cost_guard.py
├── meta_loop.py
├── mcu_optimizer.py
├── dashboard_builder.py
├── task_router.py
├── chief_scout.py                     # v69 — get_project_context() + --no-context flag
├── self_health.py
├── system_monitor.py
├── work_checker.py
├── provider_health.py                 # v71 — run_diagnosis(), session_state update
├── clacker_router.py                  # v71 — classify() + classify_all()
├── ocb_runner.py                      # v77 — +v2 API: parse_ocb/pre_flight/run_safe/read_results/stream_log + 4 checks
├── clacker_safety.py                  # v70 — pre_run, post_run_success/failure, check_html/py/server
├── clacker_validator.py               # v70 — validate(criteria, files_changed, mot_score) → PASS/FAIL/PARTIAL
├── wccs_detective.py                  # v69 — Chief Detective: scans all sources, gap analysis
├── mccm_agent.py                      # v69 — MCCM overseer, power levels 1-4, AI dispatch
├── storm_bridge.py                    # v74 — StormBridge class: ingest/get_feed/get_summary
├── ocb_wal.log                        # v68 — Write-Ahead Log (append only)
├── STATUS_MASTER.md                   # v68 — golden STATUS.md backup post-MOT
├── mcc_server.py                      # v77 — +3 OCB-Runner v2 endpoints (rollback/checks/results)
├── mcc_full_mot.py                    # 109 tests, GROUP A-H
├── aafl_wccs.py                       # v73 — archive_old_handovers() wired
├── mission_control.html               # v78 — global tooltip visibility fix (z-index, positionTooltip, data-tooltip)
├── CLAUDE.md
├── ACCA.md
├── ALP_Database.md
├── STATUS.md
├── HISTORY.md
├── INDEX.md
├── goal.txt / goal_queue.txt / meta_queue.txt
├── aafl_config.json
├── VKB_SpinDoctor_Handover_v78.md     # This file
├── data/
│   ├── knowledge_engine.db
│   ├── health.db
│   ├── ocb_status.json
│   ├── ocb_queue.json
│   ├── rrclach_request.json
│   ├── rollback_log.json
│   ├── clachr_response.json
│   ├── session_state.json
│   ├── provider_diagnosis.json
│   ├── mccm_permissions.json
│   ├── detective_report_{date}.json
│   ├── detective_queue.json           # v74 — task queue (atomic write)
│   ├── storm_feed.json                # v74 — STORM unified feed (max 1000 entries)
│   ├── mccm_investigations/
│   ├── element_registry.json
│   ├── solution_database.json
│   ├── instructions_db.json
│   ├── llow_elements.json
│   ├── llow_workflows/
│   ├── mcc_settings.json
│   ├── project_awareness.json
│   ├── project_timeline.json
│   ├── master_checklist.json
│   ├── idea_buffer.json
│   ├── mot_gaps.json
│   ├── clac_sessions.json
│   ├── screenshot_log.json
│   ├── screenshots/
│   └── ...
├── status_snapshots/
├── problems/
│   ├── conductor.py
│   ├── ed_bind_reset.py
│   └── win_hardener.py
├── data/llow_workflows/
│   ├── write_new_feature.json
│   ├── fix_bug.json
│   ├── refactor_file.json
│   └── ...
├── session_logs/
├── loop_output/
├── health_results/
└── archive_dead/
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
| Packages | mss, lmstudio, Pillow, anthropic, litellm, python-dotenv, langgraph, ddgs, beautifulsoup4 |
| API model | claude-sonnet-4-6 |
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
| `localhost:8080` refused | Run `python mcc_server.py` first |
| MCC completely frozen | Click ⟳ Reset MCC button (bottom-left, red). If not: hard-refresh (Ctrl+Shift+R) |
| Detective Panel B shows no drill-down | Click the row (not the dismiss button) — inline div toggles below the row |
| STORM Feed shows "unavailable" | mcc_server.py must be running — feed loaded from /api/storm/feed |
| Timeline popup covers other tabs | Fixed v75 — popup now position:absolute within #htl-tl-wrapper |
| Paste not working in Panel E | HISAV tab must be active AND detective panel must be open (toggled) |
| Popup hidden behind panel | Fixed v76 — OCB-R1 global z-index CSS forces all popups to z-index:99999 + position:fixed |
| Tooltip hidden behind tab bar | Fixed v78 — tab bar z-index:100, all tooltips z-index:99999, positionTooltip() guards TAB_BAR_HEIGHT |
| Post-save banner not showing | Triggered by saveSession() or copyStatusForClaude() success — check JS console |
| OCB Runner v2 shows BLOCKED | .ocb_running lock file exists — another run is in progress or crashed. Delete it manually. |
| OCB Runner v2 ROLLED BACK | CHECK B (JS) or CHECK C (Registry) failed — see Results panel for missing function/ID names |
| Rollback button not visible | Only appears if rollback_available=True in status (run failed AND stash exists) |
| CHECK B fails with missing_functions | A function called in an onclick attribute is not defined in any script block — check the name |
| bs4 import error | Run: pip install beautifulsoup4 |

---

## WHAT NOT TO DO

- Don't rebuild anything marked ✅ — it exists, find the file
- Don't add multiple games at once — one game, test fully, then next
- Don't commit to GitHub without Scott's explicit decision
- Don't auto-flash firmware — warn and guide only, never auto-flash
- Don't rebuild from scratch — extend what's there
- API credits can burn completely in one bad loop — cost_guard is the safeguard
- Don't pass --apply to meta_loop without reading the proposal first
- **NEVER delete old handover files** — always move to archive_dead/ instead
- Don't open multiple CLAC terminals at once — they share the ALP pool

---

## NEXT PRIORITIES

1. Test OCB Runner v2 end-to-end in MCC — open HISAV S11, paste a small OCB block, Parse, then Dry Run
2. Complete STORM ↔ MCCM live loop testing
3. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
4. Test HISAV detective tab live in MCC — open Panel A, add a GHOST_FILE task, run it, click Panel B finding
5. OCB-K Build 3 — Costs tab enhancements, Scout improvements, parking lot features
6. Star Citizen v0.2 benchmark via AAFL autonomous run (proof of concept #2)
7. Add GROQ + Cloudflare keys to .env (manual — security rule)
8. Polish AASKC for ship — README, demo video, r/LocalLLaMA post
9. LiteLLM full integration — replace direct provider calls with LiteLLM router
10. Electron wrapper for packaging

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
6. Run `python mcu_optimizer.py` — reads new handover + last 3 session logs + mission_control_tasks.json, updates board, prints diff
7. Update `HANDOVER_FILENAME` in `sfl_agent.py` to point to the new version

**NEVER-DELETE rule:** Old handovers are never deleted. Move to `archive_dead/` only.
**AUTO-ARCHIVE rule:** aafl_wccs.py now automatically moves any VKB_SpinDoctor_Handover_v*.md from root to archive_dead/ on every WCCS run.

---

## RESUME COMMAND

> "Continuing VKB Spin Doctor. Read VKB_SpinDoctor_Handover_v78.md. v78 session — Global tooltip/info visibility fix for entire MCC: (1) CSS z-index on all tooltip classes bumped 9999→99999 (.tooltip-wrap .tip / [data-tip]::after / .bm-tooltip / .tip-box / .mcc-popup-safe / .sh-popup / .mcc-tooltip / .hisav-popup-safe / .tip-pop); (2) Tab bar (.tab-bar) set to z-index:100 + position:relative so tooltips (99999) always float above it; (3) positionTooltip(tooltipEl, triggerEl) global JS function added at top of main script — smart viewport positioning with TAB_BAR_HEIGHT=60 guard; (4) All 4 JS tooltip functions wired: b3ShowTip() uses positionTooltip + z-index 99999, shTip() removes window.scrollY bug + uses positionTooltip, showInstructions() z-index 99999 + positionTooltip, _showTip() (BodyMapTracker) adds viewport + TAB_BAR_HEIGHT guard; (5) [data-tooltip]::after CSS system added to stylesheet; data-tooltip attributes added to all 13 tab buttons and separators in main-tab-bar; (6) New global float rule added ensuring [data-tooltip]:hover::after + .mcc-tooltip-text + .goeb-content + .tab-info-bubble all use position:fixed !important z-index:99999; (7) .sh-popup changed from position:absolute to position:fixed in CSS; (8) OCB-E CSS block updated: [class*='tooltip']/[class*='popup'] changed from position:absolute to position:fixed. 109/109 MOT ALL CLEAR."

---

## CHAT LOG
<!-- Append new entries below. Never delete. Never overwrite. -->

### 2026-05-17
**Key decisions:** Cerebras model chain llama3.1-70b → llama-3.3-70b (both deprecated) → gpt-oss-120b (current stable). reasoning_content fallback for all reasoning models. Cloudflare needs two env vars (CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID). Groq auth is API key only. win_hardener follows conductor.py API contract. Queue runner uses separate .py file to avoid batch special-character issues.
**New ACCA codes:** None
**Ideas discussed:** CHAT LOG section for permanent handover history. goal_queue.txt for overnight batch runs. Completion notification via stdlib winsound + ctypes MessageBoxW.
**Next priorities:** Star Citizen full support. Add GROQ_API_KEY to .env. Add Cloudflare keys to .env.

---

### 17 May 2026

**Key decisions:**
- AAFL first successful run confirmed — proof of concept PASSED. Cost £0.0027. Gemini planned, Mistral worked.
- Cerebras fixed: llama3.1-70b → llama-3.3-70b → gpt-oss-120b (final correct model, confirmed PASS 0.54s)
- All 7 CA tasks completed this session
- AAFL will handle all game-specific tasks (Star Citizen etc) once fully autonomous
- Chat WCCS process agreed: WCCS in Chat → I generate Chat Summary → Scott pastes into CLAC → appends to CHAT LOG
- PROF added as ACCA Shorthand for Project Files

**New ACCA codes:**
- DSP = Dangerously Skip Permission
- AFNA = Attack From New Angle
- PROF = Project Files (Shorthand section)

**Ideas discussed:**
- Monetization: Ko-fi, Itch.io PWYW, GitHub Sponsors, Patreon, YouTube, Freemium £5 Pro
- Fastest path to first £: Itch.io + Ko-fi link in README — 30 minutes work
- pin ACCA = command to show ACCA table in Chat right panel anytime

**Next priorities:**
1. Fix verify step
2. Fix Groq auth
3. Test queue_runner.bat with 3 goals overnight
4. Get Spin Doctor public on GitHub when ready
5. Add Ko-fi + Itch.io links to README

---

### 2026-05-18
**Key decisions:** AAFL first real autonomous runs confirmed working. 4 bugs fixed in loop_manager.py. Mission Control board built. run_aafl.bat built.
**New ACCA codes:** None this session
**Ideas discussed:** Xbox + VKB dual input in Star Citizen. Workflow tracker as local HTML file.
**Next priorities:** 1. Fix scout web search quality 2. Run Star Citizen job 3. Test run_aafl.bat end to end

---

### 2026-05-18 (Chat session 2)
**Key decisions:** Mission Statement formalised — 9 rules, ALP is Rule No.1. SuperClaude concept defined. AAFL confirmed as workhorse strategy.
**New ACCA codes:** WRS = Write Software. MCU = Mission Control Update.
**Next priorities:** 1. Paste tasks 1-4 CLAC block 2. Add GROQ key manually 3. Add Cloudflare keys manually

---

### 2026-05-18 (Claude Code session 2)
**Key decisions:** AAFL self-improving meta-loop built. meta_loop.py, meta_queue.txt, meta_loop.bat. Cerebras model bug found and fixed.
**New ACCA codes:** None
**Bugs fixed:** Cerebras model in aafl_core.py was still `llama-3.3-70b` (deprecated) — fixed to `gpt-oss-120b`.
**Next priorities:** 1. Review meta_proposals 2. Run meta_loop again 3. Add API keys

---

### 2026-05-18 (Claude Code session 3)
**Key decisions:** meta_loop.py work-step real-data injection fixed. _inject_file_context 100→600 lines, _inject_db_context 4→14 keywords, _inject_loop_reports() added.
**Bugs fixed:** meta_loop.py data injection broken in 3 ways.
**Next priorities:** 1. Re-add goals 2+3 to meta_queue.txt 2. Add API keys

---

### 2026-05-18 (Claude Code session 4)
**Key decisions:** mcu_optimizer.py built and tested. Reads handover + session logs + tasks JSON, LLM reorganises, diffs and writes back. Safety rules: never invents/deletes/touches Done.
**Bugs fixed:** mcu_optimizer.py: result.cost → result.cost_usd; unicode arrows → ASCII.
**Next priorities:** 1. Re-add meta goals 2. Add API keys 3. Star Citizen

---

### 2026-05-18 (Claude Code session 5)
**Key decisions:** Central Command (MCC) designed and built. dashboard_builder.py + mission_control.html 4-tab Central Command.
**New ACCA codes:** WRC = Write-Run-Check. MCC = Mission Control Center.
**Next priorities:** 1. Re-add meta goals 2. Add API keys 3. Star Citizen

---

### 2026-05-18 (Claude Code session 5)
**Key decisions:** WCCS automation system built: wccs_runner.py, mcc_server.py, mission_control.html, WCCS.bat.
**Next priorities:** 1. Open mission_control.html 2. Re-add meta goals 3. Add API keys

---

### 2026-05-18 (Claude Code session 6)
**Key decisions:** WCCS automation system built. DSP rule agreed. WCCS fully delegated to AAFL.
**Next priorities:** 1. Add DSP rule to handover 2. Scott decides MCC layout 3. Build MCC redesign

---

### 2026-05-19 (Claude Code session 1)
**Key decisions:** MCC confirmed — still controls all projects after split. Full conversation detective search done. task_router.py confirmed built. DSP rule added to WHO IS SCOTT.
**Next priorities:** 1. Sign up xAI Grok 2. Upload v39 to Project Files 3. Execute 5-project split

---

### 2026-05-19 (Chat session — Master Project strategy)
**Key decisions:** MAJOR REFRAME: AAFL IS the project. Spin Doctor is the benchmark/test subject. Master + 5 sub-projects (6 total) confirmed. merge_sessions.py chosen (Option 2).
**Next priorities:** 1. Build merge_sessions.py + .bat 2. Execute 5-project split 3. Star Citizen benchmark

---

### 2026-05-19 (Claude Code session 2)
**Key decisions:** WCCS only — no new code. 5 new MCC features planned. ALP memory consolidated.
**Next priorities:** 1. Build merge_sessions.py 2. Execute 5-project split 3. Build 5 new MCC features

---

### 2026-05-19 (Claude Code session 4)
**Key decisions:** AAFL Control Panel tab built for MCC. 6 tasks: aafl_control_config.json, 10 new endpoints, aafl_output/, AAFL Control tab (7th tab), smoke test PASSED.
**Next priorities:** 1. Build aafl_wccs.py 2. Build merge_sessions.py 3. Execute 5-project split

---

### 2026-05-19 (Claude Code session 3)
**Key decisions:** WCCS only — capturing Chat session. CAWPA added. WCCS 3-stage reliability upgrade designed.
**New ACCA codes:** CAWPA = Completely Automate Whats Possible by AI
**Next priorities:** 1. Build aafl_wccs.py 2. Build merge_sessions.py 3. Execute 5-project split

---

### 2026-05-19 (Chat session — Chief Scout + MCC Mega-Upgrade)
**Key decisions:** Chief Scout parallel agent system BUILT. Scout Control Panel BUILT. Full 29-job list compiled. MCC MEGA-UPGRADE brainstormed.
**Next priorities:** 1. Build aafl_wccs.py 2. Build merge_sessions.py 3. MCC Mega-Upgrade

---

### 2026-05-20 (Chat session — v44 truncation fix + handover redesign)
**Key decisions:** v44 confirmed truncated. NEVER-DELETE rule established. Handover split architecture designed. aafl_wccs.py full build spec written.
**New ACCA codes:** CAP = Copy and Paste
**Next priorities:** 1. CLAC session A — migrate to split structure 2. CLAC session B — build aafl_wccs.py

---

### 2026-05-27 (Claude Code session 1)
**Key decisions:** OCB-A — MCC Self-Health System foundation complete. 7 phases built.
**New ACCA codes:** OCB = One-Claude-Build
**Bugs fixed:** class MCCHandler(MCCHandler) Python error — fixed with monkey-patching. Unicode crash — replaced with ASCII.
**Next priorities:** 1. OCB-B 2. CLAC session A 3. CLAC session B 4. Star Citizen

---

### 2026-05-28 (Claude Code session 3)
**Key decisions:** OCB-G — Fix LLOW arrow drop bug + colour strategy opacity. 108/108 MOT ALL CLEAR.
**Bugs fixed:** llowOnDrop LLOW.elements guard blocking arrow drops. Colour strategy overlays invisible.
**Next priorities:** 1. Star Citizen 2. OCB-B 3. CLAC sessions A+B

---

### 2026-05-28 (Claude Code session 6)
**Key decisions:** mcc-instructions-keeper system built. 132 entries, 2 endpoints, showInstructions() JS, 7 ? buttons, skill file. 108/108 MOT ALL CLEAR.
**Next priorities:** 1. Upload SKILL.md to Project Files 2. Star Citizen 3. OCB-B

---

### 2026-05-28 (Claude Code session 7)
**Key decisions:** OCB-J built — HC-01–HC-10, Safety Shield, CLACHR Relay, /api/stuck/afna-suggestions, SUMMARY.md, CLACHR ACCA code. 108/108 MOT ALL CLEAR.
**New ACCA codes:** CLACHR = CLACH Relay
**Next priorities:** 1. Upload SKILL.md 2. OCB-B 3. CLAC sessions A+B

---

### 2026-05-28 (Claude Code session 8)
**Key decisions:** OCB-L built — 7 phases: CLAUDE.md, system monitor fix, AI status bar enriched, drill-downs, Help tab, Settings persistence. 108/108 MOT ALL CLEAR.
**Bugs fixed:** System monitor crash on missing GPU data. Settings lost on MCC HTML rewrite.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 1)
**Key decisions:** OCB-M built — 10 phases: LLOW dblclick fix, zone headers, GPU N/A verify, Help tab verify, pie chart navigation, AI providers as LELs, Health Suite drill-downs, Instructions restructure, AI Appendix. 108/108 MOT ALL CLEAR.
**New ACCA codes:** LLC = Loop Law Chain
**Bugs fixed:** LLOW LEL dblclick (DOM re-render race). GPU drill-down blank. Pie chart non-interactive. LLOW zone categories missing ai_providers.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 2)
**Key decisions:** OCB-M built — duplicate entry, see session 1.
**Next priorities:** same as session 1.

---

### 2026-05-29 (Claude Code session 3)
**Key decisions:** test chat text for recovery check
**New ACCA codes:** None
**Bugs fixed:** None
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 4)
**Key decisions:** OCB-O built — 15 fixes across 5 phases. Safety Watchdog indicator, Global Search (Ctrl+K), LLOW Alt+drag connector, fullscreen fix, CPU/RAM error fix, AI Leaderboard fix, AI bar 15s + colour latency, medical history fix, ACCA colour coding, AI Allocation panel, vertical section sliders, tab bar scroll arrows. 108/108 MOT ALL CLEAR.
**Bugs fixed:** CPU/RAM showing red on psutil error. AI Leaderboard blank. LLOW fullscreen not expanding. Medical history showing no runs.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 5)
**Key decisions:** OCB-O Code Pipeline built — 5 phases. Monaco Code Editor tab, AAFL→Editor bridge, CLAC Generator, 3 LLOW coding workflows, 4 /api/code/* endpoints. 108/108 MOT ALL CLEAR.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 6)
**Key decisions:** OCB-K Build 2 complete — 4 phases. Kanban progress bars/🔒 deps/AAFL Goal template/bulk archive+move, Activity 12-filters+Clear+date-range, AAFL Runs checkbox-compare+failure-phases+time-of-day. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** Activity filter categories wrong vs spec. b2BulkMove only moved to Done. Research template replaced with AAFL Goal.
**Next priorities:** 1. OCB-K Build 3 2. Star Citizen 3. Add GROQ + Cloudflare keys

---

### 2026-05-29 (Claude Code session 17)
**Key decisions:** MCC complete freeze diagnosed and fixed. Root cause: `?.checked = false` SyntaxError. Fixed + fullscreen guard + localStorage safety + permanent ⟳ Reset MCC button. 108/108 MOT ALL CLEAR.
**Bugs fixed:** `?.checked = false` SyntaxError in b2RunCmpSelect() line 9899.
**Next priorities:** 1. OCB-K Build 3 2. Star Citizen 3. Add GROQ + Cloudflare keys

---

### 2026-05-29 (Claude Code session 18)
**Key decisions:** OCB-O OCB Runner built. ocb_runner.py (503 lines), 5 new endpoints, full OCB Runner panel in WCCS tab. 108/108 MOT ALL CLEAR.
**Bugs fixed:** Windows console encoding crash (→ character).
**Next priorities:** 1. Test OCB Runner end-to-end 2. OCB-K Build 3 3. Star Citizen

---

### 2026-05-29 (Claude Code session 20)
**Key decisions:** OCBR Lifeguard Protocol v0.1 built. Six safety mechanisms: status_snapshots/, STATUS_MASTER.md, ocb_wal.log, data/ocb_queue.json, ocb_runner.py +8 functions + argparse CLI, aafl_wccs.py wired.
**New ACCA codes:** OCBR = OCB Runner (Lifeguard Protocol build tool)
**Bugs fixed:** generate_clac_block UnicodeEncodeError on Windows cp1252.
**Next priorities:** 1. OCB-K Build 3 2. Star Citizen 3. Add GROQ + Cloudflare keys

---

### 2026-05-29 (Claude Code session 21)
**Key decisions:** Chief Detective + MCCM built. wccs_detective.py + mccm_agent.py + 3 new endpoints + Chief Detective + MCCM panel in WCCS tab.
**New ACCA codes:** MCCM = Mission Control Center Master
**Next priorities:** 1. OCB-K Build 3 2. Star Citizen 3. Add GROQ + Cloudflare keys

---

### 2026-05-29 (Claude Code session 22)
**Key decisions:** CLACKER Safety Layer built — clacker_safety.py + clacker_validator.py + ocb_runner.py integration. 108/108 MOT ALL CLEAR.
**New ACCA codes:** RRCLACH = Run Request CLACH
**Next priorities:** 1. Test OCB Runner with RRCLACH 2. OCB-K Build 3 3. Star Citizen

---

### 2026-05-29 (Claude Code session 23)
**Key decisions:** OCB-P built — 6 phases of CLACKER Router + cockpit infrastructure. clacker_router.py, session_state.json, Command Bar + Attention Surface cockpit, Provider Diagnosis, NEEDS_OPUS detection + Retry failed phases, aafl_core.py 503 retry. 108/108 MOT ALL CLEAR.
**Next priorities:** 1. Test Command Bar + Attention Surface 2. Test NEEDS_OPUS 3. OCB-K Build 3

---

### 2026-05-30 (Claude Code session 1)
**Key decisions:** OCB-P v72 completion fixes — /api/provider-diagnosis endpoint, phLoadDetail() hover tooltips, sidebar Quick Stats from session_state. 108/108 MOT ALL CLEAR.
**Bugs fixed:** phLoadDetail errMap always empty. Sidebar Quick Stats sb-last-save wrong DOM element.
**Next priorities:** 1. Test provider hover errors 2. Test sidebar Quick Stats 3. OCB-K Build 3

---

### 2026-05-30 (Claude Code session 2)
**Key decisions:** HISAV tab built — WCCS tab renamed HISAV. 7-section accordion (→ now 9 sections). 5 new DTA data files. 8 new API endpoints. archive_old_handovers() wired in aafl_wccs.py — 16 handover files moved to archive_dead/. .tl-detail-popup CSS class added globally. 109/109 MOT ALL CLEAR.
**New ACCA codes:** HISAV = History + Ideas + Save. DTA = Data As Truth Architecture.
**Next priorities:** 1. Test HISAV tab live 2. Test CLAC Session logger 3. OCB-K Build 3 4. Star Citizen

---

### 2026-05-30 (Claude Code session 8)
**Key decisions:** OCB-Q Combined (Q2+Q3) built — 9 phases. (1) Rogue popup kill: explicit display:none on hisav-tl-popup, paste guard only fires when HISAV tab active and detective panel open. (2) Detective Panel A: progress bar strip per active task, task queue with drag-reorder, 7-strategy selector + WENTO custom instruction. (3) Panel B: every finding row clickable → inline drill-down (Finding Detail, Evidence, Resolution, Recurrence, Timeline Link). Border colour by severity. (4) Panel A→B cross-link: "View findings (N) →" link filters Panel B, grey-out others, pulsing border on matches. (5) STORM + MCCM: storm_bridge.py (StormBridge class), data/storm_feed.json, live STORM feed panel (30s auto-refresh), 3 /api/storm/* endpoints + /api/missions/update-from-sesum. (6) Panel E rebuilt: det-browse-btn, Ctrl+V paste guard, thought-bubble layout. (7) Timeline visual upgrade: PAST/PRESENT/PLANNED zone bands, TODAY marker (gold gradient, pulsing), scroll arrows (htlScrollBy), auto-scroll to current node, height:280px. (8) STATUS.md BUILT table + 2 new NEXT PRIORITIES. (9) 109/109 MOT ALL CLEAR. Commit: c0bba13.
**New ACCA codes:** STORM = Selective Targeted Output Remove Merge (unified data feed from detective/WCCS/screenshots)
**Bugs fixed:** DOMContentLoaded called detLoadPanels regardless of panel visibility — removed auto-call, now only fires on explicit toggle. Paste handler triggered even when HISAV tab wasn't active — fixed with `.classList.contains('active')` guard.
**Ideas discussed:** STORM as unified data backbone for all project telemetry — detective findings, WCCS saves, screenshot analyses all feed into one stream. StormBridge class makes ingest/query available to any Python script.
**Next priorities:**
1. Complete STORM ↔ MCCM live loop testing
2. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
3. Test detective tab live — add GHOST_FILE task, run, click Panel B finding drill-down
4. OCB-K Build 3 — Costs tab enhancements, Scout improvements
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-30 (Claude Code session 9)
**Key decisions:** HISAV post-WCCS checklist added to sticky toolbar — 4-step pill row always visible at top of HISAV pane: (1) Run WCCS, (2) Post SESUM to HISAV, (3) Update Project Files in Claude (tooltip with full instructions + 📋 Copy path button copies project folder path to clipboard), (4) Start new chat (links to https://claude.ai in new tab). Each pill toggles grey/green on click; state resets on page reload. Timeline popup (hisav-tl-popup) fixed from position:fixed to position:absolute within new #htl-tl-wrapper container — popup no longer floats over other tabs; JS positioning updated to use container-relative coordinates. 109/109 MOT ALL CLEAR. Commit: a884578.
**New ACCA codes:** None
**Bugs fixed:** hisav-tl-popup used position:fixed which caused it to cover content on other tabs when scrolling. Fixed by adding #htl-tl-wrapper position:relative container and overriding CSS with #hisav-tl-popup{position:absolute!important}.
**Ideas discussed:** Post-WCCS checklist as a persistent, always-visible reminder of the 4 end-of-session steps — no memory required, just click each pill as you complete it.
**Next priorities:**
1. Complete STORM ↔ MCCM live loop testing
2. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
3. Test HISAV detective tab live — add GHOST_FILE task, run, click Panel B finding drill-down
4. OCB-K Build 3 — Costs tab enhancements, Scout improvements
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-30 (Claude Code session 12)
**Key decisions:** OCB-R1 global MCC bug sweep — 4 fixes applied. (1) Global z-index CSS block added as last rule in `<style>`: forces all popups/tooltips/flyouts to z-index:99999 + position:fixed; inline drill-downs excepted with position:relative + z-index:auto; 5 section wrappers changed overflow:hidden → overflow:visible (.aafl-acc, .accordion-item, .qa-panel, .wc-panel, .llow-loop-acc). (2) ? button audit — 30 tip-btn elements found, all had content (b3ShowTip/shTip/showInstructions), 0 removed, 0 needed filling. (3) Post-save SESUM reminder banner (#post-save-banner) added below hisav-summary-panel: green gradient panel, 3-step dismiss flow (1 Copy SESUM → 2 Paste → 3 Open Claude); showPostSaveBanner() called from both saveSession() success branch AND copyStatusForClaude() success branch. (4) MOT 109/109 ALL CLEAR. Commit: 9aa9a7d.
**New ACCA codes:** None
**Bugs fixed:** Popups hidden behind panels due to z-index stacking context — fixed globally. overflow:hidden on section wrappers clipping tooltip edges — fixed on 5 wrappers.
**Ideas discussed:** Global z-index fix as a one-shot CSS solution for all future popup additions — any element with "popup" or "tooltip" in its class name will automatically render above everything.
**Next priorities:**
1. Complete STORM ↔ MCCM live loop testing
2. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
3. Test HISAV detective tab live — add GHOST_FILE task, run, click Panel B finding drill-down
4. OCB-K Build 3 — Costs tab enhancements, Scout improvements
5. Star Citizen v0.2 benchmark via AAFL autonomous run

---

### 2026-05-31 (Claude Code session 1)
**Key decisions:** OCB-Runner v2 built — complete upgrade to ocb_runner.py and HISAV Section 11. (1) parse_ocb(): extended parse returning files_affected, risk_level (HIGH for HTML, MEDIUM for .py, LOW for .json/.md), commands. (2) pre_flight(): preview dict with html_flag, warnings ("JS integrity check will run after edit"). (3) run_safe(): 4 guards (Lock=.ocb_running file check, Stash=git status --porcelain → git stash push, Phase=sequential exec stop-on-fail, Rollback=git stash pop on fail / stash drop + commit on success) + 4 checks (A=BS4 parse, B=JS integrity via onclick attr scanning vs function defs + getElementById targets vs DOM ids, C=element_registry.json vs DOM, D=MOT 109/109). (4) read_results(): file delta table (git diff --numstat). (5) stream_log(): live append to OCB_STATUS_FILE for polling. (6) HISAV S11 rebuilt as 3-panel board: Reader panel (textarea + Dry Run checkbox + Parse → /api/ocb/parse → risk table), Runner panel (Confirm & Run + 6 guard pills: Lock/Stash/BS4/JS/Registry/MOT + live log), Results panel (file delta table + check A/B/C/D rows + MOT badge + git diff accordion + Rollback button). (7) 3 new server endpoints: POST /api/ocb/rollback, GET /api/ocb/checks, GET /api/ocb/results. (8) Updated: /api/ocb/parse → parse_ocb()+pre_flight(), /api/ocb/run → run_safe(), /api/ocb/status → merges live_output+guard_results from module. (9) beautifulsoup4 4.14.3 installed. 109/109 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** None (net-new feature build)
**Ideas discussed:** JS integrity check as a critical safety gate — prevents broken onclick handlers by verifying all called functions are defined before committing any HTML edit. Element registry check closes the loop: any MCC element removed by an AI edit is caught immediately.
**Next priorities:**
1. Test OCB Runner v2 end-to-end in MCC — open HISAV S11, paste a small OCB block, Parse, then Dry Run
2. Complete STORM ↔ MCCM live loop testing
3. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
4. Test HISAV detective tab live in MCC — Panel A task, Panel B finding drill-down
5. OCB-K Build 3 — Costs tab enhancements

---

### 2026-05-31 (Claude Code session 2)
**Key decisions:** Global tooltip/info visibility fix for entire MCC. (1) CSS: all tooltip z-index values bumped 9999→99999 across 10 rules (.tooltip-wrap .tip, [data-tip]::after, .bm-tooltip, .tip-box, .mcc-popup-safe, .sh-popup, .mcc-tooltip OCB-E block, .hisav-popup-safe, .tip-pop, OCB-R1 block already at 99999). (2) Tab bar (.tab-bar) set to z-index:100 + position:relative so all tooltips (99999) always render above it. (3) positionTooltip(tooltipEl, triggerEl) global JS function added at start of main script — smart viewport positioning with TAB_BAR_HEIGHT=60 guard, opens below trigger by default, flips above if off-bottom, clamps to left/right viewport edges. (4) JS wiring — b3ShowTip(): z-index 9999→99999 in cssText, custom positioning replaced with positionTooltip(); shTip(): removed window.scrollY bug (invalid for position:fixed), replaced with positionTooltip(); showInstructions(): z-index 9999→99999, custom positioning replaced with positionTooltip(); _showTip() in BodyMapTracker: added viewport edge bounds check + TAB_BAR_HEIGHT guard (was cursor+14 only). (5) [data-tooltip]::after CSS system added — new hover tooltip system for arbitrary elements. (6) All 13 tab buttons and separators in #main-tab-bar got data-tooltip attributes with plain-English descriptions. (7) New global float rule added to CSS ensuring [data-tooltip]:hover::after + .mcc-tooltip-text + .goeb-content + .tab-info-bubble use position:fixed !important z-index:99999. (8) .sh-popup changed from position:absolute → position:fixed in CSS. (9) OCB-E block updated: [class*='tooltip']/[class*='popup'] changed from position:absolute → position:fixed. (10) FIX 6 overflow: no containers changed — JS position:fixed tooltips are not clipped by ancestor overflow:hidden. 109/109 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** shTip() used window.scrollY in position calculation for a position:fixed element — invalid since fixed elements are viewport-relative. positionTooltip() replaces all custom positioning with a single consistent function that prevents tooltip from appearing behind the tab bar.
**Ideas discussed:** positionTooltip() as a reusable single-source-of-truth for all JS tooltip positioning going forward — any new tooltip function should call it rather than computing positions inline.
**Next priorities:**
1. Test OCB Runner v2 end-to-end in MCC — open HISAV S11, paste a small OCB block, Parse, then Dry Run
2. Complete STORM ↔ MCCM live loop testing
3. Wire aafl_wccs.py SESUM output → STORM → Mission Launcher
4. Test HISAV detective tab live in MCC — open Panel A, add a GHOST_FILE task, run it, click Panel B finding
5. OCB-K Build 3 — Costs tab enhancements, Scout improvements

<!-- END_OF_FILE -->
