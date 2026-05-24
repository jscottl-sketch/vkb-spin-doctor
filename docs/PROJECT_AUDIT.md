# PROJECT AUDIT — VKB Spin Doctor / AAFL Platform
**Date:** 2026-05-24 | **Audited by:** Claude Code full read

---

## 1. FILE AUDIT — ROOT + SUBFOLDERS

### KEY: ACTIVE = in use / DEAD = superseded / UNKNOWN = unclear

#### Core Python (Runtime)
| File | Status | Notes |
|---|---|---|
| spin_doctor.py | ACTIVE | Main GUI, 1057+ lines, 3 tabs |
| sfl_agent.py | ACTIVE | Screenshot Feedback Loop agent v3 |
| aafl_core.py | ACTIVE | 15 providers, LiteLLM routing |
| loop_manager.py | ACTIVE | Plan-Work-Verify-Store, 471 lines |
| evaluator.py | ACTIVE | Result scorer 0-10 |
| researcher.py | ACTIVE | DDG search + 5 scout strategies |
| memory_bank.py | ACTIVE | SQLite knowledge/solution/reputation |
| meta_loop.py | ACTIVE | Self-improving meta-loop |
| chief_scout.py | ACTIVE | Parallel scout orchestrator |
| dashboard_builder.py | ACTIVE | MCC data builder |
| task_router.py | ACTIVE | Classifies AAFL/CLAC/SONNET/OPUS |
| mcc_server.py | ACTIVE | MCC HTTP server, 30+ endpoints |
| mcc_full_mot.py | ACTIVE | 108-check MOT test suite |
| mcc_test.py | ACTIVE | 138-test automated test suite |
| aafl_wccs.py | ACTIVE | Free Mistral WCCS automation |
| merge_sessions.py | ACTIVE | Weekly session log merger |
| wccs_runner.py | ACTIVE | WCCS runner (older, pre-aafl_wccs) |
| mcu_optimizer.py | ACTIVE | Kanban board optimizer via Mistral |
| aafl_watchdog.py | ACTIVE | Safety watchdog (URGENT: confirm wired) |
| cost_guard.py | ACTIVE | Cost cap safety net (URGENT: confirm wired) |
| chain_runner.py | ACTIVE | Sequential goal chain mode |
| scout_timer.py | ACTIVE | Timed scout runs |
| retry_manager.py | ACTIVE | Auto-retry with log |
| smart_suggester.py | ACTIVE | Goal/provider suggestion |
| stuck_inbox.py | ACTIVE | Stuck goal management |
| cost_predictor.py | ACTIVE | Cost estimation |
| promo_queue.py | ACTIVE | Promotion review queue |
| storage_manager.py | ACTIVE | Storage monitoring |
| module_loader.py | ACTIVE | Plugin/module system |
| provider_health.py | ACTIVE | Provider health checks |
| source_library_manager.py | ACTIVE | Sources library management |
| archive_logs.py | ACTIVE | Moves old session logs to archive/ |
| health_check.py | ACTIVE | Pings all providers |
| aafl_config_reader.py | ACTIVE | Reads aafl_config.json |
| queue_runner.py | ACTIVE | Runs goal queue batch |
| preset_manager.py | UNKNOWN | May be superseded by mcc_server.py preset handlers |
| model_router.py | DEAD | Historical AAFL prototype — archive to archive_dead/ |
| setup_router.py | DEAD | One-time admin setup — archive to archive_dead/ |
| quick_fix.py | DEAD | Old patch script — archive to archive_dead/ |
| control_panel.py | DEAD | Early prototype — archive to archive_dead/ |
| aafl_loop.py | DEAD | Superseded by loop_manager.py |
| full_auto_setup.py | UNKNOWN | Mystery file — historical zero-prompt setup |
| free_providers.py | UNKNOWN | May be superseded by aafl_core.py routing |
| HOW_TO_INTEGRATE_DIAGNOSTIC.py | UNKNOWN | Old diagnostic tool from early days |
| test_full_system.py | ACTIVE | Full system test (85/85 Phase 1) |
| test_homescreen.py | ACTIVE | Home screen test |
| test_tier1.py | ACTIVE | Tier 1 provider tests |
| test_tier2.py | ACTIVE | Tier 2 provider tests |
| test_tier3.py | ACTIVE | Tier 3 provider tests |

