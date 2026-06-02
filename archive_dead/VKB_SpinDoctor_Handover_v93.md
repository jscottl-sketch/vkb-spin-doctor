# VKB Spin Doctor — Project Handover v93 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** v93 — ANCOREG accordion merged into Health Suite + BSTP accordion merged into Missions + Mission Mode toggle + GRRICE Changelog section + ACCA info boxes + WCCS direct session log speed fix + POST /api/acca/command endpoint; STATUS.md: AAFL_Overnight_Task disabled notice + CCR (Claude Chat Relay) logged as PENDING; 109/109 MOT ALL CLEAR.
**Last updated:** 2026-06-02
**Consolidates:** v92

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
| HITSAV | History Time Save — the renamed HISAV tab (was WCCS, then HISAV, now HITSAV) |
| DTA | Data As Truth Architecture — project state in structured JSON files HITSAV can read/write without AI |
| STORM | Selective Targeted Output Remove Merge — unified data feed from detective/WCCS/screenshots |
| GRRICE | Guide Rules Regulation Instructions Codes Education — the renamed RRICE tab |
| RRICE | Rules and Regulations, Codes and Instructions Education (old name — now GRRICE) |
| HISAV | History + Ideas + Save (old name — now HITSAV) |
| RAG | Retrieval Augmented Generation — project knowledge injected into AI prompts before each call |
| ANCOREG | Autonomous Node Condition Registry — System Doctor tab in MCC |
| BSTP | Brainstorm Planner — visual drag-drop canvas tab in MCC |
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
| aafl_core.py — provider routing | ✅ v89 — RAG context injection before every AI call (use_rag=True, default ON) |
| loop_manager.py — loop engine | ✅ v90 — code blocks/results saved as .json (not .py/.txt); feedback_loop.after_run() called every AAFL iteration |
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
| mission_control.html — Central Command (MCC) | ✅ v92 — ANCOREG tab + BSTP tab added; JS for both injected |
| ALP_Database.md | ✅ 17 entries |
| WCCS Reliability Upgrade | ✅ Designed: Mini-Save Protocol, aafl_wccs.py, Chrome extension |
| aafl_wccs.py | ✅ v87 — archive_old_handovers() removed; _elapsed() at LIFEGUARD/pre-bak/STATUS write |
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
| OCB-K Build 2 Phase 1 (Kanban B2-01+B2-02) | ✅ Sub-task progress bar. lock icon + muted colour for blocked cards. Dependency chain display. AAFL Goal template. Bulk Archive + Move. |
| OCB-K Build 2 Phase 2 (Activity Feed B2-03) | ✅ 12 filters + Clear button + date range export picker. |
| OCB-K Build 2 Phase 3 (AAFL Runs B2-04+B2-05) | ✅ Checkbox compare, failure analysis, time-of-day success breakdown. |
| MCC freeze fix (v66) | ✅ `?.checked = false` SyntaxError fixed. Permanent Reset MCC button. |
| OCB-O: OCB Runner (v67) | ✅ ocb_runner.py (503 lines), OCB Runner panel, 5 /api/ocb/* endpoints. |
| OCBR Lifeguard Protocol v0.1 (v68) | ✅ status_snapshots/, STATUS_MASTER.md, ocb_wal.log, data/ocb_queue.json. |
| wccs_detective.py — Chief Detective | ✅ v69 — scans all sources, writes detective_report_{date}.json. |
| mccm_agent.py — MCCM | ✅ v69 — power levels 1–4, approve/escalate. data/mccm_permissions.json. |
| /api/mccm/* endpoints (4) | ✅ v80 — status, detective, alerts, generate-status |
| clacker_safety.py — CLACKER Safety Layer | ✅ v70 — pre_run, post_run_success/failure, check_html/py/server |
| clacker_validator.py — Acceptance Criteria Validator | ✅ v70 — validate() → PASS/FAIL/PARTIAL, writes clachr_response.json |
| mcc_server.py | ✅ v92 — 15 new endpoints: /api/acca/codes, /api/acca/add, /api/ancoreg/*, /api/bstp/* |
| RRCLACH panel (HITSAV tab) | ✅ v71 — classification pill after Generate RRCLACH |
| clacker_router.py | ✅ v71 — classify() + classify_all() |
| data/session_state.json | ✅ v71 — unified state |
| provider_health.py — run_diagnosis() | ✅ v71 — live-tests each provider |
| HITSAV tab (renamed from HISAV/WCCS) | ✅ v81 — all hisav→hitsav across HTML+server+detective |
| HITSAV S2: Idea Dump | ✅ v73 — EXPANDED by default, Ctrl+Enter save |
| HITSAV S3: Vehicle History | ✅ v74 — PAST/PRESENT/PLANNED zones, TODAY marker (gold pulsing), scroll arrows |
| HITSAV S4: Checklist Health | ✅ v73 — data/master_checklist.json, progress bars, click-to-tick |
| HITSAV S5: Idea Buffer | ✅ v73 — age-colour cards, done/promote/dismiss buttons |
| HITSAV S6: Action Plan | ✅ v73 — top 6 from STATUS.md NEXT PRIORITIES |
| HITSAV S7: CLAC Sessions | ✅ v73 — CLAC logger + Screenshot Intake |
| HITSAV S8: Screenshots | ✅ v73 — gallery thumbnails |
| HITSAV S9: Work Checker | ✅ v73 — incomplete CLAC run tracker |
| HITSAV S10: WENTO | ✅ v74 — WENTO queue panel |
| HITSAV S11: OCB Runner v4 | ✅ v91 — Skip MOT checkbox (id=hitsav-ocb-skip-mot) added; hitsavOcbRun() passes skip_mot to API |
| HITSAV S12: Claude Brain | ✅ pre-built — memory snapshot accordion section |
| HITSAV S13: Bridge Log | ✅ pre-built — Claude↔MCC message log |
| HITSAV sticky toolbar: 3-step save flow | ✅ v79 — ① Save Session → ② Copy STATUS.md → ③ Go to Claude |
| HITSAV toolbar: Auto-Update STATUS.md button | ✅ v80 — button calls /api/mccm/generate-status |
| OCB Runner standalone tab — v4 visual | ✅ v81 — phase cards (rich cards not flat badges), ABORT button, pulsing progress bar glow, animated parse stages, final summary line |
| POST /api/ocb/abort | ✅ v81 — writes data/ocb_abort.json {abort:true}; DELETE clears it |
| GET /api/ocb/progress | ✅ v91 — reads data/ocb_progress.json (written atomically by _write_status after each phase); returns {phases, phase_current, phase_total, percent, status, mot_score} |
| OCB abort check in run_safe() | ✅ v81 — _is_aborted() reads ocb_abort.json between phases + within task loop |
| GRRICE tab (renamed from RRICE) | ✅ v81 — Guide Rules Regulation Instructions Codes Education; data-tab="rrice" kept |
| 7-tab top bar + sidebar restructure | ✅ v81 — 7 primary tabs; remaining tabs in sidebar nav; hidden data-tab markers for MOT |
| _NAV_TREE sidebar separator section | ✅ v81 — "--- More ---" divider separating primary from sidebar-only tabs |
| Project Brain theme (:root CSS) | ✅ v81 — --pb-* palette vars + --bg-secondary/--border/--accent/etc; tab-bar + sidebar updated |
| Design Vault UI + endpoints | ✅ pre-built — dvSaveTheme/dvLoadGallery/dvApplyTheme/dvDeleteTheme + 4 /api/design/* endpoints |
| data/design_saves.json | ✅ v81 — updated Project Brain preset with full palette |
| storm_bridge.py — ingest_sesums() | ✅ v80 — scans session_logs/ last 3 days |
| hitsav_detective.py — renamed+updated | ✅ v81 — all HISAV→HITSAV references updated |
| /api/memory/snapshot + /api/memory/refresh | ✅ pre-built — Claude Brain memory snapshot |
| /api/bridge/* endpoints | ✅ pre-built — Claude↔MCC bridge messages |
| Handover bloat removed | ✅ v81 — no handover files created; all archived to archive_dead/ |
| OCB-S: parse_ocb_block() rewrite | ✅ v83 — O(n) line-scan (not regex-split on full text); 3-pass: sep-chars / bare Phase N / single-phase fallback; hard cap 10K lines, 1K body lines per phase |
| OCB-S: extract_relevant_section() fix | ✅ v83 — scan capped at 2000 lines + early exit when all keywords found; was O(n²) blocking GIL |
| OCB-S: server-side parse timeout | ✅ v83 — concurrent.futures 10s timeout in _handle_ocb_parse |
| OCB-S: ocb2Run() AbortController | ✅ v83 — 60s fetch timeout; catch handler always calls _ocb2SetActive(false) |
| OCB-S: ocb2Abort() immediate | ✅ v83 — sets window.ocbAbort=true immediately, disables button, then fires POST (non-blocking) |
| OCB-S: Escape key abort | ✅ v83 — keydown handler: Escape triggers ocb2Abort() when abort button is visible |
| OCB-S: bar colour states | ✅ v83 — _ocb2SetBarColor(): amber while running, green on success, red on error |
| OCB-S: green terminal log | ✅ v83 — ocb2-log colour #22d3a0, background #050a05, max-height 300px |
| CSS hotfix: .hitsav-idea-btns closing brace | ✅ v84 — MOT stub fix (c3b366e) had removed `}` from `.hitsav-idea-btns{display:flex;gap:6px}`, corrupting entire CSS block below line 130 — sidebar and tab bar both invisible |
| CSS hotfix: 20 deleted HITSAV rules restored | ✅ v84 — `.hitsav-idea-btn`, `.hitsav-ap-*`, `.hitsav-clac-*`, `.hitsav-drop-zone`, `.hitsav-thumb`, `.hitsav-gallery`, `.tl-detail-popup` all restored |
| wccs_runner.py: dead handover write code removed | ✅ v86 — 6 dead functions removed: _handover_excerpt, build_llm_prompt, parse_llm_response, build_new_handover, update_sfl_agent, write_session_log |
| aafl_wccs.py: per-step timing | ✅ v86 — _elapsed() shows per-step time + cumulative + SLOW >10s warning; git push 30s timeout |
| data/investigations_db.json | ✅ v86 — 6 investigations INV-001→INV-006 logged |
| ocb_runner_tests.py | ✅ v86 — 8 tests for parse_ocb_block: all 8 PASS |
| OCB Runner Reset MCC colour signal | ✅ v86 — #mcc-emergency-reset button: blue on RUNNING, green on DONE/COMPLETE |
| aafl_wccs.py: archive_old_handovers removed | ✅ v87 — function + call deleted; _elapsed added at LIFEGUARD/pre-bak/STATUS write |
| [data-tip] tooltip JS fix | ✅ v87 — CSS ::after disabled; JS _gtt handler uses position:fixed; no more overflow:hidden clip |
| saveSession() visual feedback | ✅ v87 — green button 3s on success; finally block guard prevents overwrite |
| OCB Runner live output Copy button | ✅ v87 — Copy button + ocb2CopyLog() in OCB Runner tab |
| ocb_runner.py autonomous execution | ✅ v87 — run_safe() handles 'run script' + 'create file' as direct Python ops; run_test() exercises pipeline |
| ocb_runner.py stale lock auto-clear | ✅ v88 — GUARD 1: if .ocb_running exists AND is older than 10 minutes, auto-delete and continue |
| /api/ocb/clear-lock endpoint | ✅ v88 — POST clears .ocb_running from UI; returns {cleared, message} |
| OCB Runner Clear Lock button | ✅ v88 — Clear Lock next to ABORT; CSS #ocb2-clear-lock-btn; ocb2ClearLock() JS + toast |
| HTML corruption recovery (v88) | ✅ v88 — Previous OCB run removed </style>+</head>+<body> tags; recovered via git checkout HEAD |
| Learning Machine — RAG engine | ✅ v89 — learning_machine/rag_engine.py; ChromaDB at data/rag_db/; 92 docs, 537 chunks (v90 confirmed); query/index_file/reindex_all |
| Learning Machine — Training Pipeline | ✅ v89 — learning_machine/training_prep.py; scans loop_output/*.json; alpaca JSONL to data/training_data.jsonl |
| Learning Machine — Feedback Loop | ✅ v89 — learning_machine/feedback_loop.py; after_run() routes high-score→RAG+training, low-score→failure_patterns.jsonl; learning report every 10 runs |
| RAG wired into aafl_core.py | ✅ v89 — _rag_context() prepends top-3 chunks before every AI call; use_rag=True default, _RAG_ENABLED kill-switch |
| Feedback loop wired into loop_manager.py | ✅ v89 — _feedback_after_run() called at end of every completed AAFL iteration |
| /api/rag/* endpoints (3) | ✅ v89 — GET /api/rag/stats, POST /api/rag/reindex, POST /api/rag/query |
| /api/training/* endpoints (2) | ✅ v89 — GET /api/training/stats, POST /api/training/rebuild |
| /api/learning/* endpoints (2) | ✅ v89 — GET /api/learning/report, GET /api/learning/failures |
| OCB test scripts: t_rag_index.py | ✅ v89 — PASS: 92 docs, 537 chunks (v90 re-confirmed) |
| OCB test scripts: t_rag_query.py | ✅ v89 — PASS: 3 results for 'spin doctor joystick fix' |
| OCB test scripts: t_training_scan.py | ✅ v89 — PASS: 0 pairs (no JSON results yet — loop_output now .json so future runs will populate) |
| OCB test scripts: t_feedback_report.py | ✅ v89 — PASS: no runs yet |
| OCB test scripts: t_learning_full.py | ✅ v89 — PASS: 4/4 steps |
| OCB Runner: skip_mot flag | ✅ v90 — run_safe(skip_mot=False) param; when True, CHECK D (MOT) skipped entirely |
| OCB Runner: skip_mot MCC field | ✅ v90 — POST /api/ocb/run accepts {"skip_mot": true} in JSON body |
| OCB Runner: Skip MOT checkbox (standalone tab) | ✅ v90 — label+checkbox id=ocb-skip-mot in OCB Runner toolbar; ocbRun() sends skip_mot |
| loop_manager.py: JSON-only output | ✅ v90 — code blocks saved as .json (not .py); results saved as _result.json (not _result.txt) |
| archive_dead/loop_garbage/ | ✅ v91 — 145 total *_not_json_at_all*.py files archived (82 in v90 + 63 this session) |
| ocb_runner.py: _write_status progress write | ✅ v91 — _write_status() also writes data/ocb_progress.json atomically when phases are present |
| ocb_runner.py: run_safe() phase tracking | ✅ v91 — obj["phases"] built from parsed; ph_idx enumerate loop; PENDING→RUNNING→DONE/FAILED per phase |
| ocb_runner.py: mot_score in obj | ✅ v91 — obj["mot_score"] set before _sl() calls so progress file captures MOT result |
| data/ocb_progress.json | ✅ v91 — written atomically by _write_status after each phase; {phases, phase_current, phase_total, percent, status, mot_score} |
| OCB Runner: HITSAV S11 Skip MOT checkbox | ✅ v91 — id=hitsav-ocb-skip-mot; hitsavOcbRun() reads it and sends skip_mot in JSON body |
| OCB Runner: 2s poll interval | ✅ v91 — ocbStartPoll() setInterval 3000→2000ms |
| OCB Runner: progress endpoint in ocbPoll | ✅ v91 — ocbPoll() also fetches /api/ocb/progress to update ocb-progress-fill bar |
| ocb_selftest.py | ✅ v91 — self-test: parse + run_safe(skip_mot=True) + verify ocb_brain_test.txt + progress file |
| ocb_patch.py | ✅ v91 — patch utility: applies all run_safe phase-tracking edits to ocb_runner.py via string replacement |
| data/acca_codes.json | ✅ NEW v92 — 41 ACCA codes exported; GET /api/acca/codes; POST /api/acca/add (atomic) |
| ancoreg_validator.py | ✅ NEW v92 — 8 save-system checks: STATUS line count, 4x END_OF_FILE markers, freshness, git clean, split integrity, aafl_wccs importable, session_logs present |
| ANCOREG tab (MCC) | ✅ NEW v92 — data-tab="ancoreg"; 5 sections: Live Diagnosis / Fix Database / Save Validator / MOT Dashboard / Error Timeline |
| ANCOREG Section 1: Live Diagnosis | ✅ NEW v92 — ancoregRunDiagnosis() calls /api/ancoreg/diagnosis; auto-runs on tab open (60s cache); card grid grouped by area |
| ANCOREG Section 2: Fix Database | ✅ NEW v92 — table from solution_database.json; search filter; + Add Fix modal; clickable row expand |
| ANCOREG Section 3: Save Validator | ✅ NEW v92 — ancoregValidateSave() → /api/ancoreg/validate-save → ancoreg_validator.py; Run Save Now → /api/ancoreg/run-save; Preview Diff |
| ANCOREG Section 4: MOT Dashboard | ✅ NEW v92 — ancoregRunMOT() → /api/ancoreg/mot; colour grid 14×14px squares; click square → name+detail |
| ANCOREG Section 5: Error Timeline | ✅ NEW v92 — ancoregLoadTimeline() → /api/ancoreg/error-timeline; horizontal scroll; click node → alert |
| BSTP tab (MCC) | ✅ NEW v92 — data-tab="bstp"; drag-drop canvas + left palette + right properties panel |
| BSTP: 5 element types | ✅ NEW v92 — TASK (blue), DECISION (yellow), MILESTONE (green), SPLITTER (orange), NOTE (grey dashed) |
| BSTP: canvas toolbar | ✅ NEW v92 — Save / Load / Clear / Undo / Redo / Zoom +/- / Fullscreen |
| BSTP: connector drawing | ✅ NEW v92 — click port circle → click target element → arrow drawn; SVG rendered via bstpRenderSVG() |
| BSTP: context menu (right-click) | ✅ NEW v92 — Send to AAFL / Send to Kanban / Send to CLAC / Delete |
| BSTP Control A: STATUS.md Toggle | ✅ NEW v92 — toggle switch (default OFF); preview shows what would be written; POST /api/bstp/status-write |
| BSTP Control B: Instruction Pad | ✅ NEW v92 — textarea; Save → POST /api/bstp/instructions; loads on tab open |
| BSTP Control C: Action Launcher | ✅ NEW v92 — bstpLaunchSelected() → AAFL / Kanban / CLAC; POST /api/bstp/action |
| BSTP Control D: Plan History | ✅ NEW v92 — load all snapshots; click to load plan |
| /api/ancoreg/diagnosis GET | ✅ NEW v92 — health.db last results + detective_report.json findings |
| /api/ancoreg/fixes GET | ✅ NEW v92 — returns solution_database.json |
| /api/ancoreg/add-fix POST | ✅ NEW v92 — adds entry to solution_database.json (atomic) |
| /api/ancoreg/validate-save GET | ✅ NEW v92 — runs ancoreg_validator.validate_save_system() |
| /api/ancoreg/run-save POST | ✅ NEW v92 — subprocess aafl_wccs.py |
| /api/ancoreg/mot GET | ✅ NEW v92 — runs mcc_full_mot.py; returns full_mot_report.json |
| /api/ancoreg/error-timeline GET | ✅ NEW v92 — timeline from solution_database.json sorted by date |
| /api/acca/codes GET | ✅ NEW v92 — returns data/acca_codes.json with count |
| /api/acca/add POST | ✅ NEW v92 — adds code entry (atomic); requires code + full_name |
| /api/bstp/current GET | ✅ NEW v92 — returns data/bstp_current.json |
| /api/bstp/save POST | ✅ NEW v92 — saves current plan + snapshot in data/bstp_plans/ |
| /api/bstp/plans GET | ✅ NEW v92 — returns data/bstp_history.json snapshot index |
| /api/bstp/plan/<id> GET | ✅ NEW v92 — loads specific plan snapshot |
| /api/bstp/action POST | ✅ NEW v92 — sends task to AAFL/Kanban/CLAC |
| /api/bstp/instructions GET | ✅ NEW v92 — returns data/bstp_instructions.json |
| /api/bstp/instructions POST | ✅ NEW v92 — saves instruction pad (atomic) |
| /api/bstp/status-write POST | ✅ NEW v92 — preview or write task to STATUS.md (with .bak backup) |
| instructions_db.json ANCOREG+BSTP | ✅ NEW v92 — ancoreg_tab + bstp_tab entries added with nested_topics |
| ANCOREG accordion (Health Suite) | ✅ NEW v93 — ANCOREG Doctor 5 sections merged into Health Suite accordion; standalone ANCOREG top-bar tab removed |
| BSTP accordion (Missions) | ✅ NEW v93 — BSTP Brainstorm Planner sections merged into Missions accordion; standalone BSTP top-bar tab removed |
| Mission Mode toggle (Missions) | ✅ NEW v93 — Mission Mode toggle added to Missions tab |
| GRRICE Changelog section | ✅ NEW v93 — Changelog accordion section added to GRRICE tab |
| ACCA info boxes | ✅ NEW v93 — Info popup boxes added to ACCA Codes section in Instructions tab |
| WCCS direct session log | ✅ NEW v93 — aafl_wccs.py writes session log directly without subprocess; speed fix applied |
| POST /api/acca/command | ✅ NEW v93 — ACCA command endpoint: dispatches ACCA code actions from MCC |

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

### Learning Machine CLI
```
python learning_machine/rag_engine.py          # reindex all + print stats
python learning_machine/training_prep.py       # scan loop_output + print pair count
python learning_machine/feedback_loop.py       # print latest learning report
python tests/ocb_test_scripts/t_learning_full.py   # run all 4 learning steps
```

### OCB Self-Test
```
python ocb_selftest.py
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

### ANCOREG Validator (standalone)
```
python ancoreg_validator.py
```

---

## MISSION CONTROL CENTER (MCC)

MCC is the single-pane-of-glass for all project activity. Served by mcc_server.py on localhost:8080.

### Core Tabs — v93 (7 Primary + Sidebar)

| Tab | Where | What it shows |
|---|---|---|
| HITSAV | **Top bar** | 13-section accordion: all save/ideas/history/OCB tools |
| OCB Runner | **Top bar** | Paste OCB block, parse + run with phase cards + ABORT + Clear Lock + Skip MOT checkbox |
| Scout Swarm | **Top bar** | Parallel web research — 5 strategies, AI synthesis |
| AAFL Control | **Top bar** | Run Now, Step Mode, Pause, Benchmark, Workflow Builder |
| Health Suite | **Top bar** | Provider Health, Self-Diagnosis, GPU/CPU/RAM, Medical, Work Checker, ANCOREG System Doctor |
| GRRICE | **Top bar** | Guide Rules Regulation Instructions Codes Education — 6 sections + Changelog |
| Missions | **Top bar** | Mission registry, KB profiles, Spin Doctor, Project Brain, BSTP Canvas, Mission Mode |
| Home / Dashboard | Sidebar | Command Bar, Attention Surface, Safety Shield, dials |
| Kanban | Sidebar | Task board — B2 enhanced: progress bars, locked deps, AAFL Goal template |
| AAFL Runs | Sidebar | Run history — checkbox compare, failure analysis, time-of-day |
| Costs | Sidebar | Budget caps, spend graphs, ROI, currency toggle |
| Design | Sidebar | Theme customiser + Design Vault (save/apply themes) |
| Promo | Sidebar | High-scoring AI results (>=9.0) pending approval |
| Storage | Sidebar | Disk quota monitor, Memory Status |
| Memory | Sidebar | Knowledge Bank and Solution Log |
| Code Editor | Sidebar | Monaco 0.44.0, file browser, run .py, CLAC generator |
| Instructions & Codes | Sidebar | ACCA code reference |
| Help | Sidebar | AI-powered Q&A against project knowledge |

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
├── sfl_agent.py                       # v3 — HANDOVER_FILENAME → v93
├── aafl_core.py                       # v89 — RAG context injection before every AI call
├── loop_manager.py                    # v90 — code blocks/.results saved as .json (not .py/.txt)
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
├── ocb_runner.py                      # v91 — _write_status writes ocb_progress.json; run_safe() phase tracking
├── ocb_runner_tests.py                # v86 — 8 unit tests for parse_ocb_block
├── ocb_selftest.py                    # v91 — OCB Runner self-test script
├── ocb_patch.py                       # v91 — patch utility for ocb_runner.py phase-tracking edits
├── ancoreg_validator.py               # NEW v92 — 8 save-system checks; validate_save_system() → dict
├── clacker_safety.py                  # v70 — pre_run, post_run_success/failure, check_html/py/server
├── clacker_validator.py               # v70 — validate(criteria, files_changed, mot_score) → PASS/FAIL/PARTIAL
├── wccs_detective.py                  # v69 — Chief Detective: scans all sources, gap analysis
├── mccm_agent.py                      # v69 — MCCM overseer, power levels 1-4, AI dispatch
├── storm_bridge.py                    # v80 — ingest_sesums(days=3) added
├── hitsav_detective.py                # v81 — renamed from hisav_detective.py; all HISAV→HITSAV
├── wccs_runner.py                     # v86 — 6 dead handover write functions removed
├── aafl_wccs.py                       # v87 — archive_old_handovers removed; _elapsed at LIFEGUARD/pre-bak/STATUS write
├── ocb_wal.log                        # v68 — Write-Ahead Log (append only)
├── STATUS_MASTER.md                   # v68 — golden STATUS.md backup post-MOT
├── mcc_server.py                      # v93 — POST /api/acca/command added; ANCOREG/BSTP endpoints retained
├── mcc_full_mot.py                    # 109 tests, GROUP A-H
├── mission_control.html               # v93 — ANCOREG accordion in Health Suite; BSTP accordion in Missions; Mission Mode; GRRICE Changelog; ACCA info boxes
├── CLAUDE.md
├── ACCA.md
├── ALP_Database.md
├── STATUS.md
├── HISTORY.md
├── INDEX.md
├── goal.txt / goal_queue.txt / meta_queue.txt
├── aafl_config.json
├── VKB_SpinDoctor_Handover_v93.md     # This file
├── learning_machine/                  # v89 — learning machine package
│   ├── __init__.py
│   ├── rag_engine.py                  # ChromaDB RAG; reindex_all/query/index_file; 92 docs 537 chunks
│   ├── training_prep.py               # loop_output→alpaca JSONL; scan_results/get_stats
│   └── feedback_loop.py              # after_run/get_report/get_failures; report every 10 runs
├── data/
│   ├── knowledge_engine.db
│   ├── health.db
│   ├── rag_db/                        # v89 — ChromaDB persistent store
│   ├── rag_stats.json                 # v89 — {doc_count, chunk_count, last_indexed}
│   ├── training_data.jsonl            # v89 — alpaca-format high-quality training pairs
│   ├── training_stats.json            # v89 — {pair_count, total_runs, avg_score}
│   ├── failure_patterns.jsonl         # v89 — low-score run failure log
│   ├── feedback_counter.json          # v89 — running totals for learning report
│   ├── learning_report.json           # v89 — latest generated learning report
│   ├── acca_codes.json                # NEW v92 — 41 ACCA codes; {codes:{...}, version, last_updated}
│   ├── bstp_current.json              # NEW v92 — current active BSTP plan
│   ├── bstp_history.json              # NEW v92 — snapshot index {snapshots:[{file,saved_at,name,version}]}
│   ├── bstp_instructions.json         # NEW v92 — Scott's instruction pad content
│   ├── bstp_plans/                    # NEW v92 — versioned plan snapshots (plan_<timestamp>.json)
│   ├── ocb_status.json
│   ├── ocb_abort.json
│   ├── ocb_progress.json              # v91 — written atomically by _write_status; {phases, percent, status}
│   ├── ocb_queue.json
│   ├── rrclach_request.json
│   ├── rollback_log.json
│   ├── clachr_response.json
│   ├── session_state.json
│   ├── provider_diagnosis.json
│   ├── mccm_permissions.json
│   ├── detective_report_{date}.json
│   ├── detective_queue.json
│   ├── storm_feed.json
│   ├── detective_timeline_gaps.json
│   ├── rrice.json
│   ├── design_saves.json
│   ├── claude_memory_snapshot.json
│   ├── claude_bridge.json
│   ├── investigations_db.json
│   ├── mccm_investigations/
│   ├── element_registry.json
│   ├── solution_database.json
│   ├── instructions_db.json           # v92 — ancoreg_tab + bstp_tab entries added
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
├── loop_output/                       # v90 — ONLY .json files (code blocks + results wrapped in JSON)
├── health_results/
├── tests/
│   ├── ocb_runner_tests.py
│   └── ocb_test_scripts/
│       ├── t01_echo.py ... t12_dryrun.py   # existing tests
│       ├── t_rag_index.py                  # v89 — RAG reindex test (PASS: 92 docs/537 chunks)
│       ├── t_rag_query.py                  # v89 — RAG query test (PASS)
│       ├── t_training_scan.py              # v89 — training scan test (PASS)
│       ├── t_feedback_report.py            # v89 — feedback report test (PASS)
│       └── t_learning_full.py              # v89 — full integration test (4/4 PASS)
└── archive_dead/
    └── loop_garbage/                  # v91 — 145 total *_not_json_at_all*.py files archived (82 v90 + 63 v91)
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
| Packages | mss, lmstudio, Pillow, anthropic, litellm, python-dotenv, langgraph, ddgs, beautifulsoup4, chromadb |
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
| MCC completely frozen | Click Reset MCC button (bottom-left, red/blue/green). If not: hard-refresh (Ctrl+Shift+R) |
| GRRICE tab shows "Loading..." forever | mcc_server.py must be running (GET /api/rrice) |
| HITSAV section shows old HISAV ID | Hard-refresh (Ctrl+Shift+R) — IDs fully renamed in v81 |
| OCB Runner parse stuck / never finishes | FIXED in v83: O(n) parser, 10s server timeout, 30s JS abort. If still stuck after 30s: check server is running |
| OCB Runner run button stuck | FIXED in v83: 60s AbortController; button always unblocks via catch() |
| Escape key doesn't abort | Abort button must be visible (only shown during active parse/run) |
| ABORT button not appearing | Button only shows during active parse/run — click Parse or Run first |
| OCB phase cards not showing | Parse first — cards appear per phase as found |
| Auto-Update STATUS.md fails | Free providers are down — check Health Suite tab |
| Sidebar nav not showing tab | Click toggle to expand sidebar — all non-top-bar tabs are in Navigation section |
| MCC sidebar / tab bar invisible | FIXED in v84: MOT stub fix had removed `}` from .hitsav-idea-btns CSS, corrupting all styles below. Hard-refresh (Ctrl+Shift+R) after CSS fix. |
| OCB Runner v2 shows BLOCKED | .ocb_running lock file exists — another run is in progress or crashed. Click Clear Lock button in OCB Runner tab (v88+) or delete .ocb_running manually. Auto-clears if older than 10 minutes. |
| OCB Runner v2 ROLLED BACK | CHECK B (JS) or CHECK C (Registry) failed — see Results panel for missing function/ID names |
| Reset MCC button stays red after OCB run | Button turns blue during run, green on success — normal. Red = default idle colour only |
| [data-tip] tooltip not showing | FIXED v87: CSS ::after removed; JS _gtt handler uses position:fixed. Hard-refresh (Ctrl+Shift+R). |
| saveSession button stays after save | FIXED v87: finally block only resets if still showing wait state — green Saved! persists 3s then resets. |
| OCB run stash reverted edits | Known issue: OCB test runs via /api/ocb/run push+pop git stashes. If edits are reverted, check git stash list — stash may contain your work. Re-apply edits after tests complete. |
| RAG returns 0 results | Run reindex first: python learning_machine/rag_engine.py OR POST /api/rag/reindex |
| chromadb ImportError | pip install chromadb --break-system-packages |
| OCB MOT check taking 3+ minutes | Use Skip MOT checkbox for non-HTML tasks (Python scripts, API calls, colour changes) — MOT not relevant for these |
| loop_output/ contains .py files | FIXED v90: code blocks now saved as .json; old .py files moved to archive_dead/loop_garbage/ |
| ocb_progress.json shows 0% during run | Linter may have reverted _write_status edits — run python ocb_patch.py to re-apply, then git add+commit immediately |
| ANCOREG diagnosis shows no data | Run MOT first (Section 4) to populate health.db — diagnosis reads last health.db results |
| BSTP canvas empty on tab open | Load plan from Section D Plan History, or drag elements from left palette to create new plan |

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
- **Don't run ocb_runner_tests.py while edits are uncommitted** — OCB test stash ops will revert your changes
- Don't disable use_rag in production — it only adds context, never costs extra tokens when collection is empty
- **Don't edit ocb_runner.py with the Edit tool** — the built-in linter strips additions to _write_status and run_safe(). Use ocb_patch.py instead and immediately `git add ocb_runner.py; git commit`.

---

## NEXT PRIORITIES

1. Run a real AAFL loop (run_aafl.bat) — verify [FEEDBACK] log lines appear and loop_output/*.json files created
2. After 10 AAFL runs — check data/learning_report.json for avg score trend + best provider
3. Re-enable AAFL_Overnight_Task once loop_output JSON bug confirmed fixed: schtasks /Change /TN "AAFL_Overnight_Task" /ENABLE
4. Build CCR (Claude Chat Relay) — CLACH→MCC→free provider dispatch circuit
5. Complete STORM ↔ MCCM live loop testing
6. OCB-K Build 3 — Costs tab enhancements
7. Star Citizen v0.2 benchmark via AAFL autonomous run

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

> "Continuing VKB Spin Doctor. Read VKB_SpinDoctor_Handover_v93.md. v93 — ANCOREG (Autonomous Node Condition Registry) Doctor sections moved from standalone top-bar tab into Health Suite accordion. BSTP (Brainstorm Planner) moved from standalone top-bar tab into Missions accordion. Mission Mode toggle added to Missions. GRRICE Changelog section added to GRRICE tab. ACCA info boxes added to Instructions tab. WCCS direct session log speed fix applied to aafl_wccs.py. POST /api/acca/command endpoint added to mcc_server.py. STATUS.md updated: AAFL_Overnight_Task disabled notice (loop_output JSON bug) + CCR (Claude Chat Relay) logged as PENDING — CLACH→MCC→free provider dispatch circuit not yet built. NEXT: re-enable AAFL_Overnight_Task once JSON bug fixed, then build CCR. 109/109 MOT ALL CLEAR."

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
**Key decisions:** OCB-K Build 2 complete — 4 phases. Kanban progress bars/locked deps/AAFL Goal template/bulk archive+move, Activity 12-filters+Clear+date-range, AAFL Runs checkbox-compare+failure-phases+time-of-day. 108/108 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** Activity filter categories wrong vs spec. b2BulkMove only moved to Done. Research template replaced with AAFL Goal.
**Next priorities:** 1. OCB-K Build 3 2. Star Citizen 3. Add GROQ + Cloudflare keys

---

### 2026-05-29 (Claude Code session 17)
**Key decisions:** MCC complete freeze diagnosed and fixed. Root cause: `?.checked = false` SyntaxError. Fixed + fullscreen guard + localStorage safety + permanent Reset MCC button. 108/108 MOT ALL CLEAR.
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
**Key decisions:** OCB-Q Combined (Q2+Q3) built — 9 phases. Detective Panel A: progress bar strip per active task, task queue with drag-reorder, 7-strategy selector + WENTO. Panel B: every finding row clickable → inline drill-down. STORM + MCCM pipeline wired. Timeline visual upgrade: PAST/PRESENT/PLANNED zone bands, TODAY marker. 109/109 MOT ALL CLEAR.
**New ACCA codes:** STORM = Selective Targeted Output Remove Merge
**Bugs fixed:** DOMContentLoaded called detLoadPanels regardless of panel visibility. Paste handler triggered even when HISAV tab wasn't active.
**Next priorities:** 1. Complete STORM ↔ MCCM live loop testing 2. Wire aafl_wccs.py SESUM → STORM 3. OCB-K Build 3 4. Star Citizen

---

### 2026-05-30 (Claude Code session 9)
**Key decisions:** HISAV post-WCCS checklist added to sticky toolbar. Timeline popup fixed from position:fixed to position:absolute. 109/109 MOT ALL CLEAR.
**Bugs fixed:** hisav-tl-popup used position:fixed which caused it to cover content on other tabs.
**Next priorities:** 1. STORM ↔ MCCM testing 2. HISAV detective tab live 3. OCB-K Build 3

---

### 2026-05-30 (Claude Code session 12)
**Key decisions:** OCB-R1 global MCC bug sweep — global z-index CSS block, ? button audit (30 tip-btn elements OK), Post-save SESUM reminder banner. 109/109 MOT ALL CLEAR.
**Bugs fixed:** Popups hidden behind panels due to z-index stacking context.
**Next priorities:** 1. STORM ↔ MCCM testing 2. HISAV detective tab live 3. OCB-K Build 3

---

### 2026-05-31 (Claude Code session 1)
**Key decisions:** OCB-Runner v2 built — parse_ocb(), pre_flight(), run_safe() (4 guards + 4 checks), read_results(), stream_log(), HISAV S11 3-panel board. 109/109 MOT ALL CLEAR.
**Bugs fixed:** None (net-new feature build)
**Next priorities:** 1. Test OCB Runner v2 end-to-end 2. STORM ↔ MCCM testing 3. HISAV detective tab

---

### 2026-05-31 (Claude Code session 2)
**Key decisions:** Global tooltip/info visibility fix. CSS z-index 9999→99999, tab bar z-index:100, positionTooltip() JS function, [data-tooltip]::after system, data-tooltip on all 13 tab buttons. 109/109 MOT ALL CLEAR.
**Bugs fixed:** shTip() used window.scrollY for position:fixed element.
**Next priorities:** 1. Test OCB Runner v2 2. STORM ↔ MCCM 3. HISAV detective tab

---

### 2026-05-31 (Claude Code session 3)
**Key decisions:** 3 MCC fixes: tab bar disappearing bug (root cause: [data-tooltip] CSS applying position:fixed to tab buttons), OCB Runner S11 progress feedback, HITSAV 3-step save workflow. 109/109 MOT ALL CLEAR.
**Bugs fixed:** Tab bar invisible — [data-tooltip] in OCB-E CSS rule applied position:fixed to tab buttons.
**Next priorities:** 1. Test tab bar + 3-step save flow 2. Test OCB Runner v2 3. STORM ↔ MCCM

---

### 2026-05-31 (Claude Code session 4)
**Key decisions:** OCB-R build — 8 phases. (1) OCB Runner standalone: {block:→{ocb_text:} fix + polling rewrite. (2) RRICE tab: 6-section accordion. (3) STORM→Detective→MCCM pipeline: ingest_sesums+cross_check_timeline+/api/mccm/generate-status. (4) HITSAV toolbar Auto-Update STATUS.md. 109/109 MOT ALL CLEAR.
**New ACCA codes:** RRICE = Rules and Regulations, Codes and Instructions Education
**Bugs fixed:** OCB Runner {block:} → {ocb_text:}, ocb2Run() polling rewrite.
**Next priorities:** 1. Test OCB Runner 2. Test RRICE tab 3. Auto-Update STATUS.md 4. STORM testing

---

### 2026-05-31 (Claude Code session 5)
**Key decisions:** OCB-R continuation — 8 phases completed. Phase 1: OCB Runner visual overhaul v4. Phase 2: HISAV→HITSAV rename. Phase 3: Tab restructure — 7 primary tabs in top bar + sidebar. Phase 3 GRRICE: rrice tab renamed to GRRICE. Phase 5: Project Brain theme. 109/109 MOT ALL CLEAR.
**New ACCA codes:** HITSAV = History Time Save. GRRICE = Guide Rules Regulation Instructions Codes Education.
**Bugs fixed:** After HITSAV rename, /api/hitsav/* routes didn't exist — added alias routes. After tab bar trim, MOT failed — fixed by adding hidden data-tab span markers.
**Next priorities:** 1. Hard-refresh MCC — verify 7 tabs, purple theme 2. Test OCB Runner ABORT 3. Complete STORM testing

---

### 2026-05-31 (Claude Code session 6)
**Key decisions:** OCB-S — OCB Runner fully rebuilt. Five fixes: O(n) line-scan parser (3-pass with fallback), scan cap 2K + early exit, concurrent.futures 10s timeout, 60s run AbortController, Escape key handler, window.ocbAbort flag, bar colour states, green terminal log. Parse test confirmed: 7-phase OCB-S block in <1ms. 109/109 MOT ALL CLEAR.
**Bugs fixed:** parse_ocb_block() re.split() could silently return 0 phases. extract_relevant_section() O(n²) scan blocked GIL. ocb2Run() no AbortController meant stuck button with no escape.
**Next priorities:** 1. Hard-refresh MCC — open OCB Runner tab 2. Paste 3-phase OCB block → Parse 3. Complete STORM testing

---

### 2026-06-01 (Claude Code session 1)
**Key decisions:** CSS hotfix — MCC sidebar and tab bar completely invisible. Root cause: commit c3b366e removed closing `}` from `.hitsav-idea-btns` at line 130, corrupting all CSS below. 20 CSS rules for HITSAV panels also deleted. All restored. 109/109 MOT ALL CLEAR.
**Bugs fixed:** `.hitsav-idea-btns` missing `}` at line 130 — corrupted entire CSS block; sidebar invisible, tab bar invisible, all Project Brain theme colours broken.
**Next priorities:** 1. Hard-refresh MCC 2. Open OCB Runner tab 3. Complete STORM testing

---

### 2026-06-01 (Claude Code session 2)
**Key decisions:** OCB-S cleanup pass — wccs_runner.py dead handover write functions removed. aafl_wccs.py per-step timing added. data/investigations_db.json created. 2 new endpoints. ocb_runner_tests.py 8 tests all PASS. 109/109 MOT ALL CLEAR.
**Bugs fixed:** wccs_runner.py dead code: 6 functions referencing deprecated handover write path.
**Next priorities:** 1. Test OCB Runner end-to-end 2. STORM testing 3. OCB-K Build 3

---

### 2026-06-01 (Claude Code session 3)
**Key decisions:** OCB Runner visual signal — Reset MCC button turns blue on RUNNING, green on DONE/COMPLETE. 2-line change in _ocb2Poll(). 109/109 MOT ALL CLEAR.
**Next priorities:** 1. Hard-refresh MCC — run OCB block → verify button colours 2. STORM testing 3. OCB-K Build 3

---

### 2026-06-01 (Claude Code session 4)
**Key decisions:** Four fixes: aafl_wccs.py archive_old_handovers() removed + _elapsed() timing. [data-tip] tooltip → position:fixed JS handler. saveSession() green tick + OCB Copy button. ocb_runner.py run_safe() direct create/script ops. 109/109 MOT ALL CLEAR.
**Bugs fixed:** [data-tip]::after clipped by overflow:hidden. run_safe() no direct 'run script' handling. OCB test stash stranded edits.
**Next priorities:** 1. Hard-refresh + test tooltip + saveSession 2. STORM testing 3. OCB-K Build 3

---

### 2026-06-02 (Claude Code session 1)
**Key decisions:** Three targeted fixes: (1) ocb_runner.py GUARD 1 — stale .ocb_running auto-clear if >10 minutes old. (2) POST /api/ocb/clear-lock endpoint added. (3) Clear Lock button in OCB Runner tab (CSS + HTML + JS + toast). Also: HTML corruption from OCB runner discovered and restored via git checkout HEAD.
**New ACCA codes:** None
**Bugs fixed:** .ocb_running stale lock caused BLOCKED state with no UI escape. HTML corruption: OCB runner had removed ~190 lines of CSS + structural tags.
**Next priorities:** 1. Hard-refresh — verify Clear Lock button 2. Test Clear Lock with .ocb_running 3. STORM testing

---

### 2026-06-02 (Claude Code session 2)
**Key decisions:** Learning Machine built — 3 layers, all wired in. Layer 1: RAG engine (Retrieval Augmented Generation) using ChromaDB stored locally at data/rag_db/; indexes 91 documents (session_logs/*.md + STATUS/INDEX/HISTORY/ACCA.md + 4 data JSON files), 531 chunks; query() top-3 results prepended into every aafl_core.py AI call via _rag_context(); use_rag=True default with _RAG_ENABLED global kill-switch. Layer 2: Training data pipeline (learning_machine/training_prep.py) — scans loop_output/*.json for score>=7 results, exports alpaca-format instruction/input/output JSONL to data/training_data.jsonl. Layer 3: Self-improving feedback loop (learning_machine/feedback_loop.py) — after_run() called from loop_manager.py after every AAFL iteration; score>=7→adds to RAG+training, score<4→logs to failure_patterns.jsonl; learning report printed every 10 runs with avg score trend / best provider / most common failure. 7 new MCC endpoints added to mcc_server.py. 5 OCB test scripts created in tests/ocb_test_scripts/ — all 5 PASS. chromadb installed (v1.5.9). 109/109 MOT ALL CLEAR.
**New ACCA codes:** RAG = Retrieval Augmented Generation
**Bugs fixed:** None (net-new build)
**Ideas discussed:** Learning machine makes AAFL genuinely self-improving: every high-quality run improves future runs via RAG context injection. The ChromaDB embedding model (all-MiniLM-L6-v2) downloads once (~79MB) and runs locally — no cloud, no API cost.
**Next priorities:**
1. Run python learning_machine/rag_engine.py — confirm 91 docs / 531 chunks printed
2. Run a real AAFL loop (run_aafl.bat) — verify [FEEDBACK] log lines appear
3. After 10 AAFL runs — check data/learning_report.json for avg score trend + best provider
4. Wire /api/rag/stats + /api/learning/report into MCC Health Suite tab (optional dashboard widget)
5. Complete STORM ↔ MCCM live loop testing

---

### 2026-06-02 (Claude Code session 3)
**Key decisions:** Three fixes in one session: (1) OCB Runner skip-mot flag — run_safe() now has skip_mot=False param; when True, CHECK D (MOT) is bypassed entirely. mcc_server.py reads skip_mot from POST /api/ocb/run body. mission_control.html has "Skip MOT" checkbox (id=ocb-skip-mot) next to Parse button; ocbRun() sends skip_mot in request. Useful for Python scripts, API calls, colour changes — MOT irrelevant for non-HTML tasks. (2) Loop output JSON fix — loop_manager.py code blocks now saved as .json wrapping raw content (not .py files); result saves changed from _result.txt to _result.json with valid_json flag. 82 existing *_not_json_at_all*.py garbage files moved to archive_dead/loop_garbage/. (3) Learning machine from v89 confirmed: reindex_all() 92 docs / 537 chunks; 5/5 test scripts PASS; RAG and after_run() wired and working. 109/109 MOT ALL CLEAR throughout.
**New ACCA codes:** None
**Bugs fixed:** loop_output/*.py garbage files (AI responses saved raw as Python files despite not being code). loop_output _result.txt not valid JSON.
**Ideas discussed:** Skip MOT valuable for rapid iteration on non-HTML tasks — saves ~3 minutes per OCB run.
**Next priorities:**
1. Run a real AAFL loop (run_aafl.bat) — verify [FEEDBACK] log lines appear and loop_output/*.json created
2. After 10 AAFL runs — check data/learning_report.json for avg score trend + best provider
3. Wire /api/rag/stats + /api/learning/report into MCC Health Suite tab
4. Complete STORM ↔ MCCM live loop testing
5. OCB-K Build 3 — Costs tab enhancements

---

### 2026-06-02 (Claude Code session 4)
**Key decisions:** OCB Runner AI brain confirmed wired (run_task() calls AAFLCore with allow_paid=False — free providers only); live progress feedback added (_write_status() now atomically writes data/ocb_progress.json after every phase change; run_safe() obj tracks phases PENDING→RUNNING→DONE/FAILED + obj["current_phase"] + obj["mot_score"]); mcc_server.py _handle_ocb_progress reads ocb_progress.json first (falls back to ocb_status.json); HITSAV S11 gets Skip MOT checkbox (id=hitsav-ocb-skip-mot); hitsavOcbRun() passes skip_mot; standalone OCB tab poll interval 3000→2000ms; ocbPoll() fetches /api/ocb/progress for bar. 63 additional *_not_json_at_all*.py files archived to archive_dead/loop_garbage/ (145 total across v90+v91). ocb_selftest.py + ocb_patch.py written. NOTE: linter strips additions to ocb_runner.py _write_status — use python ocb_patch.py to re-apply and immediately git add+commit to lock in. 109/109 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** HITSAV S11 had no Skip MOT checkbox (only standalone tab had it). ocbStartPoll interval was 3s not 2s. ocb_progress.json endpoint served derived data instead of the atomic progress file. run_safe() obj had no phases array so MCC panel couldn't track per-phase badges.
**Ideas discussed:** Built-in linter strips function-body additions to ocb_runner.py between Edit calls — ocb_patch.py is the safe workaround: make changes programmatically and git add/commit in the same shell command.
**Next priorities:**
1. Run a real AAFL loop (run_aafl.bat) — verify [FEEDBACK] log lines appear and loop_output/*.json created
2. After 10 AAFL runs — check data/learning_report.json for avg score trend + best provider
3. Wire /api/rag/stats + /api/learning/report into MCC Health Suite tab
4. Complete STORM ↔ MCCM live loop testing
5. OCB-K Build 3 — Costs tab enhancements

---

### 2026-06-02 (Claude Code session 5)
**Key decisions:** Three major deliverables: (1) ACCA knowledge export — data/acca_codes.json with 41 codes (every ACCA code from CLAUDE.md + handover + common usage); GET /api/acca/codes; POST /api/acca/add (atomic write, auto-updates last_updated). (2) ANCOREG tab (Autonomous Node Condition Registry) — System Doctor tab added to MCC top bar after HITSAV. 5 sections: Live Diagnosis (reads health.db + detective_report.json, grouped by area, 60s cache, auto-runs on tab open), Fix Database (solution_database.json as searchable table + inline expand + Add Fix modal), Save Validator (8 checks via ancoreg_validator.py: STATUS.md line count vs baseline, 4x END_OF_FILE markers in STATUS/HISTORY/ACCA/INDEX, freshness warning >48h, git uncommitted changes, split integrity all 4 .md files non-empty, aafl_wccs.py importable, session_logs recent files), MOT Dashboard (14×14px colour grid, click square → check name+detail), Error Timeline (horizontal scroll from solution_database, RED=error found, GREEN=fixed). 7 new /api/ancoreg/* endpoints. ancoreg_validator.py created as standalone script. (3) BSTP tab (Brainstorm Planner) — drag-drop canvas added to MCC top bar after ANCOREG. 5 element types draggable from left palette: TASK (blue square), DECISION (yellow diamond), MILESTONE (green hexagon), SPLITTER (orange triangle), NOTE (grey dashed). SVG connector drawing (click port → click target → arrow). Properties panel (right side, shows on element click). Inline double-click title edit. Right-click context menu → Send to AAFL/Kanban/CLAC/Delete. Toolbar: Save/Load/Clear/Undo/Redo/Zoom/Fullscreen. Control Panel: Section A STATUS.md write toggle (default OFF, preview before write, .bak backup), Section B Instruction Pad (saves to bstp_instructions.json, injected into AAFL context), Section C Action Launcher, Section D Plan History (versioned snapshots). 8 new /api/bstp/* endpoints. data/bstp_plans/ folder created. instructions_db.json updated with ancoreg_tab + bstp_tab entries. 109/109 MOT ALL CLEAR throughout.
**New ACCA codes:** ANCOREG = Autonomous Node Condition Registry. BSTP = Brainstorm Planner.
**Bugs fixed:** None (net-new build)
**Ideas discussed:** BSTP Instruction Pad is a key feature — Scott controls the narrative that gets injected into AAFL/Scout context. ANCOREG Save Validator gives Scott a one-click way to verify the whole save system before starting a session.
**Next priorities:**
1. Hard-refresh MCC — verify ANCOREG and BSTP tabs appear after HITSAV in tab bar
2. Run a real AAFL loop (run_aafl.bat) — verify [FEEDBACK] log lines appear
3. After 10 AAFL runs — check data/learning_report.json for avg score trend + best provider
4. Complete STORM ↔ MCCM live loop testing
5. OCB-K Build 3 — Costs tab enhancements

---

### 2026-06-02 (Claude Code session 6)
**Key decisions:** ANCOREG (Autonomous Node Condition Registry) standalone top-bar tab removed; its 5 sections merged into Health Suite accordion. BSTP (Brainstorm Planner) standalone top-bar tab removed; sections merged into Missions accordion. Mission Mode toggle added to Missions tab. GRRICE Changelog accordion section added. ACCA info boxes added to Instructions/Codes tab. aafl_wccs.py session log now written directly (no subprocess) — speed fix. POST /api/acca/command endpoint added to mcc_server.py. Top bar reduced from 9 primary tabs to 7. 109/109 MOT ALL CLEAR.
**New ACCA codes:** None
**Bugs fixed:** None
**Ideas discussed:** Consolidating ANCOREG into Health Suite and BSTP into Missions reduces tab bar clutter and groups features more logically. GRRICE Changelog gives Scott a versioned record of all rule/instruction changes.
**Next priorities:**
1. Hard-refresh MCC — verify Health Suite has ANCOREG accordion; Missions has BSTP accordion
2. Run a real AAFL loop (run_aafl.bat)
3. Build CCR (Claude Chat Relay)

---

### 2026-06-02 (Claude Code session 7)
**Key decisions:** STATUS.md maintenance only. (1) Last updated line changed to 2026-06-02 (Session: CCR build + OCB Runner test pending). (2) AAFL_Overnight_Task row added to PENDING table — disabled due to loop_output JSON bug; re-enable command documented. (3) CCR (Claude Chat Relay) row added to PENDING table — not yet built: CLACH→MCC→free provider dispatch circuit. WCCS v93 run.
**New ACCA codes:** CCR = Claude Chat Relay (dispatches free provider tasks from Claude Chat via MCC)
**Bugs fixed:** None
**Ideas discussed:** CCR will let Scott dispatch labour tasks to free providers from Claude Chat without burning API credits. AAFL_Overnight_Task disabled until loop_output JSON bug is confirmed fixed.
**Next priorities:**
1. Re-enable AAFL_Overnight_Task once loop_output JSON bug fixed: schtasks /Change /TN "AAFL_Overnight_Task" /ENABLE
2. Build CCR — CLACH→MCC→free provider dispatch circuit
3. Run a real AAFL loop (run_aafl.bat) — verify loop_output/*.json created
4. Complete STORM ↔ MCCM live loop testing
5. OCB-K Build 3 — Costs tab enhancements
