# STATUS — VKB Spin Doctor
**Last updated:** 2026-05-29 (OCB-N) | **Updated by:** aafl_wccs.py
**Companion files:** INDEX.md | HISTORY.md | ACCA.md

---

## WHO IS SCOTT — READ THIS FIRST
- Brain injury (BI) 2023 — ONE STEP AT A TIME. No exceptions. Never stack steps.
- Beginner with code — explain what's being built as you go
- Always expand acronyms on first use
- Always include keyboard shortcuts inline (e.g. Windows key + X)
- Tables preferred for structured info
- Number all options — Scott replies with just a number
- No bullshit — if something's hard or slow, say so upfront
- DSP rule — Before giving ANY CLAC block, ALWAYS ask "DSP? (claude --dangerously-skip-permissions)"

---

## MISSION PRIORITY ORDER
1. ALP (Allowance Preservation) — absolute Rule No.1
2. AAFL is THE PROJECT now — Spin Doctor is the benchmark/test subject
3. ACCA codes generated as bonus, organised later
4. Spin Doctor = ultimate validation of AAFL
5. Promo explored last — proof of concept
6. AAFL + Spin Doctor must be fluid, flexible, reusable on any project
7. Could become bigger platform than original idea
8. Claude is master teacher — keeps Scott on track
9. WS+CA opportunities = absolute duty to flag. TIME is ALP's brother.
10. Always provide links + copy boxes
11. WCCS triggered automatically — never ask
12. Never write code unnecessarily — update existing where possible
13. Spin Doctor games are not end goal — AAFL is
14. Spin Doctor success = AAFL success

---