#### Core Python (Problems module)
| File | Status | Notes |
|---|---|---|
| problems/conductor.py | ACTIVE | 619 lines, 22 problems |
| problems/win_hardener.py | ACTIVE | 9 Windows hardware problems |
| problems/ed_bind_reset.py | ACTIVE | ED Bind Reset prevention |
| problems/__init__.py | ACTIVE | Module init |

#### HTML / Web
| File | Status | Notes |
|---|---|---|
| mission_control.html | ACTIVE | MCC dashboard, 19+ tabs |

#### Docs / Reference
| File | Status | Notes |
|---|---|---|
| INDEX.md | ACTIVE | Project resume guide |
| STATUS.md | ACTIVE | Current state (rewritten each session) |
| HISTORY.md | ACTIVE | Append-only session log |
| ACCA.md | ACTIVE | Append-only code archive |
| DESIGN_RULES.md | ACTIVE | FFUE + dual-mode rules |
| ALP_Database.md | ACTIVE | 17 ALP rules |
| docs/MCC_FULL_GUIDE.md | ACTIVE | MCC user guide (plain English) |
| Universal_Input_Device_Database.md | ACTIVE | 98 devices reference |
| Knowledge_Engine_Schema_v1.md | ACTIVE | DB schema reference |
| morning_report.md | ACTIVE | Latest AAFL loop output copy |
| VKB_SpinDoctor_Handover_v40.md | DEAD | Old handover — should move to archive_dead/ |
| VKB_SpinDoctor_Handover_v41.md | DEAD | Old handover — should move to archive_dead/ |
| VKB_SpinDoctor_Handover_v43.md | DEAD | Old handover — already in archive_dead/ (duplicate) |
| pending_wccs_notes.txt | ACTIVE | Pending design rule note (design rule is now in DESIGN_RULES.md — can be cleared) |
| project_inventory.txt | ACTIVE | Last file inventory snapshot (now stale) |

#### Batch / Launch
| File | Status | Notes |
|---|---|---|
| RUN_VKB.bat | ACTIVE | Launches spin_doctor.py |
| run_aafl.bat | ACTIVE | Full AAFL launch (LM Studio + queue) |
| queue_runner.bat | ACTIVE | Runs goal queue |
| meta_loop.bat | ACTIVE | Meta-loop launcher |
| merge_sessions.bat | ACTIVE | Weekly session merge |
| START_MCC.bat | ACTIVE | Starts MCC server |
| SAVE_NOW.bat | ACTIVE | One-click bulletproof save |
| END_SESSION.bat | ACTIVE | End-of-session save |
| GIT_BACKUP.bat | ACTIVE | Git backup |
| GIT_INIT.bat | ACTIVE | Git init |
| GOODNIGHT.bat | ACTIVE | Overnight session close |
| RUN_OVERNIGHT.bat | ACTIVE | Overnight run launcher |
| regression_test.bat | ACTIVE | Regression test runner |
| set_goal.bat | ACTIVE | Sets goal.txt |
| aafl_doctor.bat | ACTIVE | Pre-flight health check |
| START_LMSTUDIO.bat | ACTIVE | Starts LM Studio |
| STOP_LMSTUDIO.bat | ACTIVE | Stops LM Studio |
| UPDATE_WCCS_SKILL.bat | ACTIVE | Updates WCCS skill |

