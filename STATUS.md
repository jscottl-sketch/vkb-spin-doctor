# STATUS — VKB Spin Doctor
**Last updated:** 2026-05-25 | **Updated by:** aafl_wccs.py
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
| mcu_optimizer.py | Free-LLM Kanban optimiser. WCCS step 6. |
| dashboard_builder.py | MCC data builder. Atomic write. --dry-run flag. |
| task_router.py | Classifies AAFL/CLAC/SONNET/OPUS. 88 lines. |
| problems/conductor.py | 619 lines, 22 problems |
| problems/win_hardener.py | 9 problems W-001-W-009 |
| problems/ed_bind_reset.py | ED Bind Reset prevention |
| mission_control.html | MCC — 21 tabs, Build 2 complete, 108/108 MOT ALL CLEAR |
| mcc_server.py | Bridges MCC HTML to filesystem. 55+ endpoints. B2 routes added. |
| data/devices.json | 98 devices with VID/PID lookup |
| AAFL autonomous runs | 4 goals, scores 8.07-9.33, DB cache hit confirmed |
| Regression test | PASS 8.83/10 |
| ALP_Database.md | 17 entries |
| Handover split | INDEX/STATUS/HISTORY/ACCA applied 2026-05-20 |
| aafl_wccs.py | Built 2026-05-20. Permanent WCCS fix (free Mistral). |
| merge_sessions.py + .bat | Built 2026-05-23. DSP required |
| MCC MOT 108/108 | ALL CLEAR 2026-05-25 (Build 2) |
| mss library | Installed 2026-05-23 (fixes sfl_agent pre-existing error) |
| Build 1 (10 features) | 13/13 modules, 12/12 tests PASS. Complete 2026-05-23 |
| Build 2 (23 features) | ALL 23 complete 2026-05-25. MOT 108/108 ALL CLEAR. |
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
| mcu_optimizer.py | Reads handover + session logs + board, sends to Mistral, rewrites kanban JSON. WCCS step 6. |
| wccs_runner.py | Original WCCS runner (pre-aafl_wccs). Still present. |
| aafl_watchdog.py | Safety watchdog — built 2026-05-20. Wiring UNCONFIRMED — verify before overnight run. |
| cost_guard.py | Cost cap safety net — built ~2026-05-15. Wiring UNCONFIRMED. |
| meta_loop.py + meta_loop.bat | Self-improving meta-loop. Dry-run default. 3 proposals in meta_proposals/ (never actioned). |
| queue_runner.py + queue_runner.bat | Batch goal runner — reads goal_queue.txt, runs loop --once per goal. ACTIVE. |
| morning_report.md | Auto-copy of latest AAFL result. Updated each AAFL run. |
| mcc_full_mot.py | 108-check MOT test suite. MOT result: 108/108 ALL CLEAR 2026-05-25. |
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
| B2-01: Kanban dependencies + sub-tasks | Built 2026-05-25. kanban_board.json. /b2/kanban endpoints. |
| B2-02: Kanban templates + bulk + auto-archive | Built 2026-05-25. Templates: bug/feature/research. |
| B2-03: Activity Feed (12 filters + AI + export) | Built 2026-05-25. autolog tab. activity_log.json. /b2/activity endpoints. |
| B2-04: AAFL Runs compare + failure + success | Built 2026-05-25. Compare mode, failure groups, success patterns. |
| B2-05: AAFL Runs tag/notes | Built 2026-05-25. /b2/run-tag + /b2/run-notes. SQLite columns added. |
| B2-06: AAFL Control step-by-step + pause | Built 2026-05-25. Phase dots, pause flag, /b2/step-* endpoints. |
| B2-07: AAFL Control chain builder + notifications | Built 2026-05-25. /b2/chain-save + /b2/chain-run. Browser Notifications API. |
| B2-08: AAFL Control benchmark runner | Built 2026-05-25. /b2/benchmark. benchmark_results.json. |
| B2-09: AAFL Control second opinion AI | Built 2026-05-25. /b2/second-opinion. aafl_output/second_opinion.txt. |
| B2-10: Costs budget caps + savings + ROI | Built 2026-05-25. budget_caps.json. /b2/budget-caps. |
| B2-11: Costs trend graphs + currency toggle | Built 2026-05-25. SVG line + bar charts. /b2/costs. GBP/USD/EUR. |
| B2-12: Scout multi-browser sources | Built 2026-05-25. Multi-source columns in Scout tab. |
| B2-13: Scout AI comparison mode | Built 2026-05-25. /b2/scout-compare. Side-by-side results. |
| B2-14: Scout per-strategy AI override | Built 2026-05-25. /b2/strategy-overrides. scout_config.json. |
| B2-15: Scout parallel workers slider | Built 2026-05-25. /b2/workers. 1-10 range. |
| B2-16: Scout source health + blocked sources | Built 2026-05-25. /b2/source-health, /b2/block-source, /b2/unblock-source. b2_blocked_sources.json. |
| B2-17: Scout export briefing | Built 2026-05-25. /b2/export-briefing. scout_briefings/ folder. |
| B2-18: WCCS timeline + diff + rewind | Built 2026-05-25. Timeline dots, click-to-preview in WCCS tab. |
| B2-19: Global dark/light theme toggle | Built 2026-05-25. body.theme-light CSS. /b2/prefs saves preference. |
| B2-20: Global tutorial mode | Built 2026-05-25. body.tutorial-on. Tooltip overlays on first run. |
| B2-21: Global keyboard shortcuts + command palette | Built 2026-05-25. Ctrl+1-9, Ctrl+K palette, full shortcut overlay. |
| B2-22: Keybinding Profile Library v0.5 | Built 2026-05-25. keybind_profiles/ folder. /b2/keybind-profiles CRUD. Star rating. |
| B2-23: Electron wrapper | Built 2026-05-25. electron/main.js + preload.js + package.json. Auto-starts mcc_server.py. |
| SIF delivered | 2026-05-25. 68-test smoke test designed. |
| Knowledge Bank | Built 2026-05-25. Knowledge Harvester + Auto-Capture Hook. AAFL Plan phase queries knowledge bank. Knowledge tab in MCC. |
| WCBB fixes | 17 fixes designed 2026-05-25. |
| Dead file archive | model_router.py, setup_router.py, quick_fix.py, control_panel.py, aafl_loop.py, full_auto_setup.py, free_providers.py, v40/v41/v43 handovers → archive_dead/ 2026-05-24 |
| LiteLLM full integration | Replaced direct provider calls with LiteLLM router 2026-05-25. |
| aafl_watchdog.py + cost_guard.py wiring | Confirmed wired into loop_manager.py 2026-05-25. |
| AFNA strategies → Stuck Inbox | Wired afna_strategies.json into Stuck Inbox AFNA suggestions 2026-05-25. |
| loop_output file cap | Implemented 50-file cap 2026-05-25. |

