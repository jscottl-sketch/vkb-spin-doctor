# VKB Spin Doctor — Project Handover v70 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** CLACKER Safety Layer built — clacker_safety.py + clacker_validator.py, git named stash, HTML parse guard, acceptance criteria in RRCLACH panel + /api/ocb/run, validator after MOT. 108/108 MOT ALL CLEAR.
**Last updated:** 2026-05-29
**Consolidates:** v69

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
| mission_control.html — Central Command (MCC) | ✅ v70 — RRCLACH panel added in WCCS tab |
| ALP_Database.md | ✅ 17 entries |
| WCCS Reliability Upgrade | ✅ Designed: Mini-Save Protocol, aafl_wccs.py, Chrome extension |
| aafl_wccs.py | ✅ LIFEGUARD PROTOCOL added v68 — pre-save snapshot + MOT all-clear auto-sync |
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
| OCB-K Build 2 Phase 1 (Kanban B2-01+B2-02) | ✅ Sub-task progress bar. 🔒 icon + muted colour for blocked cards. Dependency chain display. "Blocked by" set via b2SetDep(). AAFL Goal template (replaced Research). Bulk Archive. Bulk Move to any column. |
| OCB-K Build 2 Phase 2 (Activity Feed B2-03) | ✅ 12 filters: AAFL Run/Scout/WCCS/Error/Warning/Info/Kanban/Medical/Storage/Provider/User/System + Clear button. Date range export picker. |
| OCB-K Build 2 Phase 3 (AAFL Runs B2-04+B2-05) | ✅ Checkbox on each row — auto-opens compare when 2 selected. Change-highlighted side-by-side compare. Failure analysis: phase breakdown + suggested fix. Success patterns: time-of-day + goal-type breakdown. |
| OCB-K Build 2 Phase 4 (AAFL Control B2-06+B2-09) | ✅ All already built (Step Mode, Pause, Benchmark Runner, Second Opinion AI). |
| MCC freeze fix (v66) | ✅ Root cause: `?.checked = false` SyntaxError (line 9899) killed all JS in strict mode. Fixed + fullscreen guard + localStorage safety + permanent ⟳ Reset MCC button. |
| OCB-O: OCB Runner (v67) | ✅ ocb_runner.py (503 lines), OCB Runner panel in WCCS tab, 5 /api/ocb/* endpoints, real-time phase badges, live log, polling |
| OCBR Lifeguard Protocol v0.1 (v68) | ✅ status_snapshots/, STATUS_MASTER.md, ocb_wal.log, data/ocb_queue.json. ocb_runner.py +8 functions + argparse CLI. aafl_wccs.py wired. |
| wccs_detective.py — Chief Detective | ✅ v69 — scans STATUS/HISTORY/ACCA/session_logs/WAL/kanban/health.db/snapshots/git log. scan_all_sources, cross_reference_dates, find_gaps, build_case_file, propose_status_updates, request_ai_investigation. Writes data/detective_report_{date}.json. |
| mccm_agent.py — MCCM | ✅ v69 — power levels 1–4, assess_power_level, check_pending_requests, approve_ai_dispatch (dispatches chief_scout.py), raise_scott_interrupt, get_overview. data/mccm_permissions.json. |
| data/mccm_permissions.json | ✅ v69 — Created. power_level, pending, approved, rejected, scott_interrupts, last_cycle. |
| /api/mccm/status endpoint | ✅ v69 — runs mccm_agent.py --overview, returns JSON with status + power_level |
| /api/mccm/detective endpoint | ✅ v69 — returns latest detective_report_{date}.json |
| /api/mccm/alerts endpoint | ✅ v69 — returns pending scott_interrupts from mccm_permissions.json |
| Chief Detective + MCCM panel (WCCS tab) | ✅ v69 — Run Investigation + Run MCCM Cycle buttons, Level X/4 badge, results panel, proposed updates copy box, Scott Alerts with pulsing badge |
| clacker_safety.py — CLACKER Safety Layer | ✅ NEW v70 — pre_run (named stash), post_run_success (drop), post_run_failure (pop + rollback_log.json), check_html, check_py, check_server |
| clacker_validator.py — Acceptance Criteria Validator | ✅ NEW v70 — validate(criteria, files_changed, mot_score, project_root) → PASS/FAIL/PARTIAL, writes clachr_response.json |
| ocb_runner.py — CLACKER integration | ✅ v70 — named stash (pre-ocb-{run_id}), try/except wraps phase loop, HTML parse check in apply_result, acceptance_criteria param, validator called after MOT, clachr dict includes validator result |
| mcc_server.py — RRCLACH endpoint | ✅ v70 — /api/ocb/run reads acceptance_criteria from body; new POST /api/rrclach/save writes data/rrclach_request.json |
| RRCLACH panel (WCCS tab) | ✅ v70 — Instructions textarea + Acceptance Criteria textarea + Generate RRCLACH button → writes rrclach_request.json via /api/rrclach/save |
| data/rrclach_request.json | ✅ v70 — schema: {ocb_text, acceptance_criteria: [], saved_at} |
| data/rollback_log.json | ✅ v70 — appended on every ROLLED_BACK event by clacker_safety.post_run_failure |
| aafl_wccs.py — AAFL-powered handover writer | ⏸ Specced — CLAC session B (DSP required) |
| Handover split migration | ⏸ CLAC session A |
| OCB-B — Body Map visual + Auto-Fix Engine | ⏸ Next build block |
| Throttle slider in War Thunder | ⏸ Open |
| Star Citizen full support | ⏸ Next benchmark |
| merge_sessions.py + .bat | ⏸ Planned — DSP not yet confirmed |

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
python ocb_runner.py --status          # WAL + snapshot + master copy age
python ocb_runner.py --list            # pending OCBs in queue
python ocb_runner.py --run OCB-K-Build3   # start next OCB
python ocb_runner.py --sync-master     # force sync STATUS_MASTER.md
python ocb_runner.py --recover         # show recovery plan from last snapshot
```

### Chief Detective + MCCM CLI
```
python wccs_detective.py --investigate    # full scan, writes data/detective_report_{date}.json
python wccs_detective.py --propose        # print proposed STATUS.md additions only
python wccs_detective.py --gaps           # print gaps only
python mccm_agent.py --run               # full MCCM cycle (approve dispatches, escalate)
python mccm_agent.py --overview          # project state summary
python mccm_agent.py --power             # print current power level
python mccm_agent.py --alerts            # show pending Scott interrupts
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
| Home | Safety Shield, system dials, AI status bar, home cards |
| Kanban | Task board — B2 enhanced: progress bars, 🔒 deps, AAFL Goal template, bulk archive/move |
| AAFL Runs | Run history — B2 enhanced: row checkboxes for compare, failure analysis phases, success time-of-day |
| Costs | Budget caps, spend graphs, ROI, currency toggle |
| Scout | Parallel web research — Scout Swarm LEL, presets, live results |
| AAFL Control | Run Now, Step Mode, Pause, Benchmark Runner, Second Opinion AI, Workflow Builder |
| Code Editor | Monaco 0.44.0, file browser, run .py, CLAC generator, AAFL bridge |
| Health Suite | Provider Health, Self-Diagnosis, GPU/CPU/RAM, Medical, Work Checker |
| WCCS | Activity Feed (12 filters), Save Timeline, SESUM, OCB Runner, RRCLACH Panel, **Chief Detective + MCCM panel** |
| Instructions | 3-section accordion: INFORMATION / INSTRUCTIONS / CODES + AI Appendix |
| ACCA | ACCA code table — colour coded by category |

### Emergency Reset Button
A permanent red **⟳ Reset MCC** button sits at bottom-left (position:fixed, z-index:99999). Clicking it:
- Closes all overlays (kb-overlay, cmdpal-overlay, confirm-overlay)
- Hides any floating popups (instr-popup, ctx-menu, llow-jb-edit-popup etc.)
- Resets LLOW fullscreen if stuck
- Navigates to WCCS tab
- Does NOT do a full page refresh

### OCB Runner (v67)

The OCB Runner panel is in the WCCS tab at the bottom. Paste any OCB block (the ═══ PHASE N — NAME ═══ format), choose a provider and retry count, and click **Run OCB**. Free AI executes the build autonomously.

| Component | Detail |
|---|---|
| Input area | Textarea (10 rows monospace), provider dropdown (Auto/Codestral/Mistral/Gemini), retries spinner (1–5) |
| Phase list | One row per phase — PENDING/RUNNING/DONE/FAILED/SKIPPED badges, progress bar |
| Live log | Scrolling 8-row log, timestamps, Copy log + Archive run buttons |
| Poll | MCC polls GET /api/ocb/status/{run_id} every 3 seconds while running |
| ocb_runner.py | v70 — CLACKER wired: named stash, try/except, HTML check, validator |
| Endpoints | POST /api/ocb/parse, POST /api/ocb/run, GET /api/ocb/status/<id>, POST /api/ocb/cancel/<id>, POST /api/ocb/archive/<id> |
| CLACHR integration | run_all() writes data/clachr_response.json on completion — CLACHR panel auto-loads it |

### OCBR Lifeguard Protocol (v68)

Six safety mechanisms added to ocb_runner.py and wired into aafl_wccs.py:

| Function | What it does |
|---|---|
| pre_mission_snapshot(ocb_id) | Copies STATUS.md → status_snapshots/STATUS_pre_{id}_{ts}.md before any build |
| wal_log(ocb_id, phase, intent) | Appends timestamped line to ocb_wal.log — append-only, never delete |
| post_phase_beacon(ocb_id, phase, summary) | Writes 5-line beacon to session_logs/ocb_beacon_{id}_{phase}_{date}.md |
| distress_save(ocb_id, phase, error) | STATUS_FAIL snapshot + WAL FAILURE + stuck_inbox.json flag |
| sync_master_copy() | Overwrites STATUS_MASTER.md with current STATUS.md + updated header |
| recover(ocb_id?) | Lists snapshots, shows WAL entries since chosen snapshot, prints restore plan |
| generate_clac_block(ocb_id, desc) | Prints formatted CLAC stub with DSP reminder |
| run_ocb(ocb_id, desc) | Full OCB kickoff: snapshot → WAL START → CLAC block |

aafl_wccs.py additions:
- LIFEGUARD PROTOCOL: calls `ocb_runner.py --complete WCCS-autosave` at start of every save (pre-save snapshot)
- MOT detection: if chat_latest.txt contains "108/108" or "ALL CLEAR", auto-calls `--sync-master`

### CLACKER Safety Layer (v70)

Two new Python modules add a defensive safety layer around OCB builds:

**clacker_safety.py** — Git + file validation helpers

| Function | What it does |
|---|---|
| pre_run(run_id, project_root) | git stash push -m pre-ocb-{run_id} — named stash for traceability. Returns stash output. |
| post_run_success(run_id, project_root) | git stash drop — changes are good, discard safety copy |
| post_run_failure(run_id, project_root, stash_ref) | git stash pop (rollback) + appends ROLLED_BACK entry to data/rollback_log.json |
| check_html(filepath) | Parses file with html.parser. Returns (True,"") or (False, error string) on HTMLParseError |
| check_py(filepath) | py_compile check. Returns (True,"") or (False, error string) on syntax error |
| check_server() | GET http://127.0.0.1:8080/api/health. Returns True if 200 OK |

**clacker_validator.py** — Acceptance criteria checker

| Criterion rule | Check performed |
|---|---|
| "MOT" or "108/108" in criterion | Checks mot_score contains "108/108" + "all clear" |
| filename in criterion | Checks that file was in files_changed list |
| "tabs load" in criterion | Calls clacker_safety.check_server() |
| "renders" in criterion | Checks named file was in files_changed |
| No match | Marks "[unchecked, assumed pass]" |

Returns: `{"status": "PASS"/"FAIL"/"PARTIAL", "passed": [], "failed": [], "notes": ""}` and writes data/clachr_response.json atomically.

**ocb_runner.py changes (v70):**
- Imports clacker_safety + clacker_validator at top
- `run_all()` now takes `acceptance_criteria: list = []` parameter — stored in ocb_status.json
- Phase loop wrapped in try/except: on unhandled exception → status=ROLLED_BACK → post_run_failure → re-raise
- apply_result(): HTML files checked with clacker_safety.check_html() before rename (returns False on parse error)
- After MOT: clacker_validator.validate() called, result merged into clachr_response.json
- Stash now named (pre-ocb-{run_id}) via clacker_safety.pre_run()

**mcc_server.py changes (v70):**
- POST /api/ocb/run: reads `acceptance_criteria` from request body (default []), passes to run_all()
- NEW POST /api/rrclach/save: writes data/rrclach_request.json with {ocb_text, acceptance_criteria, saved_at}

**RRCLACH Panel (WCCS tab, v70):**
- Section: "RRCLACH — Generate Run Request"
- Instructions textarea (OCB block)
- Acceptance Criteria textarea (one per line — e.g. "green pill renders", "all tabs load", "MOT 108/108")
- "⚡ Generate RRCLACH" button → POST /api/rrclach/save → writes rrclach_request.json

### Chief Detective + MCCM (v69)

Two new Python tools for autonomous project state awareness:

**wccs_detective.py** — WCCS Chief Detective

| Function | What it does |
|---|---|
| scan_all_sources() | Reads STATUS/HISTORY/ACCA/session_logs/WAL/kanban/health.db/snapshots/git log. Returns {source: {last_modified, key_facts, timestamps, ocb_names}} |
| cross_reference_dates() | Compares timestamps across sources. Finds session logs not in STATUS, WAL entries without beacons, OCBs in HISTORY not in STATUS BUILT table |
| find_gaps() | Lists things mentioned in one source but absent from STATUS.md. Each gap has confidence HIGH/MEDIUM/LOW + suggested_fix |
| build_case_file() | CONFIRMED (2+ sources), UNCERTAIN (1 source), UNKNOWN, PROPOSED_UPDATES |
| propose_status_updates() | Prints formatted STATUS.md table rows — never auto-writes |
| request_ai_investigation(gap_id) | Appends LOW-confidence gap to data/mccm_permissions.json pending list |

**mccm_agent.py** — Mission Control Center Master (MCCM)

| Power Level | Unlock condition |
|---|---|
| 1 | Default — read, deduce, propose |
| 2 | memory_bank.db + health.db + 10+ session logs present |
| 3 | 10+ AAFL autonomous run records |
| 4 | Future — full autonomy |

| Function | What it does |
|---|---|
| assess_power_level() | Checks file presence + run count, saves to mccm_permissions.json |
| check_pending_requests() | Splits pending into approvable (level OK) vs escalation_needed |
| approve_ai_dispatch(request_id) | Moves to approved, dispatches chief_scout.py, saves result to data/mccm_investigations/ |
| raise_scott_interrupt(reason) | Logs to scott_interrupts, POSTs to /api/stuck/add |
| get_overview() | Prints STATUS.md summary + detective report + pending counts |

MCC endpoints (3 new):
- `GET /api/mccm/status` — runs mccm_agent.py --overview, returns output + power_level
- `GET /api/mccm/detective` — returns latest detective_report_{date}.json
- `GET /api/mccm/alerts` — returns pending scott_interrupts

MCC panel (WCCS tab, after OCB Runner):
- Run Investigation button → loads detective report
- Run MCCM Cycle button → triggers overview
- Level X/4 badge (grey=1, blue=2, gold=3, red=4)
- Results panel (CONFIRMED/UNCERTAIN/UNKNOWN counts + proposed rows)
- Scott Alerts section (pulsing red badge if pending)

### OCB-K Build 2 — Kanban Enhancements

| Feature | Detail |
|---|---|
| Sub-task progress bar | Colour-filled bar below subtask count shows % complete |
| 🔒 blocked cards | Cards with unmet `blocked_by` show 🔒 icon, muted/faded border and opacity |
| Dependency chain | Blocked cards show "Needs: [card title]" in red panel on card face |
| Set dependency | "🔗 dep" button on each card → numbered prompt to pick blocking card |
| AAFL Goal template | Replaces Research template — 4 sub-tasks: Define goal / Run AAFL / Review+store / Update STATUS.md |
| Bulk Archive | "📦 Archive" in bulk bar moves selected cards to archive (viewable via Archive button) |
| Bulk Move to column | Column selector dropdown + Move button — moves all selected cards to any column |

### OCB-K Build 2 — Activity Feed Enhancements

| Feature | Detail |
|---|---|
| 12 spec filters | AAFL Run / Scout / WCCS / Error / Warning / Info / Kanban / Medical / Storage / Provider / User / System |
| Clear button | Resets all filters back to All |
| Date range export | From/To date pickers beside Export button — filters exported entries by date |

### OCB-K Build 2 — AAFL Runs Enhancements

| Feature | Detail |
|---|---|
| Row checkboxes | Tick any 2 rows — compare panel auto-opens with change-highlighted diff |
| Failure analysis phases | Shows which phase failed most + error breakdown + suggested fix (switch provider heuristic) |
| Success patterns | Best providers (avg score) + best goal types + best time of day (4 slots) |

---

## ENGINE ARCHITECTURE — MICROKERNEL

Drop a .py file into `/problems/` — engine picks it up automatically. No registration needed.

| Module ID | Name | Problems covered | Status |
|---|---|---|---|
| spin_fix | Spin Bug (Mouse Axis) | Removes mouse double-bind from flight axes | ✅ Working (War Thunder) |
| usb_power_saver | USB Power Saver | Disables Windows USB port power-off mid-session | ✅ Built |
| steam_input_conflict | Steam Input Conflict | Turns Steam Input OFF for WT, ED, MSFS, DCS, IL-2, AC7 | ✅ Built |
| conductor | Process Conductor | 22 problems — companion software, input mappers, overlays, launch order | ✅ Built |
| win_hardener | Windows Hardener | 9 problems W-001→W-009 — USB power, polling rate, registry, HID errors | ✅ Built |
| ed_bind_reset | ED Bind Reset prevention | Prevents Elite Dangerous from resetting custom bindings | ✅ Built |

---

## PROJECT FILES

```
VKB-SpinDoctor/
├── spin_doctor.py
├── sfl_agent.py                       # v3 — HANDOVER_FILENAME → v70
├── aafl_core.py
├── loop_manager.py
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
├── ocb_runner.py                      # v70 — CLACKER wired: named stash, try/except, HTML check, validator
├── clacker_safety.py                  # NEW v70 — pre_run, post_run_success/failure, check_html/py/server
├── clacker_validator.py               # NEW v70 — validate(criteria, files_changed, mot_score) → PASS/FAIL/PARTIAL
├── wccs_detective.py                  # NEW v69 — Chief Detective: scans all sources, gap analysis
├── mccm_agent.py                      # NEW v69 — MCCM overseer, power levels 1-4, AI dispatch
├── ocb_wal.log                        # v68 — Write-Ahead Log (append only)
├── STATUS_MASTER.md                   # v68 — golden STATUS.md backup post-MOT
├── mcc_server.py                      # v70 — /api/ocb/run reads acceptance_criteria; POST /api/rrclach/save
├── mcc_full_mot.py                    # 108 tests, GROUP A-H
├── aafl_wccs.py                       # v68 — LIFEGUARD PROTOCOL wired
├── mission_control.html               # v70 — RRCLACH panel in WCCS tab
├── CLAUDE.md
├── ACCA.md
├── ALP_Database.md
├── STATUS.md
├── HISTORY.md
├── INDEX.md
├── goal.txt / goal_queue.txt / meta_queue.txt
├── VKB_SpinDoctor_Handover_v70.md     # This file
├── data/
│   ├── knowledge_engine.db
│   ├── health.db
│   ├── ocb_status.json                # OCB run state (now includes acceptance_criteria)
│   ├── ocb_queue.json                 # v68 — pending OCB queue
│   ├── rrclach_request.json           # NEW v70 — {ocb_text, acceptance_criteria, saved_at}
│   ├── rollback_log.json              # NEW v70 — appended on every ROLLED_BACK event
│   ├── clachr_response.json           # v70 — now includes validator result
│   ├── mccm_permissions.json          # NEW v69 — MCCM power level + request queues
│   ├── detective_report_{date}.json   # NEW v69 — daily detective case file
│   ├── mccm_investigations/           # NEW v69 — chief_scout results per gap
│   ├── element_registry.json          # 125 UI elements
│   ├── solution_database.json         # 12 auto-fix solutions
│   ├── instructions_db.json           # 132 help entries
│   ├── llow_elements.json             # LLOW palette + 11 AI providers
│   ├── llow_workflows/                # 14 workflow presets
│   ├── mcc_settings.json
│   ├── project_awareness.json
│   └── ...
├── status_snapshots/                  # v68 — pre-mission STATUS.md snapshots
│   └── STATUS_pre_{ocb_id}_{ts}.md
├── problems/
│   ├── conductor.py
│   ├── ed_bind_reset.py
│   └── win_hardener.py
├── data/llow_workflows/
│   ├── write_new_feature.json
│   ├── fix_bug.json
│   ├── refactor_file.json
│   └── ... (11 more presets)
├── session_logs/
├── loop_output/
├── health_results/
└── archive_dead/                      # Old handovers — NEVER deleted
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
| Packages | mss, lmstudio, Pillow, anthropic, litellm, python-dotenv, langgraph, ddgs |
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
| MCC completely frozen / all buttons dead | Click ⟳ Reset MCC button (bottom-left, red). If that doesn't work, hard-refresh (Ctrl+Shift+R) |
| MCC stuck on WCCS tab | Was caused by `?.checked = false` SyntaxError (fixed v66). If it recurs, open browser console (F12) and look for SyntaxError |
| Kanban card not moving to Done | Check if card has 🔒 icon — unmet dependencies block →Done button |
| Activity filter not showing entries | Check category matches — new filters use spec names (aafl-run not aafl, error not errors) |
| AAFL Runs compare not auto-opening | Tick exactly 2 checkboxes on run rows — compare panel opens automatically |
| OCB Runner shows no phases after Parse | OCB block must use ═══ PHASE N — NAME ═══ format (Unicode box chars) |
| OCB Runner run hangs | Click ■ Cancel button — sets cancelled flag, runner checks between tasks |
| OCB Runner rolled back unexpectedly | Check data/rollback_log.json for the reason. Named stash shows as pre-ocb-{run_id} in git stash list |
| Acceptance criteria all FAIL | Check mot_score format — validator looks for "108/108" + "all clear" |
| RRCLACH save fails | Make sure Instructions textarea has OCB block content before clicking Generate |
| `localhost:1234` refused | Use `127.0.0.1:1234` |
| LM Studio server drops | Don't reload models while server is running |
| Cerebras model fails | Use cerebras/gpt-oss-120b in aafl_core.py |
| Multiple CLAC terminals open | ALP-dangerous — run one at a time |
| MCC Self-Health tab shows no data | Run self_health.py manually once to create health.db |
| Code Editor Run fails | Script runs with 30s timeout — save first (Ctrl+S) |
| ocb_runner.py UnicodeEncodeError | Box-drawing chars cause cp1252 crash — fixed v68, use ASCII borders in generate_clac_block |
| Detective report not found | Run: python wccs_detective.py --investigate first |
| MCCM power stays at 1 | Needs memory_bank.db + health.db + 10 session logs for level 2 |

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

1. Test OCB Runner end-to-end with RRCLACH + acceptance criteria (paste real OCB, verify validator output)
2. OCB-K Build 3 — Costs tab enhancements, Scout improvements, parking lot features
3. Star Citizen v0.2 benchmark via AAFL autonomous run (proof of concept #2)
4. Add GROQ + Cloudflare keys to .env (manual — security rule)
5. Polish AASKC for ship — README, demo video, r/LocalLLaMA post
6. Post on r/LocalLLaMA when Star Citizen benchmark passes
7. LiteLLM full integration — replace direct provider calls with LiteLLM router
8. Electron wrapper for packaging

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

---

## RESUME COMMAND

> "Continuing VKB Spin Doctor. Read VKB_SpinDoctor_Handover_v70.md. CLACKER Safety Layer built this session. Five phases: (1) clacker_safety.py — pre_run named stash, post_run_success/failure, check_html/py/server; (2) clacker_validator.py — validate(criteria, files_changed, mot_score) PASS/FAIL/PARTIAL, writes clachr_response.json; (3) ocb_runner.py updated — imports both modules, phase loop wrapped in try/except with rollback on unhandled exception, apply_result checks HTML with clacker_safety.check_html before rename, acceptance_criteria param added to run_all, validator called after MOT; (4) mcc_server.py — /api/ocb/run reads acceptance_criteria from body, new POST /api/rrclach/save writes data/rrclach_request.json; (5) mission_control.html — RRCLACH panel (Instructions textarea + Acceptance Criteria textarea + Generate RRCLACH button). 108/108 MOT ALL CLEAR. Next: test OCB Runner end-to-end with acceptance criteria. Then OCB-K Build 3."

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
**Key decisions:** OCB-O built — 15 fixes across 5 phases. Safety Watchdog indicator, Global Search (Ctrl+K), Help tab button removed, LLOW Alt+drag connector, fullscreen fix, CPU/RAM error→0 fix, AI Leaderboard fix, AI bar 15s + colour latency, medical history fix, ACCA colour coding, AI Allocation panel, vertical section sliders, tab bar scroll arrows. 2 new server endpoints. 108/108 MOT ALL CLEAR.
**Bugs fixed:** CPU/RAM showing red on psutil error. AI Leaderboard blank. LLOW fullscreen not expanding. Medical history showing no runs.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 5)
**Key decisions:** OCB-O Code Pipeline built — 5 phases. Monaco Code Editor tab, AAFL→Editor bridge, CLAC Generator, 3 LLOW coding workflows (write_new_feature/fix_bug/refactor_file), 4 /api/code/* endpoints. 108/108 MOT ALL CLEAR.
**Next priorities:** 1. OCB-B 2. Star Citizen 3. Add API keys

---

### 2026-05-29 (Claude Code session 6)
**Key decisions:** OCB-K Build 2 complete — 4 phases. (1) Kanban: progress bars on subtask checklist, 🔒 icon + muted colour + dep chain on blocked cards, b2SetDep() numbered-list dep picker, AAFL Goal template (replaced Research), Bulk Archive button, Bulk Move to any column. (2) Activity Feed: 12 filter bar updated to spec names (AAFL Run/Scout/WCCS/Error/Warning/Info/Kanban/Medical/Storage/Provider/User/System), Clear button (b2ActClear()), date range pickers for export. (3) AAFL Runs: checkbox on each row, auto-compare when 2 ticked (b2CompareByCheckboxes() with ⚡ change-highlight on differing fields), failure analysis phase breakdown + suggested fix heuristic, success patterns adds goal-type + time-of-day analysis. (4) AAFL Control: all B2-06/08/09 features already built (Step Mode, Pause, Benchmark Runner, Second Opinion AI). 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** Activity filter categories were wrong vs spec (old: costs/manual/auto/today/week/month — new: spec's 12). b2BulkMove only moved to Done — now has column selector. Research template not in spec — replaced with AAFL Goal (4 relevant sub-tasks).
**Ideas discussed:** Dependency chain visible on card face (not just expand) — more immediate for blocked cards. Auto-open compare panel when 2 checkboxes ticked is faster than toggle+dropdown flow.
**Next priorities:**
1. OCB-K Build 3 — Costs tab enhancements, Scout improvements
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Post on r/LocalLLaMA when Star Citizen benchmark passes
5. Electron wrapper for packaging

---

### 2026-05-29 (Claude Code session 17)
**Key decisions:** MCC complete freeze diagnosed and fixed. Root cause: `?.checked = false` (optional chaining on LHS of assignment) is a JavaScript SyntaxError. It appeared on line 9899 of mission_control.html in OCB-K Build 2's b2RunCmpSelect() function. With `'use strict'` at the top of the 11,600-line script block, this single syntax error prevented the ENTIRE block from parsing — initTabs() never ran, every button was dead, page stuck on WCCS. Fix: replaced with `const _oldCb = ...; if (_oldCb) _oldCb.checked = false;`. Three additional safety hardening changes: (1) DOMContentLoaded guard resets llow-fs-active class if stuck on page load. (2) Module-level `_llowLoopPresets` localStorage read wrapped in try/catch. (3) Permanent ⟳ Reset MCC button added (position:fixed, bottom:10px, left:10px, z-index:99999) — clears overlays, resets fullscreen, navigates to WCCS. Node.js `--check` used to verify all 3 script blocks clean. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** `?.checked = false` SyntaxError in b2RunCmpSelect() line 9899 — killed all JS, made entire MCC unresponsive.
**Ideas discussed:** Using Node.js `--check` as a syntax validator for the HTML script blocks — fast way to catch these issues before commit.
**Next priorities:**
1. OCB-K Build 3 — Costs tab enhancements, Scout improvements, parking lot features
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Post on r/LocalLLaMA when Star Citizen benchmark passes
5. Electron wrapper for packaging

---

### 2026-05-29 (Claude Code session 18)
**Key decisions:** OCB-O OCB Runner built — the biggest MCC build yet. Scott can now paste any OCB block into the WCCS tab and free AI executes it autonomously without Claude Code. ocb_runner.py (503 lines): parse_ocb_block (regex on ═══ PHASE N — pattern), identify_affected_file (15 known filenames), extract_relevant_section (keyword scoring ±150 lines), run_task (calls aafl_core 'code' routing), apply_result (atomic write + py_compile for .py), run_all orchestrator (writes ocb_status.json throughout, MOT at end, clachr_response.json). Five new endpoints in mcc_server.py. WCCS tab now has full OCB Runner panel with input area, phase list with colour badges, live log, progress bar, Copy/Archive buttons. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** Windows console encoding crash (→ character in self-test print) — replaced with ->.
**Ideas discussed:** None
**Next priorities:**
1. Test OCB Runner end-to-end — paste a real OCB block, verify Parse + Run
2. OCB-K Build 3 — Costs tab enhancements, Scout improvements
3. Star Citizen v0.2 benchmark via AAFL autonomous run
4. Add GROQ + Cloudflare keys to .env (manual — security rule)
5. Post on r/LocalLLaMA when Star Citizen benchmark passes

---

### 2026-05-29 (Claude Code session 20)
**Key decisions:** OCBR Lifeguard Protocol v0.1 built. Six safety mechanisms added to the project: (1) status_snapshots/ directory for pre-mission STATUS.md snapshots; (2) STATUS_MASTER.md golden backup, only overwritten after MOT all-clear; (3) ocb_wal.log Write-Ahead Log, append-only, timestamped entries; (4) data/ocb_queue.json pending/completed OCB tracker; (5) ocb_runner.py extended with 8 new functions (wal_log, pre_mission_snapshot, post_phase_beacon, distress_save, sync_master_copy, recover, generate_clac_block, run_ocb) and full argparse CLI (--run/--complete/--sync-master/--recover/--list/--status); (6) aafl_wccs.py wired — LIFEGUARD PROTOCOL comment added, pre-save snapshot call before every write, auto-sync STATUS_MASTER when chat text contains 108/108 or ALL CLEAR. UnicodeEncodeError on Windows cp1252 fixed by replacing box-drawing chars in generate_clac_block with ASCII borders. All 3 CLI tests pass: --status (shows WAL + snapshot + master age), --list (shows 2 pending OCBs), --run OCB-K-Build3 (snapshot saved, CLAC block printed).
**New ACCA codes:** OCBR = OCB Runner (Lifeguard Protocol build tool)
**Bugs fixed:** generate_clac_block UnicodeEncodeError on Windows cp1252 — box chars replaced with ASCII = borders.
**Ideas discussed:** WAL log as audit trail for recovery — shows exactly what happened after last snapshot, enabling precise re-apply of completed work.
**Next priorities:**
1. OCB-K Build 3 — Costs tab enhancements, Scout improvements, LLOW enhancements
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Polish AASKC for ship — README, demo video, r/LocalLLaMA post
5. Electron wrapper for packaging

---

### 2026-05-29 (Claude Code session 21)
**Key decisions:** Chief Detective + MCCM built. wccs_detective.py (scan_all_sources reads STATUS/HISTORY/ACCA/session_logs/WAL/kanban/health.db/snapshots/git log; cross_reference_dates finds session logs not in STATUS + WAL entries without STATUS date + HISTORY OCBs not in BUILT; find_gaps returns HIGH/MEDIUM/LOW confidence items with suggested_fix; build_case_file: CONFIRMED 2+sources/UNCERTAIN 1-source/UNKNOWN/PROPOSED_UPDATES; request_ai_investigation appends LOW gaps to mccm_permissions.json pending). mccm_agent.py (power levels 1-4: 2=memory_bank+health+10sessions, 3=10+AAFL runs; assess_power_level saves to mccm_permissions.json; check_pending_requests splits by level; approve_ai_dispatch dispatches chief_scout.py subprocess, saves result to data/mccm_investigations/{request_id}.txt; raise_scott_interrupt POSTs to /api/stuck/add). data/mccm_permissions.json created. Three new mcc_server.py endpoints: GET /api/mccm/status (runs --overview), GET /api/mccm/detective (returns latest detective report JSON), GET /api/mccm/alerts (returns pending scott_interrupts). WCCS tab: Chief Detective + MCCM section added after OCB Runner — Run Investigation button, Run MCCM Cycle button, Level X/4 badge (grey/blue/gold/red), results panel, proposed STATUS rows copy box, Scott Alerts pulsing badge + list. chief_scout.py: get_project_context() added (STATUS first 30 + INDEX first 20 lines), prepended to query in __main__, --no-context flag skips it. All CLI tests pass: detective 15 confirmed/2 uncertain, mccm --run power 1/4, mccm --power correct.
**New ACCA codes:** MCCM = Mission Control Center Master
**Bugs fixed:** None
**Ideas discussed:** Power level system lets MCCM earn autonomy as the project grows — starts conservative, unlocks dispatches once evidence of real activity exists.
**Next priorities:**
1. OCB-K Build 3 — Costs tab enhancements, Scout improvements, parking lot features
2. Star Citizen v0.2 benchmark via AAFL autonomous run
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Polish AASKC for ship — README, demo video, r/LocalLLaMA post
5. Electron wrapper for packaging

---

### 2026-05-29 (Claude Code session 22)
**Key decisions:** CLACKER Safety Layer built — 5 phases. (1) clacker_safety.py: pre_run uses named git stash (pre-ocb-{run_id}), post_run_success drops stash, post_run_failure pops (rollback) + appends to data/rollback_log.json, check_html parses with html.parser (catches HTMLParseError before rename), check_py wraps py_compile, check_server GETs /api/health. (2) clacker_validator.py: validate(criteria, files_changed, mot_score, project_root) checks each criterion by rule (MOT score, filename in changed, tabs load → check_server, renders → file in changed, else assumed pass), returns PASS/FAIL/PARTIAL dict, writes clachr_response.json atomically. (3) ocb_runner.py: imports both modules at top, phase loop wrapped in try/except (ROLLED_BACK status + post_run_failure + re-raise on unhandled exception), apply_result adds HTML check before rename, run_all gains acceptance_criteria param stored in ocb_status.json, validator called after MOT and result merged into clachr_response.json. (4) mcc_server.py: /api/ocb/run reads acceptance_criteria from body, new POST /api/rrclach/save writes data/rrclach_request.json. (5) mission_control.html: RRCLACH panel added (Instructions textarea, Acceptance Criteria textarea, Generate RRCLACH button wired to /api/rrclach/save). 108/108 MOT ALL CLEAR.
**New ACCA codes:** RRCLACH = Run Request CLACH — panel that generates rrclach_request.json with OCB block + acceptance criteria
**Bugs fixed:** None
**Ideas discussed:** Acceptance criteria as a formal contract between the build spec and the automated validator — instead of human eyeballing MOT results, the criteria list is machine-checked and the verdict is written to clachr_response.json automatically.
**Next priorities:**
1. Test OCB Runner end-to-end with RRCLACH + acceptance criteria (paste real OCB, verify validator output)
2. OCB-K Build 3 — Costs tab enhancements, Scout improvements, parking lot features
3. Star Citizen v0.2 benchmark via AAFL autonomous run
4. Add GROQ + Cloudflare keys to .env (manual — security rule)
5. Polish AASKC for ship — README, demo video, r/LocalLLaMA post

<!-- END_OF_FILE -->