#### Config / Data / Output
| File | Status | Notes |
|---|---|---|
| aafl_config.json | ACTIVE | Confidence threshold + cost cap |
| aafl_control_config.json | ACTIVE | 14 providers + loop settings for MCC |
| chief_scout_config.json | ACTIVE | Scout presets |
| afna_strategies.json | ACTIVE | AFNA attack strategies |
| goal.txt | ACTIVE | Current AAFL goal |
| goal_queue.txt | ACTIVE | Queued goals for batch runs |
| sources_library.json | ACTIVE | Source discovery library |
| storage_config.json | ACTIVE | Storage monitoring config |
| stuck_inbox.json | ACTIVE | Stuck goals list |
| promo_queue.json | ACTIVE | Promotion candidates |
| task_db.json | UNKNOWN | Model router database (historical?) |
| modules/module_registry.json | ACTIVE | Module registry |
| presets/*.json | ACTIVE | 3 starter presets |
| data/knowledge_engine.db | ACTIVE | SQLite knowledge/solutions DB |
| data/devices.json | ACTIVE | 98 devices with VID/PID |
| data/dashboard_data.json | ACTIVE | Dashboard data |
| dashboard_data/*.json | ACTIVE | Per-tab dashboard JSON files |
| health_results/*.json | ACTIVE | Health check outputs |
| meta_proposals/*.md | ACTIVE | AAFL self-improvement proposals (3 — never actioned!) |
| loop_output/*.txt/*.md | ACTIVE | AAFL run outputs (35+ files, cleanup needed) |
| aafl_output/latest.txt | ACTIVE | Live AAFL stream |
| scout_output/latest.txt | ACTIVE | Latest scout result |
| .env | ACTIVE | API keys (manual only — security) |
| wccs_log.md | ACTIVE | WCCS save history |
| chat_latest.txt | ACTIVE | Current session chat |
| chat_latest_test.txt | DEAD | Test artifact from mcc_test.py |
| health_log.json | ACTIVE | Health check log |
| AAFL_Overnight_Task.xml | UNKNOWN | Old Task Scheduler XML? |
| machine_PRE_FIX_SAFETY.blk | ACTIVE | War Thunder safe backup |
| mcc_test_results.json | ACTIVE | Latest test results |
| test_run_1.json | ACTIVE | Test run comparison data |
| test_run_2.json | ACTIVE | Test run comparison data |
| meta_queue.txt | ACTIVE | Meta-loop goals (all marked # DONE) |
| session_logs/ | ACTIVE | Post-split session logs dir |
| sfl_logs/ | ACTIVE | SFL agent logs (historical) |
| .gitignore | ACTIVE | Git ignore rules |

---

## 2. STATUS.md COVERAGE GAPS

These active files/components exist but are NOT mentioned in STATUS.md BUILT table:

| Missing Item | Why it matters |
|---|---|
| mcu_optimizer.py | Step 6 of WCCS protocol — critical, used every session |
| wccs_runner.py | Original WCCS runner — still present, unclear if still active vs replaced by aafl_wccs.py |
| aafl_watchdog.py | Safety net — flagged URGENT in 2026-05-23 HISTORY |
| cost_guard.py | Rule No.1 safety net — flagged URGENT in 2026-05-23 HISTORY |
| meta_loop.py + meta_loop.bat | Self-improving loop — significant feature |
| mcc_full_mot.py | MOT test script (108 checks) — result mentioned but file not listed |
| docs/MCC_FULL_GUIDE.md | User guide — built 2026-05-24, not recorded |
| queue_runner.py + queue_runner.bat | Batch goal runner — confirmed ACTIVE in HISTORY |
| morning_report.md | Auto-output copy — confirmed ACTIVE in HISTORY |
| provider_health.py | Health check system — significant feature |
| source_library_manager.py | Sources library management — built in Build 1 |
| aafl_config_reader.py | Config reader utility |
| set_goal.bat | Useful launcher bat |
| regression_test.bat | Regression test launcher |
| aafl_doctor.bat | Pre-flight diagnostic bat |
| AAFL Live Output panel | Built 2026-05-24 this session — new MCC feature |
| AAFL↔Scout Bridge | Built 2026-05-24 this session — new MCC feature |
| Workflow Builder | Built 2026-05-24 this session — new MCC feature |
| Scout Strategies section | Built 2026-05-24 this session — new MCC feature |
| mcc_server.py endpoint count | STATUS says "10+ endpoints" — now 30+ |
| Auto-refresh polling | Added 2026-05-24 — 30s pollCoreData(), manual refresh button |
| afna_strategies.json | AFNA strategy config — active, used by chief_scout |

Also STATUS.md says mcc_server.py "10+ endpoints" — it's now well over 30.

---

## 3. ACCA.md COMPLETENESS CHECK

Full required list: DRR, DWR, YO, AIO, SIB, SIF, CR, WMBW, WCBB, NRM, BI, SFL, AAFL, ALP, CA, WS, WSF, WYM, WCCS, CLAC, CLACH, TBLM, DDM, BGM, BPM, EM, FFUE, DSP, PROF, CNP, SS, WENTO, CAWPA, SBS, RIBS, MCC, SESUM, AFNA

### Present in ACCA.md main table: ✓
DRR, DWR, YO, AIO, SIB, SIF, CR, WMBW, WCBB, NRM, BI, SFL, AAFL, ALP, CA, WS, WSF, WYM, WCCS, CLAC, DSP, AFNA, PROF, SS, WENTO, CAWPA, MCC

### Present but in non-table format (NEED MOVING INTO TABLE):
| Code | Where | Issue |
|---|---|---|
| TBLM, DDM, BGM, BPM, EM | Prose line at bottom of main table | Should be in proper table rows |
| FFUE | Stray separate table at very bottom | Should be integrated into main table |
| SBS | In HISTORY.md only (2026-05-20: "SBS = Step By Step") | **MISSING from ACCA.md entirely** |

### MISSING from ACCA.md — meaning unknown:
| Code | Status |
|---|---|
| CLACH | Not in ACCA.md or HISTORY.md — meaning unknown |
| CNP | Not in ACCA.md or HISTORY.md — meaning unknown |
| RIBS | Mentioned in HISTORY.md 2026-05-21 as "ALP Counter Tab RIBS idea" — never formally defined |
| SESUM | Not in ACCA.md or HISTORY.md — meaning unknown |

**ACTION REQUIRED:** Add SBS to ACCA.md. Clarify CLACH, CNP, RIBS, SESUM meanings.

---

## 4. DESIGN_RULES.md — FFUE CHECK

FFUE is defined as **"Fluid, Flexible, Upgradeable, Editable"** in DESIGN_RULES.md.

This is CORRECT. Matches ACCA.md entry and 2026-05-23 HISTORY.md.

The file also correctly documents:
- Dual-mode (Workstation + Packaged) rule
- All 4 components covered (Scout, AAFL, MCC, Spin Doctor)
- ALP First, append-only logs, atomic writes, LiteLLM routing, free-first, one step at a time

**NOTE:** pending_wccs_notes.txt contains: "Add: All components must support workstation mode AND packaged mode" — this is ALREADY in DESIGN_RULES.md. The pending_wccs_notes.txt can be cleared.

---

## 5. BUILT BUT NOT IN STATUS.md

These were built (confirmed in HISTORY.md/session logs) but not recorded in STATUS.md BUILT table:

| Built Item | Built Date | Notes |
|---|---|---|
| mcu_optimizer.py | 2026-05-18 | WCCS step 6 — critical |
| wccs_runner.py | 2026-05-18 | Original WCCS runner |
| meta_loop.py + meta_loop.bat | 2026-05-18 | Self-improving meta-loop |
| queue_runner.py + queue_runner.bat | 2026-05-17 | Batch goal runner |
| aafl_watchdog.py | 2026-05-20 | Safety watchdog |
| cost_guard.py | ~2026-05-15 | Cost cap safety net |
| morning_report.md | ~2026-05-17 | Auto-copy of latest AAFL result |
| mcc_full_mot.py | 2026-05-23 | 108-check MOT suite |
| provider_health.py | 2026-05-23 | Provider health system |
| source_library_manager.py | 2026-05-23 | Sources library manager |
| docs/MCC_FULL_GUIDE.md | 2026-05-24 | MCC user guide |
| Auto-refresh polling (MCC) | 2026-05-24 | 30s pollCoreData(), refresh button |
| AAFL Live Output panel | 2026-05-24 | Live streaming output in MCC |
| AAFL↔Scout Bridge | 2026-05-24 | Scout runs for AAFL goal |
| Workflow Builder | 2026-05-24 | Provider sequence builder + presets |
| Scout Strategies section | 2026-05-24 | 5 individual strategies + All Parallel |
| /aafl/run-goal endpoint | 2026-05-24 | Actually launches AAFL (was broken) |
| /scout/strategy endpoint | 2026-05-24 | Individual scout strategy launcher |
| afna_strategies.json | 2026-05-23 | AFNA strategy definitions |
| AAFL Overnight Task XML | UNKNOWN | Old Task Scheduler artifact |

---

## 6. UNACTIONED HISTORY.md IDEAS

Ideas discussed in HISTORY.md that were NEVER actioned (not in STATUS.md pending or action plan):

| Idea | Source Date | Status |
|---|---|---|
| n8n as AAFL foundation — investigate | 2026-05-16 | Never actioned |
| Ko-fi + Itch.io links in README | 2026-05-17 | Never actioned |
| Chrome extension auto-capture (Stage 3 WCCS) | 2026-05-19 | Future — not in action plan |
| Pin ACCA command (shows ACCA table in Chat right panel) | 2026-05-17 | Never actioned |
| loop_output file cleanup cap (50 files max) | 2026-05-20 | Never implemented — now 35+ files |
| meta_proposals/ review + implementation | 2026-05-23 | 3 proposals exist, none implemented |
| AFNA strategies wired into Stuck Inbox | 2026-05-23 | Planned in action item, unclear if done |
| aafl_watchdog.py + cost_guard.py wiring confirmation | 2026-05-23 | Urgent action item — never confirmed |
| SBS ACCA code | 2026-05-20 | Defined in HISTORY, missing from ACCA.md |
| Database-backed handover.db | 2026-05-20 | Was Job #1 then superseded by split architecture |
| RIBS = ALP Counter Tab idea | 2026-05-21 | Mentioned but never defined or built |
| MCC Option A vs B redesign | 2026-05-18 | Option B (single scroll) implied but never confirmed |
| GitHub MCP connector | 2026-05-24 | Now in STATUS.md PENDING — good |
| Deep Research tool | 2026-05-24 | Now in STATUS.md PENDING — good |
| 5-project split execution | 2026-05-19 | Still in PENDING — not yet done |
| xAI Grok signup | 2026-05-17 | Deferred repeatedly — still not done |
| Stage 3 Chrome auto-capture | 2026-05-19 | Future item, not tracked |

---

## 7. ADDITIONAL FINDINGS

### HISTORY.md noise (minor)
- 15+ duplicate "test session from mcc_test.py" entries at the end — these are test artifacts from mcc_test.py writing to HISTORY.md during test runs. Consider filtering mcc_test.py from writing to HISTORY.md, or adding a `[TEST]` prefix.

### Stale handover files in root (not archive_dead):
- VKB_SpinDoctor_Handover_v40.md, v41.md, v43.md — should move to archive_dead/

### project_inventory.txt is stale
- Last captured 2026-05-23, many new files since. This audit replaces it.

### mcc_server.py endpoint count stale in STATUS.md
- STATUS.md says "10+ endpoints" — actual count is 30+.

### pending_wccs_notes.txt can be cleared
- Its content (dual-mode rule) is already captured in DESIGN_RULES.md.

### meta_proposals/ — 3 proposals, none implemented:
- `2026-05-18_compare_langgraph_120_vs_current.md` — FLAGGED (LangGraph vs loop_manager comparison)
- `2026-05-18_identify_the_single_biggest_bottleneck.md` — FLAGGED
- `2026-05-18_score_each_provider_in_aafl_corepy.md` — FLAGGED
These are AAFL's own improvement ideas. The 2026-05-23 action plan said to read + implement high-value ones. Never done.

### aafl_watchdog.py + cost_guard.py wiring UNCONFIRMED
- Both files exist. Whether they are called from loop_manager.py is unverified. The 2026-05-23 HISTORY flagged this as URGENT before any overnight run.

---

## RECOMMENDATIONS (no action — report only)

1. **Add SBS to ACCA.md** (defined 2026-05-20, never appended)
2. **Move TBLM/DDM/BGM/BPM/EM from prose line into ACCA.md main table**
3. **Move FFUE from stray bottom entry into main table**
4. **Clarify CLACH, CNP, RIBS, SESUM** — meanings not found in any project file
5. **Update STATUS.md BUILT table** with 20+ missing items (see Section 5)
6. **Update STATUS.md mcc_server.py** — "10+ endpoints" → "30+ endpoints"
7. **Archive dead files** — v40/v41/v43 handovers + model_router.py + setup_router.py + quick_fix.py + control_panel.py → archive_dead/
8. **Confirm aafl_watchdog.py + cost_guard.py wiring** before next overnight run (URGENT)
9. **Read meta_proposals/** — AAFL's own improvement ideas, none implemented since May 18
10. **loop_output cleanup** — 35+ files, cap at 50 was planned but never implemented
11. **Clear pending_wccs_notes.txt** — its content is already in DESIGN_RULES.md

<!-- END_OF_FILE -->