## CURRENT STATUS — BUILT AND WORKING
| Component | Notes |
|---|---|
| v0.1 spin fix | War Thunder confirmed working |
| spin_doctor.py | ~1057 lines, 3 tabs (Fix / Conductor / KB) |
| sfl_agent.py v3 | ~920 lines, ACP v1, handover injection, call_aafl() |
| aafl_core.py | 14 providers, Cerebras=gpt-oss-120b, reasoning_content fallback |
| loop_manager.py | Plan-Work-Verify-Store. Phases B+C+D. AGENT_SYSTEM injected. 4 bugs fixed. |
| evaluator.py | Result scorer 0-10 |
| researcher.py | research() + scout() with source reputation |
| memory_bank.py | SQLite — knowledge, solution_log, source_reputation |
| meta_loop.py | Self-improving meta-loop. Real data injection fixed. |
| chief_scout.py | Parallel scout — 5 strategies, Mistral synthesis |
| mcu_optimizer.py | Reads handover + session logs + board, sends to Mistral, rewrites kanban JSON. WCCS step 6. |
| dashboard_builder.py | MCC data builder. Atomic write. --dry-run flag. |
| task_router.py | Classifies AAFL/CLAC/SONNET/OPUS. 88 lines. |
| problems/conductor.py | 619 lines, 22 problems |
| problems/win_hardener.py | 9 problems W-001-W-009 |
| problems/ed_bind_reset.py | ED Bind Reset prevention |
| mission_control.html | MCC — 19+ tabs, JS audit complete, zero missing functions |
| mcc_server.py | Bridges MCC HTML to filesystem. 30+ endpoints. |
| data/devices.json | 98 devices with VID/PID lookup |
| AAFL autonomous runs | 4 goals, scores 8.07-9.33, DB cache hit confirmed |
| Regression test | PASS 8.83/10 |
| ALP_Database.md | 17 entries |
| Handover split | INDEX/STATUS/HISTORY/ACCA applied 2026-05-20 |
| aafl_wccs.py | Built 2026-05-20. Permanent WCCS fix (free Mistral). |
| merge_sessions.py + .bat | Built 2026-05-23. DSP required |
| MCC MOT 108/108 | ALL CLEAR 2026-05-23 |
| mss library | Installed 2026-05-23 (fixes sfl_agent pre-existing error) |
| Build 1 (10 features) | 13/13 modules, 12/12 tests PASS. Complete 2026-05-23 |
| Plugin/module architecture | modules/, module_registry.json, module_loader.py |
| Preset system | presets/, 3 starters, preset bar in MCC |
| aafl_config.json | Confidence threshold + cost cap controls |
| retry_manager.py | Auto-retry with retry_log.json |
| smart_suggester.py | Goal suggestion engine |
| chain_runner.py | Chain mode for sequential goals |
| scout_timer.py | Timed scout with indefinite mode |
| sources_library.json | Source discovery library |
| storage_manager.py | Storage tab + storage_config.json |
| Stuck Inbox (MCC) | Severity field, bulk resolve, AFNA suggestions |
| MCC UI drill-downs | WCCS tab: Auto-Save Log, History Search, Session Logs, Rewind+Edit, Diff Viewer. Home: Provider Health drill-down, Self-Diagnosis tab, 6 gauges, 4 quick-action buttons |
| SAVE_NOW.bat | One-click save, auto-creates chat_latest.txt if missing |
| Auto-Sunday merge | Wired into aafl_wccs.py, runs merge_sessions on Sundays |
| Pre-flight ALP check | Added to aafl_wccs.py |
| WCCS skill v2 | Uploaded 2026-05-24 |
| Action plan skill | Uploaded 2026-05-24 |
| MCC copy buttons | Home tab — Copy STATUS.md + Copy HISTORY.md with green toast |
| MCP endpoints | /api/status, /api/history, /api/acca, /api/health all live in mcc_server.py |
| Auto git push | aafl_wccs.py pushes to remote after every commit (non-fatal on failure) |
| DESIGN_RULES.md | FFUE + dual-mode (workstation/API) documented. All 4 components covered. |
| LiteLLM installed | Already installed + comment at aafl_core.py:201. Full integration pending. |
| mcc_test.py | Test session completed successfully 2026-05-24. 133/138 PASS |
| mcc_test.py captures | 5 test sessions added from mcc_test.py |
| wccs_runner.py | Original WCCS runner (pre-aafl_wccs). Still present. |
| aafl_watchdog.py | Safety watchdog — built 2026-05-20. Wiring status UNCONFIRMED — must verify before overnight run. |
| cost_guard.py | Cost cap safety net — built ~2026-05-15. Rule No.1 brake. Wiring status UNCONFIRMED. |
| meta_loop.py + meta_loop.bat | Self-improving meta-loop. Dry-run default. 3 proposals in meta_proposals/ (never actioned). |
| queue_runner.py + queue_runner.bat | Batch goal runner — reads goal_queue.txt, runs loop --once per goal. ACTIVE. |
| morning_report.md | Auto-copy of latest AAFL result. Updated each AAFL run. |
| mcc_full_mot.py | 108-check MOT test suite. MOT result: 108/108 ALL CLEAR 2026-05-23. |
| provider_health.py | Provider health system — 3 tiers, 29 tests. |
| source_library_manager.py | Sources library management — reads/writes sources_library.json. |
| preset_manager.py | Build 1 Feature 2 — standalone preset utility (save/load/list/delete). ACTIVE. |
| docs/MCC_FULL_GUIDE.md | Plain-English MCC user guide. Created 2026-05-24. |
| afna_strategies.json | AFNA (Attack From New Angle) strategy definitions. |
| Auto-refresh polling (MCC) | 30s pollCoreData(), manual ↻ Refresh button, Last updated label. Added 2026-05-24. |
| AAFL Live Output panel | Live streaming AAFL output in AAFL Control tab. Phase + provider badges. Added 2026-05-24. |
| AAFL↔Scout Bridge | Trigger scout for current goal, result feeds back to MCC. Added 2026-05-24. |
| Workflow Builder | Provider sequence builder (add/remove steps), save/load named presets. Added 2026-05-24. |
| Scout Strategies section | 5 individual strategy buttons (DDG/Reddit/GitHub/YouTube/Forum) + All Parallel. Added 2026-05-24. |
| /aafl/run-goal endpoint | Fixes "Failed to fetch" — now actually launches loop_manager.py. Added 2026-05-24. |
| /scout/strategy endpoint | Individual scout strategy launcher. Added 2026-05-24. |
| docs/PROJECT_AUDIT.md | Created 2026-05-24. Lists 22 missing items. |
| ACCA.md cleanup | 5 codes added (CLACH/CNP/RIBS/SESUM/SBS), 5 mode codes reformatted, CAP duplicate confirmed clean. |
| FFUE correction | FFUE corrected to Fluid Flexible Upgradeable Editable. |
| aafl_wccs.py attempt | All providers failed, manual session log cc2 committed. |
| Coder 32B loaded | Ready for retry. |
| STATUS.md restore | Completed 2026-05-27 — 168/195 lines (86%) restored from chat history |
| aafl_wccs.py read-merge-write | Completed 2026-05-27 — merged 3 session logs into aafl_wccs.py |
| 90% sanity check | Completed 2026-05-27 — mcc_server.py verified stable |
| Line count warning | Added to WCCS tab — highlights when STATUS.md exceeds 250 lines |
| Old saves scanner | Added to WCCS tab — scans session_logs/ for old saves |
| chat→SESUM | Added to WCCS tab — converts chat history to SESUM format |
| Missions tab | Added to MCC — shows current mission priorities |
| UI shuffle | Completed 2026-05-27 — removed ALP/Memory tabs from top bar |
| Tooltips | Added to all MCC buttons — shows keyboard shortcuts |
| IBR scan | Added to WCCS tab — scans for Investigate Brainstorm Reports |
| Red banner fix | Replaced with blue pulse glow + bouncing arrow (Block D) |
| SESUM saved | Saved to session_logs/sesum_2026-05-27.md |
| Build 4 (MCC) | Quick Ask, AAFL Results, Scout Search, Loop Presets, Chain Builder — 108/108 MOT |
| Build 4b (Health Suite) | Sidebar nav tree, sticky scroll fix, duplicate ID removal — 109/109 MOT |
| Build 5a (Unified Query) | Unified query bar (AAFL + Scout tabs), quick-ask endpoint fix, hsTabSwitch fix |
| OCB-A (MCC Self-Health) | work_checker.py, self_health.py, data/health.db, data/element_registry.json, data/solution_database.json |
| OCB-B (Body Map + Auto-Fix) | auto_fixer.py, Body Map SVG in MCC, real-time Health Suite polling |
| OCB-C Phase 1 (Missions) | 8-card mission launcher, KB Profiles merged into Missions, launch-spindoctor API |
| OCB-C Phase 2 (Workflow) | Workflow Builder + Chain Mode + B2-07 merged into single accordion with SVG flowchart |
| OCB-C Phase 3 (Storage) | 8 visual elements + 3 API endpoints — pie chart, bar graphs, dial, trend, forecast, sliders |
| OCB-C Phase 4 (System Monitor) | system_monitor.py, 4-dial hs-pane-system, AI process cards, timeline SVG, 6 API endpoints |
| STORM (deduplication) | deduplicate_status/sesums/history methods in storage_manager.py — ACCA: STORM |
| OCB-D Phase 1 (LLOW Engine) | llow_engine.py, data/llow_elements.json (35 elements), data/llow_arrows.json (15 types) |
| OCB-D Phase 2 (LLOW Canvas UI) | 3-panel drag-drop canvas in AAFL Control tab — palette, canvas, properties, exec log |
| OCB-D Phase 3 (LLOW Endpoints) | 10 /api/llow/* endpoints in mcc_server.py + run_llow_workflow() in loop_manager.py |
| OCB-D Phase 4 (Starter Workflows) | basic_research, full_dev_cycle, overnight_aafl in data/llow_workflows/ |
| OCB-E Phase 1 (LLOW Population) | 38 elements (added DRR, DWR, WENTO, moved CNP) — retry logic fixed |
| OCB-E Phase 3 (Popup z-index) | .mcc-popup-safe CSS class + z-index:9999 global fix |
| OCB-E Phase 4 (Visual Overhaul) | Ticker bar, AI provider cards, leaderboard, cost savings counter in Health Suite |
| OCB-E Phase 5 (Storage Visuals) | Treemap, archive timeline heatmap, cleanup suggestions, 4 new API endpoints |
| OCB-E Phase 6 (SESUM+ACCA) | sesum_2026-05-28_combined.md saved. ACCA: WRC, LLOW, STORM, AASKC added |
| OCB-F Phase 1 (Arrow Drop Fix) | `llowOnDrop` now handles type=arrow; sets `pendingArrowType` for next port connection. Badge in topbar shows active type. All 15 arrow types draggable. |
| OCB-F Phase 2 (Colour Strategy) | ⚙️ Settings slide-in panel. Phase Flow / Element Mirror / Snap Glow — three independent toggles. Starter workflow auto-suggest hints. 108/108 MOT. |
| OCB-G Phase 1 (CONNECTORS) | Palette section renamed "Arrow Types" → "CONNECTORS". Per-type line styles for all 15: dotted timer/scheduled, dashed jump/branch/alp/hard_stop, solid+width for trigger/repeat/ab_split. |
| OCB-G Phase 2 (Junction Boxes) | 8 new junction types in junctions category (llow_elements.json): Decision/Merge/Split/Gate/Counter/Logger/Router/Delay. CSS clip-path shapes per type. Double-click popup for Gate/Counter/Router/Delay editable params. Props panel "Edit Options" button. |
| OCB-G Phase 3 (Preset Load) | Dropdown renamed "Preset Load…". 8 new workflow presets: Tutorial Load, Bug Hunt, ALP Audit Run, Scout Deep Dive, Morning Report, Meta Improve, New Project Bootstrap, Star Citizen Benchmark. Strategy auto-suggest extended to all 11 presets. |
| OCB-G Phase 4 (Colour Strategy) | Phase Flow now renders visible zone header labels at canvas top: "INPUT", "PROCESS", "OUTPUT" with full subtitles. Strict Mode 4th toggle: wrong-zone drop = canvas shake + red zone flash + snap-back + log message. Requires Phase Flow ON. |
| OCB-H Phase 1 (Snap Mode) | "Strict Mode" renamed to "Snap Mode" everywhere in code, CSS, JS, and UI label. Ghost bug fixed: only grabbed LEL ghosts/moves, all others stay solid. Custom drag image for palette elements. 108/108 MOT. |
| OCB-H Phase 2 (Tab Renames) | "Scout" → "Scout Swarm" in tab bar. KB Profiles tab button hidden from main tab bar — already lives in Missions tab as sub-section. |
| OCB-H Phase 3 (AI Status Bar) | Persistent bar across top of all MCC tabs. Shows all AI providers with live pulse dots, latency, score. Scrolling ticker. Updates on every provider health refresh. |
| OCB-H Phase 4 (Health Suite) | Timeline: 60-reading cap removed — full session history with grid lines + elapsed time label. AI Process Table: per-process CPU/RAM bars + detailed table with Kill buttons. Leaderboard: animated score bars + crown/medal icons. |
| OCB-H Phase 5 (Storage) | Pie chart: 160px, animated segments, darker=more used, centre shows % used. Legend shows per-slot % with colour coding. |
| OCB-H Phase 6 (Animations) | Scout card hover, memory card hover, cost savings counter pulse glow, cardSlideIn/fadeInUp/countUp CSS keyframes added. |
| OCB-H Phase 7 (Instructions) | Full reorganisation into 9 areas: General MCC, WCCS/Saving, Scout Swarm, LLOW Canvas, Health Suite, Storage/Missions/Design/Promo, AAFL Engine, Data Flow, ACCA Codes by category. Documents all OCB-A through OCB-H features. |
| OCB-H Phase 8 (Design Tab) | Animation speed slider, Layout density (comfortable/compact/spacious), Tab bar style (default/pills/minimal), Sidebar accent colour, Tab bar accent colour picker. |
| OCB-H Phase 9 (Promo Tab) | Project story + description, stat counters (14 providers/108 MOT/9.33 score), competitive comparison table (AAFL vs LangGraph/CrewAI/AutoGPT), links section (Ko-fi/Itch.io/GitHub/r/LocalLLaMA). |
| OCB-H Phase 10 (Missions) | Progress overview panel: 6 animated progress bars per mission, AAFL score trend SVG chart, milestone markers (done/pending/planned). |
| OCB-H Phase 11 (MOT) | 108/108 ALL CLEAR 2026-05-28 |
| OCB-I Phase 1 (LEL Options) | Every LEL has 3-4 configurable options. Palette click → options panel below. Canvas double-click → popup. GOEB tooltips on all options. |
| OCB-I Phase 2 (Junction Boxes) | All 8 JB types fully rebuilt with 4 options each: Decision/Merge/Split/Gate/Counter/Logger/Router/Delay. Full double-click popup for all. |
| OCB-I Phase 3 (AI Master Control) | Collapsible panel above LLOW canvas: per-phase AI dropdowns, parallel workers slider, cost cap, temperature, Smart Auto-Assign, fallback chain drag-reorder, provider toggles. |
| OCB-I Phase 4 (Snap Mode Fix) | Snap Mode now works with BOTH Phase Flow AND Element Mirror. Element Mirror: each LEL snaps to its own colour zone. Phase Flow: 3-zone INPUT/PROCESS/OUTPUT enforcement. |
| OCB-I Phase 5 (Zone Labels) | All 3 zones (INPUT/PROCESS/OUTPUT) have visible headers with subtitle text, GOEB tooltip, colour-coded borders. |
| OCB-I Phase 6 (LLOW Fullscreen) | ↗ button in LLOW toolbar expands canvas to fill viewport. Escape or ↙ exits. Works in fullscreen for all LLOW functions. |
| OCB-I Phase 7 (Scrollbar Width) | All LLOW scrollbars widened to 10px: palette, canvas, props panel, settings, exec log. |
| OCB-I Phase 8 (Loop Behaviour → LLOW) | Loop Behaviour absorbed into LLOW section as collapsible accordion. All 8 loop action LELs present. Loop presets saved to localStorage. |
| OCB-I Phase 9 (Section Reorganiser) | All aafl-acc sections get ⠿ drag handle + ▲ minimise button. Drag-to-reorder within tab. Order saved to localStorage per tab. |
| OCB-I Phase 10 (MOT) | 108/108 ALL CLEAR 2026-05-28 |
| mcc-instructions-keeper | data/instructions_db.json (132 entries) + /api/instructions endpoints + 7 ? help buttons in MCC headers + showInstructions() JS. Skill file uploaded to Project Files 2026-05-28. |
| OCB-K Finish | data/project_awareness.json + CLAUDE.md (project orientation) — both created 2026-05-28. |
| OCB-L Phase 1 (OCB-K finish) | data/project_awareness.json built, CLAUDE.md written, data/help_history.json + data/mcc_settings.json created. |
| OCB-L Phase 2 (System Monitor fix) | _refreshSystemMonitor() dual-source (system/snapshot + resources/snapshot). GPU shows grey N/A when unavailable. LM Studio status pill added. RAM AMBER >80%, RED only >95%. |
| OCB-L Phase 3 (AI Status Bar) | /api/provider-health endpoint with location/model_loaded/VRAM. Bar height 44px. Richer provider cards with GPU/CPU/CLOUD/PAID badges. Click = expandable tooltip. Auto-refresh 20s. |
| OCB-L Phase 4 (System Drill-Downs) | All 5 dials clickable. CPU/RAM/Disk/GPU/LMStudio expand panels below dials. 5 new /api/resources/* endpoints. |
| OCB-L Phase 5 (Help Tab) | 🔍 Help tab added. /api/help/ask (SSE streaming). /api/help/history. AI hierarchy selector. Q&A history accordion. ask() routing via aafl_core provider chain. |
| OCB-L Phase 6 (Settings Persistence) | data/mcc_settings.json. GET/POST /api/settings. Design tab saves to disk. section_order_per_tab to disk. mccLoadSettings() on DOMContentLoaded. Restore Defaults button. 9 localStorage calls replaced with API. |
| OCB-L Phase 7 (MOT) | 108/108 ALL CLEAR 2026-05-28 |
| OCB-N Phase 1 (Scout Swarm LEL) | DATA SOURCES category + SCOUT_SWARM LEL in llow_elements.json. Time limit/counter/status/params on canvas node. /api/llow/scout-swarm endpoints. |
| OCB-N Phase 2 (Project Timeline) | project_timeline_builder.py — scans git/session_logs/STATUS/HISTORY/ACCA. Saves data/project_timeline.json. Wired into aafl_wccs.py on every save. /api/timeline-data endpoint. |
| OCB-N Phase 3 (Work Checker upgrade) | 3 new panels: TIMELINE (horizontal OCB track), CHECKLIST (STATUS.md PENDING as live checkboxes), ACTION PLAN (top 5 priorities + Delegate buttons). 5 new endpoints. |
| OCB-N Phase 4 (ACCA Ticker) | Persistent bottom bar scrolling all ACCA codes. Click-to-expand. Auto-loads on connect. Colour coded. Auto-reload every 5min. |
| OCB-N Phase 5 (Remove handover writes) | wccs_runner.py no longer creates VKB_SpinDoctor_Handover_vXX.md files. STATUS/HISTORY/ACCA are source of truth. |
| OCB-N Phase 6 (MOT) | 108/108 ALL CLEAR 2026-05-29 |

## CURRENT STATUS — PENDING
| Component | Notes |
|---|---|
| Star Citizen full support | Next benchmark — first public AAFL proof |
| Throttle slider in WT | Likely PS5/Xbox conflict — unplug and retry |
| 5-project split | AAFL Engine / Spin Doctor / Mission Control / Promo / ACCA — after Star Citizen benchmark |
| Add GROQ_API_KEY to .env | console.groq.com → API Keys |
| Add Cloudflare keys to .env | CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID |
| **Build 2 — Parking Lot (23 features)** | CLAC block pending — next session |
| B2-01: Kanban task dependencies + sub-tasks | Kanban tab |
| B2-02: Kanban templates + bulk actions + auto-archive | Kanban tab |
| B2-03: Activity Feed — all 12 filters + AI summarise + export | Activity tab |
| B2-04: AAFL Runs — compare mode + failure analysis + success patterns | AAFL Runs tab |
| B2-05: AAFL Runs — tag/notes on runs | AAFL Runs tab |
| B2-06: AAFL Control — step-by-step + pause mode | AAFL Control tab |
| B2-07: AAFL Control — chain builder + notification settings | MERGED into OCB-C Workflow Builder |
| B2-08: AAFL Control — benchmark runner | AAFL Control tab |
| B2-09: AAFL Control — second opinion AI | AAFL Control tab |
| B2-10: Costs — budget caps + savings tracker + ROI tracker | Costs tab |
| B2-11: Costs — trend graphs + currency toggle | Costs tab |
| B2-12: Scout Control — multi-browser sources | Scout tab |
| B2-13: Scout Control — AI comparison mode | Scout tab |
| B2-14: Scout Control — per-strategy AI override | Scout tab |
| B2-15: Scout Control — parallel workers slider | Scout tab |
| B2-16: Scout Control — source health monitor + blocked sources | Scout tab |
| B2-17: Scout Control — export briefing | Scout tab |
| B2-18: WCCS Save tab — diff viewer + timeline + rewind | WCCS tab |
| B2-19: Global — dark/light theme toggle | Global |
| B2-20: Global — tutorial mode | Global |
| B2-21: Global — keyboard shortcuts (full set) | Global |
| B2-22: Keybinding Profile Library v0.5 | Global |
| B2-23: Electron wrapper | Packaging |
| GitHub MCP connector | Connect repo to Chat, read code without CLAC burn. Discussed 24 May. Manual setup. |
| Deep Research tool | Replace scout hours for keybind/competitor research. Free. Discussed 24 May. |
| aafl_watchdog.py + cost_guard.py wiring | URGENT — confirm both are called from loop_manager.py before next overnight run |
| meta_proposals review | 3 AAFL self-improvement proposals in meta_proposals/ from 2026-05-18. None implemented. High value — read next. |
| loop_output file cap | 35+ files now. Cleanup cap (50 max) planned 2026-05-20, never built. |
| AFNA strategies → Stuck Inbox | Wire afna_strategies.json into Stuck Inbox AFNA suggestions. Planned 2026-05-23. |
| Stage 3 WCCS (Chrome extension) | Auto-capture chat without manual trigger. Long-term. |
| Ko-fi + Itch.io links | Fastest monetisation path. 30 min. In README. |
| xAI Grok signup | console.x.ai → add GROQ_API_KEY to .env manually |
| n8n investigation | n8n self-hosted as potential AAFL foundation. Flagged May 2026. Never investigated. |
| Dead file archive | model_router.py, setup_router.py, quick_fix.py, control_panel.py, aafl_loop.py, full_auto_setup.py, free_providers.py, v40/v41/v43 handovers → archive_dead/ 2026-05-24 |

---

## BIG VISION
AAFL IS THE PROJECT NOW. Spin Doctor is the first proof. AAFL competes with LangGraph, CrewAI, AutoGPT. Story angle: beginner with BI builds self-improving AI agent. Target: r/LocalLLaMA when Star Citizen v0.2 benchmark passes.

**AASKC** (Autonomous AI Simultaneous Knowledge Connection) = the PRODUCT NAME for the full platform: AAFL engine + Mission Control Center + LLOW visual canvas + Scout web researcher + STORM dedup. One product. One brand. Beginner built.

Spin Doctor = universal input device assistant. Any hardware, any game. Core fix: Steam Generic Gamepad Config silently breaks joysticks for millions. One unchecked box = fixed.

MCC = cross-cutting cockpit across all 6 projects.

---

## PROVIDER STATUS
| Provider | Model | Tier | Status |
|---|---|---|---|
| LM Studio x4 | Coder32B/VL32B/DeepSeekR1/Phi4 | 1 local | When LM Studio running |
| Cerebras | cerebras/gpt-oss-120b | 2 free | Fixed (was llama-3.3-70b deprecated) |
| Mistral Codestral | mistral/codestral-latest | 2 free | Working |
| Gemini 2.5 Flash | gemini/gemini-2.5-flash | 2 free | Working, occasional 503s |
| OpenRouter Auto | openrouter/openrouter/auto | 3 fallback | Working, 23-34s |
| Groq x2 | llama-3.3-70b + deepseek-r1 | 2 free | Needs GROQ_API_KEY |
| Cloudflare | llama-3.1-8b-instruct | 2 free | Needs both Cloudflare keys |
| Claude Sonnet | claude-sonnet-4-6 | 99 paid | Blocked unless allow_paid=True |
Still to sign up (8): xAI Grok, NVIDIA NIM, SambaNova, GitHub Models, Ollama, Together AI, Fireworks, DeepSeek

---

## NEXT PRIORITIES
1. Run MOT 108/108 after OCB-N — confirm all checks PASS
2. Star Citizen v0.2 benchmark via AAFL autonomous run (proof of concept #2)
3. Add GROQ + Cloudflare keys to .env (manual — security rule)
4. Polish AASKC for ship — README, demo video, r/LocalLLaMA post
5. Build 2 CLAC block (23 parking lot features — B2-07 now done via OCB-C)
6. Post on r/LocalLLaMA when Star Citizen benchmark passes
7. LiteLLM full integration — replace direct provider calls with LiteLLM router
8. Electron wrapper for packaging

<!-- END_OF_FILE -->