## CURRENT STATUS — PENDING
| Component | Notes |
|---|---|
| Star Citizen full support | Next benchmark — first public AAFL proof |
| Throttle slider in WT | Likely PS5/Xbox conflict — unplug and retry |
| 5-project split | AAFL Engine, VKB Spin Doctor, Mission Control, Promo, ACCA Database + Master |
| Add GROQ_API_KEY to .env | console.groq.com → API Keys |
| Add Cloudflare keys to .env | CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID |
| GitHub MCP connector | Connect repo to Chat, read code without CLAC burn. Discussed 24 May. Manual setup. |
| Deep Research tool | Replace scout hours for keybind/competitor research. Free. Discussed 24 May. |
| meta_proposals review | 3 AAFL self-improvement proposals in meta_proposals/ from 2026-05-18. None implemented. High value — read next. |
| Stage 3 WCCS (Chrome extension) | Auto-capture chat without manual trigger. Long-term. |
| Ko-fi + Itch.io links | Fastest monetisation path. 30 min. In README. |
| 5-project split | AAFL Engine / Spin Doctor / Mission Control / Promo / ACCA — after Star Citizen benchmark |
| xAI Grok signup | console.x.ai → add GROQ_API_KEY to .env manually |
| n8n investigation | n8n self-hosted as potential AAFL foundation. Flagged May 2026. Never investigated. |
| B2-23 Electron install | Run `npm install` in electron/ then `npm start` to test wrapper |

---

## BIG V

<!-- END_OF_FILE -->
