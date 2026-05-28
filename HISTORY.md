# HISTORY — VKB Spin Doctor
*Append-only chat log archive. Migrated from v45 on 2026-05-20. Never rewrite — only append.*

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

### 2026-05-18 (Claude Code session 5b)
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

### 2026-05-20

SESSION: 20 May 2026 — aafl_watchdog.py built, Star Citizen 8.33/10 autonomous, Scout Control mega-upgrade brainstormed, MCC tabs reorganization discussed, database-backed handover designed as permanent WCCS fix.

JOB #1 NEXT SESSION: Build database-backed handover (handover.db SQLite + migration from v45). CLAC block ready above. This fixes truncation permanently.

ACCA: SBS = Step By Step

NEXT: File cleanup caps (loop_output 50 max), provider keys (Gemini/Mistral dead), MCC Watchdog+Rewind tab, START_MCC.bat rename.


---

### 2026-05-21

Session 21 May 2026 - aafl_wccs fixed, merge_sessions built, MCC 7 save features built, JSON error fixed, ACCA tab planned, ASKC defined, ALP Counter Tab RIBS idea, Scout timed runs and 1TB storage planned


---

### 2026-05-23

Test session 23 May 2026 - provider reliability fix priority, MCC features reminded, merge_sessions auto-weekly planned


---

### 2026-05-23

Test session 23 May 2026 - provider reliability fix priority, MCC features reminded, merge_sessions auto-weekly planned


---

### 2026-05-23

SESSION: 23 May 2026 — PHASE 2 & MCC BUILD COMPLETE

WHAT GOT DONE TODAY:
- Provider Health Check system — 3 tiers, all 29/29 tests passing
- 10 new MCC features built: Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promo Queue, ACCA Tab, ALP Counter Tab, Keyboard Shortcuts, Undo on Everything, Sunday Auto-Merge
- Home screen built — 7 cards + 3 empty slots, clickable nav to each tab
- Full system test — 85/85 Phase 1, 29/29 Phase 3
- MCC server live at localhost:8080
- Project audit completed — 200+ files inventoried, dead files identified
- New files created: stuck_inbox.py, cost_predictor.py, promo_queue.py, merge_sessions.py, test_full_system.py, data/devices.json
- loop_manager.py wired to stuck_inbox — 3-strike rule sends goals to stuck inbox
- evaluator.py wired to promo_queue — score 9.0+ auto-queues for review
- aafl_wccs.py wired for Sunday auto-merge via merge_sessions.py
- New mcc_server.py endpoints: /stuck-inbox, /resolve-stuck, /run-now, /memory/knowledge, /memory/solutions, /memory/sources, /promo-queue, /approve-promo, /reject-promo, /acca-codes, /alp-data, /alp-add
- mission_control.html now has 12 tabs: Home, WCCS, Diff Viewer, Rewind, Sessions, HISTORY Search, Auto-Save Log, Provider Health, Kanban, AAFL Runs, Scout Control, Costs, AAFL Control, Memory, Promo, ACCA, ALP
- Keyboard shortcuts: 1-9 tab jump, R refresh, C connect, Esc close, Shift+? help overlay
- Undo toast system: 10-second undo on Resolve, Approve, Reject, Run Now, ALP Add

WHAT WE LEARNED:
- Provider reliability is CRITICAL. Gemini/Mistral/Cerebras all went dead in same run. LM Studio carried it solo. Single point of failure — need all providers GREEN before loop runs overnight.
- Early prototype files (model_router, setup_router, quick_fix) are historical gold showing AAFL evolution. Archive, don't delete.
- morning_report.md and queue_runner.py are still ACTIVE — forgotten but working.
- aafl_watchdog.py and cost_guard.py are Rule No.1 safety nets — need confirmation they're wired into current system before next overnight run.
- meta_proposals/ folder contains AAFL's own improvement ideas from May 18 — never acted on, may have value.
- solution_log table has no provider column (uses problem/approach columns). source_reputation uses domain/avg_score not source_url/reputation_score.

ACTION PLAN — NEXT PRIORITIES (IN ORDER):
1. [URGENT] Confirm aafl_watchdog.py + cost_guard.py wired into AAFL. Test with mock overnight run.
2. [URGENT] Read meta_proposals/ — AAFL's own improvement ideas. Implement high-value ones.
3. Read aafl_watchdog.py, cost_guard.py, afna_strategies.json fully. Wire afna_strategies into new Stuck Inbox system.
4. Archive dead files: model_router.py, setup_router.py (keep copy), quick_fix.py, control_panel.py to archive_dead/
5. Test provider health check script manually — confirm all GREEN before trusting overnight runs.
6. Groq + Cloudflare API keys — add to .env (manual, security rule).
7. Star Citizen v0.2 benchmark via AAFL — THIS IS THE PROOF TEST.
8. 5-project split (if AAFL passes Star Citizen).
9. r/LocalLLaMA post (trigger = Star Citizen benchmark passes).

ACCA CODES ADDED:
FFUE = Fluid Flexible Upgradeable Editable (new today)

WHAT TO DO AT NEXT WCCS:
- Add ACTION PLAN section to STATUS.md permanently
- Update STATUS.md CURRENT STATUS table with all 10 new features marked BUILT
- Add aafl_watchdog.py, cost_guard.py, afna_strategies.json, morning_report.md, queue_runner.py to BUILT section
- Move model_router, setup_router, quick_fix, control_panel to ARCHIVE section
- Add new ACCA code: FFUE = Fluid Flexible Upgradeable Editable


---

### 2026-05-23

SESSION: 23 May 2026 — PHASE 2 & MCC BUILD COMPLETE

WHAT GOT DONE TODAY:
- Provider Health Check system — 3 tiers, all 29/29 tests passing
- 10 new MCC features built: Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promo Queue, ACCA Tab, ALP Counter Tab, Keyboard Shortcuts, Undo on Everything, Sunday Auto-Merge
- Home screen built — 7 cards + 3 empty slots, clickable nav to each tab
- Full system test — 85/85 Phase 1, 29/29 Phase 3
- MCC server live at localhost:8080
- Project audit completed — 200+ files inventoried, dead files identified
- New files created: stuck_inbox.py, cost_predictor.py, promo_queue.py, merge_sessions.py, test_full_system.py, data/devices.json
- loop_manager.py wired to stuck_inbox — 3-strike rule sends goals to stuck inbox
- evaluator.py wired to promo_queue — score 9.0+ auto-queues for review
- aafl_wccs.py wired for Sunday auto-merge via merge_sessions.py
- New mcc_server.py endpoints: /stuck-inbox, /resolve-stuck, /run-now, /memory/knowledge, /memory/solutions, /memory/sources, /promo-queue, /approve-promo, /reject-promo, /acca-codes, /alp-data, /alp-add
- mission_control.html now has 12 tabs: Home, WCCS, Diff Viewer, Rewind, Sessions, HISTORY Search, Auto-Save Log, Provider Health, Kanban, AAFL Runs, Scout Control, Costs, AAFL Control, Memory, Promo, ACCA, ALP
- Keyboard shortcuts: 1-9 tab jump, R refresh, C connect, Esc close, Shift+? help overlay
- Undo toast system: 10-second undo on Resolve, Approve, Reject, Run Now, ALP Add

WHAT WE LEARNED:
- Provider reliability is CRITICAL. Gemini/Mistral/Cerebras all went dead in same run. LM Studio carried it solo. Single point of failure — need all providers GREEN before loop runs overnight.
- Early prototype files (model_router, setup_router, quick_fix) are historical gold showing AAFL evolution. Archive, don't delete.
- morning_report.md and queue_runner.py are still ACTIVE — forgotten but working.
- aafl_watchdog.py and cost_guard.py are Rule No.1 safety nets — need confirmation they're wired into current system before next overnight run.
- meta_proposals/ folder contains AAFL's own improvement ideas from May 18 — never acted on, may have value.
- solution_log table has no provider column (uses problem/approach columns). source_reputation uses domain/avg_score not source_url/reputation_score.

ACTION PLAN — NEXT PRIORITIES (IN ORDER):
1. [URGENT] Confirm aafl_watchdog.py + cost_guard.py wired into AAFL. Test with mock overnight run.
2. [URGENT] Read meta_proposals/ — AAFL's own improvement ideas. Implement high-value ones.
3. Read aafl_watchdog.py, cost_guard.py, afna_strategies.json fully. Wire afna_strategies into new Stuck Inbox system.
4. Archive dead files: model_router.py, setup_router.py (keep copy), quick_fix.py, control_panel.py to archive_dead/
5. Test provider health check script manually — confirm all GREEN before trusting overnight runs.
6. Groq + Cloudflare API keys — add to .env (manual, security rule).
7. Star Citizen v0.2 benchmark via AAFL — THIS IS THE PROOF TEST.
8. 5-project split (if AAFL passes Star Citizen).
9. r/LocalLLaMA post (trigger = Star Citizen benchmark passes).

ACCA CODES ADDED:
FFUE = Fluid Flexible Upgradeable Editable (new today)

WHAT TO DO AT NEXT WCCS:
- Add ACTION PLAN section to STATUS.md permanently
- Update STATUS.md CURRENT STATUS table with all 10 new features marked BUILT
- Add aafl_watchdog.py, cost_guard.py, afna_strategies.json, morning_report.md, queue_runner.py to BUILT section
- Move model_router, setup_router, quick_fix, control_panel to ARCHIVE section
- Add new ACCA code: FFUE = Fluid Flexible Upgradeable Editable


---

### 2026-05-23

SESSION: 23 May 2026 — MCC MOT + Build 1 Launch

WHAT GOT DONE:
✅ MCC UPGRADE COMPLETE — 107/108 MOT tests passing
✅ Phase 1: mcc_full_mot.py — 8 test groups, 108 checks built
✅ Phase 2: Self-Diagnosis tab built (MOT results, Known Issues, System Info, File Health)
✅ Phase 3: Home page upgrade — 6 instrument gauges + 4 quick action buttons
✅ Phase 4: Endpoint sweep — 8/8 pass
✅ Bug fixed: HEALTH_DIR typo in mcc_server.py → HEALTH_RESULTS
✅ Only failure: sfl_agent missing mss library (pre-existing, fix: pip install mss --break-system-packages)
✅ Build 1 CLAC block pasted and running (10 features)

BUILD 1 FEATURES IN PROGRESS:
1. Plugin/module architecture (modules/ folder, module_registry.json, module_loader.py)
2. Preset system (presets/ folder, 3 starter presets, preset bar in MCC)
3. Confidence threshold + cost cap per goal (aafl_config.json)
4. Auto-retry on failure (retry_manager.py, retry_log.json)
5. Smart suggester (smart_suggester.py, keyword routing)
6. Chain mode Scout→AAFL→Verify (chain_runner.py)
7. Timed scout runs (scout_timer.py, stop flag mechanism)
8. Source discovery mode (sources_library.json)
9. Stuck Inbox enhancements (severity, bulk resolve, AFNA suggestions)
10. Storage Manager Agent (storage_manager.py, storage_config.json, Storage tab in MCC)

DECISIONS MADE:
- PowerShell broken for DSP — use CMD only (Windows key + R → cmd)
- Commands always in 3 separate lines — never combined
- 60+ feature list cut to 12 Build 1 + 23 Build 2 (parking lot)
- FFUE baked into every build — modular, independent blocks
- MCC = personal cockpit, Build 2 parking lot items come after Build 1 tests pass
- Self-Diagnosis tab = internal only, not for commercial version

NEXT SESSION:
- Check Build 1 results
- Fix any failures
- Paste Build 2 CLAC block (23 features)
- Add Groq + Cloudflare API keys to .env (manual — security rule)
- Star Citizen v0.2 benchmark when all green


---

### 2026-05-23

SESSION: 23 May 2026 — Build 1 Complete + JS Bug Fixes

COMPLETED:
✅ MCC MOT 108/108 ALL CLEAR
✅ Build 1 — 10 features, 13/13 modules, 11 tests PASS
✅ WCCS tab — 5 drill-down buttons built and wired
✅ Home tab — Provider Health Show Details drill-down
✅ JS bug fixes — all missing onclick functions added (3 rounds)
✅ mss library installed (fixes sfl_agent pre-existing error)
✅ MCC confirmed loading at localhost:8080

BUGS FIXED THIS SESSION:
- phToggleDetail, homeCardClick, saveSession, connectData, homeRunAafl, homeStartScout, savePreset, loadPresets, loadHomeScreen — all were missing JS definitions, all fixed

DECISIONS:
- CMD only for DSP — PowerShell broken permanently
- Always 3 separate steps — never combined
- QuickEdit Mode needed in CMD for paste to work (Properties → Options → QuickEdit)
- MCC server = python mcc_server.py (short version works)
- Build 2 (23 parking lot features) = next session

NEXT SESSION:
1. Build 2 CLAC block (23 parking lot features)
2. Star Citizen v0.2 benchmark
3. Groq + Cloudflare keys to .env
4. r/LocalLLaMA post when benchmark passes

---

SESSION 23 May 2026 — Build 1 Complete + UI Drill-downs:
- MCC MOT 108/108 (after mss pip fix)
- Build 1 complete: 10 features, 13/13 modules, 12 tests PASS
- Features: plugin architecture, preset system, confidence threshold, cost cap, auto-retry, smart suggester, chain mode, timed scout, source discovery, stuck inbox enhanced, storage manager
- WCCS drill-down x5 added to WCCS tab
- Home Provider Health drill-down added
- CMD confirmed only working terminal for DSP
- Build 2 (23 parking lot features) ready next


---

### 2026-05-24

SESSION 4 — 24 May 2026
- WCCS recovery: STATUS.md was stale (Build 1 not recorded), fixed
- STATUS.md patched 138→162 lines, Build 1 in BUILT, 23 Build 2 features in PENDING
- HISTORY.md verified (23 May entry already at line 479)
- Git commit be794c5
- aafl_wccs.py --dry-run kicked off (result pending)
- Confirmed: aafl_wccs.py (free Mistral) replaces CLAC WCCS permanently
- ALP lesson: always verify WCCS actually saved before closing session

---

## Session 24 May 2026 — Save System Audit + Fix
- Audited all 7 sessions since 20 May split
- Found 7 items discussed but never saved (FFUE rule, auto-Sunday merge, mini-save protocol, recovery path, pre-flight ALP, tools to explore, WCCS skill outdated)
- Wired auto-Sunday merge into aafl_wccs.py
- Added pre-flight ALP check (auto-creates chat_latest.txt if missing)
- Created SAVE_NOW.bat (one-click bulletproof save)
- Updated STATUS.md with missing items
- DSP confirmed as always-yes — never ask again


---

### 2026-05-24

Session 24 May 2026 — Save system audit complete. 7 missing items recovered from past chats. Auto-Sunday merge wired into aafl_wccs.py. Pre-flight ALP check added. SAVE_NOW.bat created. WCCS skill v2 uploaded. Action plan skill uploaded. FFUE design rule, GitHub MCP, Deep Research added to PENDING. DSP confirmed always-yes. Complete project todo list compiled.


---

### 2026-05-24

test session from mcc_test.py


---

### 2026-05-24

test session from mcc_test.py


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:27:03] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:27:03] "test capture from mcc_test.py"
[2026-05-24 19:28:26] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py


---

### 2026-05-24

test session from mcc_test.py


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"
[2026-05-24 20:33:26] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"
[2026-05-24 20:33:26] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"
[2026-05-24 20:33:26] "test capture from mcc_test.py"
[2026-05-24 20:38:57] "test capture from mcc_test.py"


---

### 2026-05-24

test session from mcc_test.py[2026-05-24 19:32:35] "test capture from mcc_test.py"
[2026-05-24 19:39:27] "test capture from mcc_test.py"
[2026-05-24 19:44:50] "test capture from mcc_test.py"
[2026-05-24 20:24:13] "test capture from mcc_test.py"
[2026-05-24 20:29:45] "test capture from mcc_test.py"
[2026-05-24 20:33:26] "test capture from mcc_test.py"
[2026-05-24 20:38:57] "test capture from mcc_test.py"


---

### 2026-05-24

SESUM (Session Summary) — 24 May 2026:
MCC test suite built (mcc_test.py, 138 tests, 133/138 PASS, dual-run comparison). Auto-refresh polling added (30s, "updated Xs ago" label, manual refresh button). AAFL Control fixed — Run Now works, Live Output panel with phase/provider badges, Workflow Builder with presets, AAFL↔Scout Bridge. Scout tab wired — 6 strategy buttons linked to chief_scout.py. ACCA tab renamed to "Instructions & Codes" with collapsible MCC guide. Full project audit — docs/PROJECT_AUDIT.md created, STATUS.md updated with 22 missing items. 10 dead files archived. ACCA.md cleaned — 5 codes added (CLACH/CNP/RIBS/SESUM/SBS), 5 mode codes reformatted, CAP duplicate confirmed clean. FFUE corrected to Fluid Flexible Upgradeable Editable. aafl_wccs.py attempted — all providers failed, manual session log cc2 committed. Coder 32B loaded for retry.


---

### 2026-05-25

SESSION: 25 May 2026 (AM) — SIF + Build 2 Test + WCBB + Knowledge Bank
✅ SIF delivered, Build 2 CLAC block written (23 features), 68-test smoke test designed, 17 WCBB fixes designed, Knowledge Harvester + Auto-Capture Hook built, AAFL Plan phase now queries knowledge bank, Knowledge tab designed for MCC, Mission statement confirmed aligned.


---

### 2026-05-25

Session Summary — 25 May 2026
Chat: "Implementing Claude software development best practices"
What happened:

Scott asked if the project is worth investing time into — AIO (AI Opinion): YES, but Star Citizen benchmark is the gate. Pass = keep going, fail = rethink
Mapped 6 Claude best practices against the project — all 6 already covered
Scott paid £20 extra on top of Pro subscription (was past weekly limit, resets Tuesday 7PM)
Caught Scott on Opus 4.7 — SuperClaude flagged it, Scott switched off it permanently for brainstorming/instruction tasks
Built ALP Audit Skill v2 with Mr Claude (model-switching teacher) + SuperClaude (emergency protocol at 90% allowance) + check #13 (switch back after Opus)
Uploaded v2 to project files — confirmed loaded and working

Decisions made:

Opus reserved for web searches and file scanning only, not instructions/brainstorming
Sonnet is the daily driver, Haiku for small jobs
Star Citizen benchmark is next priority (unchanged)

Files created:

SKILL_alp_audit_v2.md — uploaded to project files ✅

No ACCA codes added (none new this session)
Next priorities (unchanged):

Wire aafl_watchdog.py + cost_guard.py (safety first)
Star Citizen v0.2 benchmark via AAFL autonomous run
Wait for weekly limit reset Tuesday 7PM


---

### 2026-05-27

DATE: 2026-05-27
SESSION_TYPE: Chat (CLACH)
PROJECT: VKB-SpinDoctor / AAFL

CLAC_BLOCKS_WRITTEN_NOT_YET_RUN:
- Block A: STATUS.md restore + aafl_wccs.py read-merge-write + 90% sanity check in mcc_server.py
- Block B: 7 features (line count warning, old saves scanner, chat→SESUM, Missions tab, UI shuffle, tooltips, IBR scan) — RAN, mostly complete, 3 bugs found
- Block C: 3 bug fixes (banner location, undefined/undefined, wrong timestamps)
- Block D: Red banner replaced with post-save nudge → blue pulse glow + bouncing arrow + "Next step →" label on Copy STATUS.md button
- Block E: SESUM saved to session_logs/sesum_2026-05-27.md

BUGS_IDENTIFIED_THIS_SESSION:
- Red banner showing on ALL tabs — should be WCCS tab only
- Banner shows "undefined / undefined lines" — JS reading wrong field names from /api/statuscheck
- Recent saves timestamps showing 2026-05-25 — using git dates not file mtime
- Red banner UX wrong entirely — replaced with post-save nudge design (Block D)

TASKS_CONFIRMED_INCOMPLETE:
- ALP still showing as standalone top tab — Task 5 (UI shuffle) failed to remove it
- Memory tab still in top bar — likely same failure
- AAFL Runs removal from top bar — unconfirmed

JOBS_AUDIT_DONE:
- 18 jobs tracked
- 7 complete, 8 not run, 3 partially failed
- All outstanding jobs listed and prioritised

NEW_ACCA_CODES_THIS_SESSION:
- IBR = Investigate Brainstorm Report
- AXO = accident (acca)
- OCB = One Copy Box
- STATUS: in chat only, NOT yet written to ACCA.md on disk

STATUS_MD_HEALTH: DEGRADED — 168 lines vs 195 baseline (86%). Block A not run. URGENT.
MOT_CURRENT: 108/108 ALL CLEAR (last confirmed Build 7 features session)

NEXT_PRIORITIES:
1. OCB — combine all outstanding blocks (A+C+D+E + ALP/Memory/Runs UI fix + ACCA codes to disk) into one block
2. Run combined block
3. Star Citizen v0.2 benchmark
4. GROQ + Cloudflare keys to .env
5. meta_proposals/ — 3 unactioned self-improvement proposals

RULE_VIOLATIONS_THIS_SESSION:
- ALP tab still in top bar = Rule 1 violation (wasted tokens loading unused tab every message)
- 3 screenshots sent in one message (earlier) = ALP leak


---

### 2026-05-28

DATE: 2026-05-28 (combined 26-28 May)
SESSION_TYPE: Combined SESUM — 3 days merged
PROJECT: VKB-SpinDoctor / AAFL / AASKC

DAY 1 (26 May): Build 3 MCC overhaul 14 tasks complete. Build 4 partial — Quick Ask, accordions, sidebar nav started. Health Suite consolidation started. ALP ran out.
DAY 2 (27 May): STATUS.md truncation investigation (IBR). 9 OCB fixes designed. Block B 7 features. Fix Quick Ask cascade. ALP ran out mid-CLAC.
DAY 3 (28 May): OCB-A retry designed (9 fixes + Work Checker + Self-Health). OCB-B (Body Map + Auto-Fix + Real-Time). OCB-C (Missions + Workflow merge + Storage + GPU/CPU/RAM). OCB-D LLOW complete — engine + canvas + 10 endpoints + 3 starter workflows. Multiple ALP burnouts. Work Checker system designed. STORM designed.

PRODUCT NAME CONFIRMED: AASKC (Autonomous AI Simultaneous Knowledge Connection)
KNOWN BUGS: LLOW empty (no elements/arrows loaded), dials/gauges dead, timeline black, popup z-index, animations not rendering data, system_monitor.py data pipeline broken
NEW_ACCA: CLACR, WRC, LLOW, STORM, AASKC
NEXT: Bug fix OCB, then visual overhaul (Layout 2+3 mix), WENTO additions, Storage upgrades

<!-- END_OF_FILE -->


---
<!-- merged from session_logs/2026-05-16_session.md on 2026-05-20 19:03 -->

# Session Log — 16 May 2026

**Source:** chat_latest.txt (15 May 2026 overnight session)

## What changed vs. v23

| Item | Change |
|---|---|
| memory_bank.py | Was missing from Current Status — now ✅ (190 lines, SQLite, self-test passed) |
| cost_guard.py | Was missing entirely — now ✅ (135 lines, all 3 brakes fire) |
| Memory Bank (Next Priorities #5) | Marked complete |
| Key Files table | Added memory_bank.py and cost_guard.py |
| ALP_Database.md | Created (was missing). 12 entries seeded from this session's discoveries. |
| Claude Code ALP Rules | Added 9 new rules: Sonnet vs Opus, screenshots, new chats, combine questions, old file removal, Extended Thinking, WCCS updated instruction, session log format, n8n discovery |

## Key discoveries captured in ALP_Database.md
- Sonnet = 3-5x more messages than Opus
- Chat + Claude Code share same allowance pool (was misunderstood)
- Session logs replace full handover rewrites (WCCS upgraded)
- n8n self-hosted = potential AAFL replacement worth investigating
- SFL not suited for reading chat (use text export instead)

## Next session pick-up
1. Add file-write step to loop_manager.py (code saves to DB not disk)
2. Fix HuggingFace model name
3. Investigate n8n as AAFL foundation
4. Remove old handover versions (v16–v22) from Project Files
5. Switch model to Sonnet in Claude Chat


---
<!-- merged from session_logs/2026-05-17-cc.md on 2026-05-20 19:03 -->

# Session Log — 17 May 2026 (Claude Code)

**Handover:** v15 → v16
**Focus:** AAFL loop components, HuggingFace model fix, LangGraph, loop test

## Done This Session

1. aafl_core.py: HuggingFace model fixed → `mistralai/Mistral-7B-Instruct-v0.3` (was gated Llama Vision)
2. Vision route updated — huggingface removed (not a vision model)
3. LangGraph 1.2.0 installed and verified (`langgraph OK`)
4. ddgs (renamed duckduckgo_search) installed
5. evaluator.py built — 0-10 scorer, completeness/clarity/accuracy, pure logic, no APIs
6. researcher.py built — DuckDuckGo search via ddgs, top 5 results, fallback on error
7. sfl_agent.py: call_aafl(prompt) added at line 580
8. goal.txt updated: Python function returning top 3 numbers
9. loop_manager.py: max_loop_iters/max_llm_calls decoupled — --once now runs 1 full loop cycle
10. Loop test PASSED (under 30s): Gemini Flash (plan) + Mistral Codestral (work) → goal_met=True
11. DB verified: entry 6a948adb stored in knowledge_engine.db
12. loop_output/ confirmed: 2 result files present
13. Git commit: Backup 2026-05-17 18:26:30 (12 files, 346 insertions)

## Issues Found

- Cerebras llama3.1-70b model name is dead — fails with NotFoundError
- duckduckgo_search package renamed to ddgs — old import works but warns

## Next Session — Pick Up At

1. Wire evaluator.py into loop_manager.py result scoring
2. Wire researcher.py into planning step
3. Fix Cerebras provider model name
4. win_hardener module (9 problems)


---
<!-- merged from session_logs/2026-05-17-cc2.md on 2026-05-20 19:03 -->

# Session Log — 17 May 2026 (Claude Code — Session 2)

**Handover:** v16 → v17
**Focus:** Phases B+C+D — learning DB, scout agent, source reputation, tag taxonomy

## Done This Session

1. memory_bank.py: Fixed critical bug — `return result` → `return results` in recent()
2. memory_bank.py: Phase B — solution_log table, search_solution(), search_failures(), store_solution()
3. memory_bank.py: Phase C — source_reputation table, update_source(), get_top_sources(), get_blocked_sources()
4. memory_bank.py: Phase D — TAGS constant (23 tags), extended solution_log columns (tags, cost_tokens, iterations, game, hardware, verified_at), _migrate_solution_log() for existing DBs
5. researcher.py: Phase C — scout(goal) added with urlparse domain extraction, blocked/top source filtering, returns dict {results, briefing}
6. loop_manager.py: Phase B — DB cache check before loop, failure injection into plan prompt, store_solution() after scoring
7. loop_manager.py: Phase C — scout() call before planning, briefing injection into plan prompt, update_source() after scoring per domain
8. loop_manager.py: Phase D — fast LLM tag inference call, game detection (_detect_game()), [DB] Stored print with score/tags/iterations
9. memory_bank self-test PASSED: all functions including solution_log and source_reputation
10. --once run 1: [SCOUT] 5 sources, score 7.93/10, goal_met=True, stored to solution_log
11. --once run 2: [DB] Past solution found (score 7.93) — DB cache hit confirmed, no LLM calls made
12. source_reputation verified: 6 entries (github.com, docs.python.org, geeksforgeeks.org, realpython.com, pythonguides.com + example.com from self-test)
13. solution_log verified: extended fields game/hardware/iterations all populated
14. Git commit: "Phases B+C+D: learning DB, scout agent, source reputation, tag taxonomy"
15. sfl_agent.py HANDOVER_FILENAME updated to VKB_SpinDoctor_Handover_v27.md

## Issues Found

- Tags always empty: fast task type hits Cerebras (broken) + LM Studio (offline) + Gemini Flash (empty response for short tasks). Graceful fallback to "" — not a crash, just missing enrichment.
- Cerebras model name still broken (llama3.1-70b renamed) — carried forward from v16

## Next Session — Pick Up At

1. Fix Cerebras provider model name (check current valid model name)
2. win_hardener module (9 problems)
3. Star Citizen full support


---
<!-- merged from session_logs/2026-05-17-cc3.md on 2026-05-20 19:03 -->

# Session Log — 17 May 2026 (Claude Code — Session 3)

**Handover:** v18 → v19
**Focus:** Handover maintenance — 11 fixes across v28/v29

## Done This Session

1. Handover v28 fix batch 1 (7 fixes): ACCA table expanded (WS, WSF, CA, AAFL, ALP, SIF, WYM, WENTO, SS, CLAC, WCCS added); GitHub section added (jscottl-sketch / vkb-spin-doctor / private); Cloudflare Workers AI row added to provider table; both Groq rows updated with auth fix note; balance note updated with debug burn warning; file tree updated (control_panel.py + Knowledge_Engine_Schema_v1.md — both confirmed present)
2. Handover v28 fix batch 2 (4 fixes): WHAT NOT TO DO — credit burn / cost_guard warning added; Qwen2.5-VL-72B added to hardware (44GB, D:\lmstudio-community); HOW_TO_INTEGRATE_DIAGNOSTIC.py added to file tree (confirmed present; sl_loop.py and screenshot_diagnostic.py not found — not added); both Groq rows updated to "confirmed working"

## Issues Found

- sl_loop.py and screenshot_diagnostic.py not found in project folder at time of check

## Next Session — Pick Up At

1. Fix Cerebras provider model name (llama3.1-70b renamed)
2. win_hardener module (9 problems)
3. Star Citizen full support


---
<!-- merged from session_logs/2026-05-17-cc4.md on 2026-05-20 19:03 -->

# Session Log — 17 May 2026 (Claude Code — Session 4)

**Handover:** v19 → v20
**Focus:** Cerebras fix, AAFL loop improvements, bat utilities, win_hardener module

## Done This Session

1. **Cerebras provider fixed** — llama3.1-70b deprecated → llama-3.3-70b deprecated → gpt-oss-120b (current stable). Confirmed working at 0.54s response time.
2. **reasoning_content fallback** — aafl_core.py `_call()` now falls back to `reasoning_content` when `content=None` (affects Cerebras gpt-oss-120b, DeepSeek R1, and other reasoning models).
3. **Cloudflare provider added** — aafl_core.py: provider entry for `cloudflare/@cf/meta/llama-3.1-8b-instruct`. `extra_env` field added + `_has_key()` updated to check both `CLOUDFLARE_API_KEY` and `CLOUDFLARE_ACCOUNT_ID`. Commented placeholders added to .env.
4. **Groq auth clarified** — GROQ_API_KEY env var is the correct auth method (not Google OAuth). Commented placeholder added to .env.
5. **set_goal.bat** — writes goal.txt via `$env:_GOAL` PowerShell trick to avoid special character issues in batch.
6. **aafl_doctor.bat** — pre-flight health check: last score + providers from DB metadata, row counts, current goal. Two-step Python inline to avoid batch parenthesis conflicts.
7. **regression_test.bat** — sets known goal, runs loop_manager.py --once, prints PASS/FAIL.
8. **goal_queue.txt + queue_runner.py + queue_runner.bat** — reads queue file, runs loop --once per goal, logs results to loop_output/queue_log_*.txt.
9. **loop_manager.py report naming** — reports now save to `loop_output/YYYY-MM-DD_HH-MM_<first 4 words of goal>.md`. morning_report.md always updated as copy of latest. No overwrites.
10. **Completion notification** — winsound + ctypes (stdlib only). Beeps (880Hz + 1100Hz) then MessageBoxW with stop reason, iterations, cost.
11. **infer_tags_from_keywords()** — memory_bank.py fallback for when LLM tag call fails. Substring matches goal text against TAGS list. Wired into loop_manager.py.
12. **problems/win_hardener.py** — 9 problems W-001→W-009: USB Selective Suspend (powercfg), polling rate advisory, joy.cpl check, HID ConfigFlags error code, registry cleaner damage, duplicate OEM entries, enumeration order advisory, HidUsb driver disabled, GameInput conflict.
13. **WinHardenerCard wired into spin_doctor.py** — Fix tab now shows win_hardener card with refresh/details popup. Load error displayed if import fails.

## Issues Encountered

- Cerebras model name required three iterations: llama3.1-70b → llama-3.3-70b → gpt-oss-120b
- gpt-oss-120b returns content=None with small max_tokens (reasoning model — thinking fills the budget). Fixed with reasoning_content fallback.
- aafl_doctor.bat Python inline couldn't use `( )` redirect blocks due to batch parenthesis conflicts — solved by splitting into two separate python -c calls.
- DB cache hit prevented live Cerebras routing test — tested Cerebras directly via aafl_core.py instead.
- python-dotenv, litellm, duckduckgo-search all needed pip install before loop_manager.py would run.

## Next Session — Pick Up At

1. Star Citizen full support
2. Add GROQ_API_KEY to .env (from console.groq.com → API Keys tab)
3. Add Cloudflare keys to .env (CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID from dash.cloudflare.com)
4. Verify all 6 skills toggles ON at claude.ai/customize/skills (manual)


---
<!-- merged from session_logs/2026-05-17_session.md on 2026-05-20 19:03 -->

# Session Log — 17 May 2026

**Handover:** v24 → v25
**Focus:** Upload 6 custom skills + WCCS skill v2 + end-of-session tooling

---

## Done This Session

1. All 6 custom skills uploaded to claude.ai/customize/skills via Chrome browser
2. Found correct upload path: + button in chat → Skills → Add skill → upload zip
3. Skills management confirmed at: claude.ai/customize/skills
4. WCCS skill replaced with v2 — now includes version incrementing + wccs_log.md logging
5. Built RUN_WCCS.bat — one-click batch file for end-of-session saves
6. Discovered "Save skill" button — can replace skills directly from SKILL.md output in chat
7. ALP #13 added: Research Anthropic docs FIRST for any platform question

## ALP Violations This Session

- Multiple messages wasted guessing UI paths before checking docs
- Batch file errors (wrong Desktop path, spaces in zip paths) caused repeated rebuilds
- Should have built zip server-side from the start

## New ALP Rule

**#13 — Research docs FIRST.** One Anthropic docs search costs less than 5 wrong guesses.

## Next Session — Pick Up At

1. Verify all 6 skill toggles ON at claude.ai/customize/skills
2. Test skills in a fresh chat
3. Add file-write step to loop_manager.py


---
<!-- merged from session_logs/2026-05-18-cc1.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18-cc1

**Date:** 18 May 2026
**Tool:** Claude Code (CLAC)
**Handover:** v30 → v31

---

## Tasks Completed

### 1. Fix verify step — empty responses, loop scoring blind
- `aafl_core._call()`: reasoning_content `</think>` extraction — extracts post-think answer, not thinking chain
- `loop_manager.py`: defensive guard before `evaluate()` — `if not work_text.strip(): continue`
- `loop_manager.py`: `load_goal()` changed to `utf-8-sig` — fixes BOM crash from PowerShell Set-Content
- `loop_manager.py`: tag inference `max_tokens=50` → `200` — fixes Gemini 2.5 Flash empty response on short token budget

### 2. run_aafl.bat
- One-click full launch: checks if LM Studio is running, starts it if not, polls port 1234 every 2s (90s timeout), runs aafl_doctor.bat, runs queue_runner.bat
- LM Studio path: `%LOCALAPPDATA%\Programs\LM Studio\LM Studio.exe`

### 3. Regression test PASS
- Score: 8.83/10 (completeness=10.0, clarity=8.0, accuracy=8.5)
- Plan provider: gemini_flash. Work provider: mistral_code.

### 4. Mission Control board
- `C:\Users\jscot\Desktop\mission_control.html` — standalone kanban board, dark theme, drag & drop, click to edit, add/delete
- `C:\Users\jscot\Desktop\mission_control_tasks.json` — 30 tasks pre-populated from v30 handover
- File System Access API + IndexedDB for seamless read/write
- AAFL/CLAC update JSON directly; Scott hits Refresh to pull changes

### 5. AAFL queue runner end-to-end test
- 4 goals processed: cache hit (9.33), VKB polling rate (8.67), WT axis drift (8.67), HidHide+SC (8.07)

### 6. Fix 4 loop_manager.py bugs
- Web search not reaching work step: `if briefing_text:` → `if briefing_data["results"]:`, briefing now injected into work prompt too
- Plan truncating: `max_tokens=512` → `max_tokens=1024`
- Chatbot follow-up questions: `AGENT_SYSTEM` constant added, injected via `system=` on all LLM calls
- Goal queue: completed test goals commented out, "Add Star Citizen full support" is sole active goal

### 7. WCCS v31
- Handover v30 → v31 written
- wccs_log.md updated (row 6)
- Session log written
- sfl_agent.py HANDOVER_FILENAME updated to v31

---

## Files Changed

| File | Change |
|---|---|
| aafl_core.py | </think> extraction in _call() |
| loop_manager.py | utf-8-sig, verify guard, tag max_tokens, AGENT_SYSTEM, plan 1024 tokens, briefing to work step, briefing guard |
| goal_queue.txt | Completed goals commented out |
| run_aafl.bat | Created |
| C:\Users\jscot\Desktop\mission_control.html | Created |
| C:\Users\jscot\Desktop\mission_control_tasks.json | Created |
| VKB_SpinDoctor_Handover_v31.md | Created |
| wccs_log.md | Row 6 added |
| sfl_agent.py | HANDOVER_FILENAME updated to v31 |

---

## Regression Test Result

```
[LOOP] Score: 8.83/10  (completeness=10.0  clarity=8.0  accuracy=8.5)
[LOOP] Score >= 7 — goal met.
[RESULT] PASS
```


---
<!-- merged from session_logs/2026-05-18-cc2.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18-cc2

**Session:** Claude Code session 2, 18 May 2026
**Handover:** v32 → v33
**Task:** Build AAFL self-improving meta-loop

---

## Files Created

| File | Purpose |
|---|---|
| `meta_loop.py` | AAFL meta-loop — reads loop_output/ stats, processes meta_queue.txt goals, runs scout→plan→work→score, second opinion, writes proposals to meta_proposals/. Dry-run default. --apply writes code changes with snapshot+regression guard. |
| `meta_queue.txt` | 3 starter goals for the meta-loop: LangGraph comparison, bottleneck finder, provider scorer. Goals are commented out after processing. |
| `meta_loop.bat` | Launcher — runs meta_loop.py --once by default, passes extra args through. |
| `meta_proposals/2026-05-18_compare_langgraph_120_vs_current.md` | First proposal — LangGraph 1.2.0 vs loop_manager.py comparison. Status: FLAGGED (scores 8.03/7.73, below 8.5 threshold). |

## Files Modified

| File | Change |
|---|---|
| `aafl_core.py` | Cerebras model fixed: `llama-3.3-70b` → `gpt-oss-120b` (deprecated model was still in code despite handover saying it was fixed) |
| `sfl_agent.py` | HANDOVER_FILENAME updated: v32 → v33 |
| `wccs_log.md` | Row 8 added |
| `Desktop/mission_control_tasks.json` | Added t031 (meta-loop dry-run review, Up Next) and t032 (Task Scheduler, Backlog) |
| `VKB_SpinDoctor_Handover_v33.md` | New handover written |

---

## Key Decisions

- **Dry-run default** — no code changes without explicit --apply. Safety-first.
- **Second opinion** uses task_type="batch" (→ Mistral route) vs task_type="reason" (→ Cerebras route) for genuine different-provider comparison
- **Hard cap** of 3 meta-goals per invocation
- **--apply flow**: snapshot backups/ → apply CHANGE FILE blocks → run regression_test.bat → restore if fail
- **Goal queue**: goals are commented out after processing with `# DONE` prefix

## Bugs Fixed

- **Cerebras model in aafl_core.py** was still `llama-3.3-70b` (deprecated) even though handover v32 said it was fixed. The handover was updated but the code wasn't. Fixed to `gpt-oss-120b` (confirmed working 0.54s in v32 session).

## Test Results

- First dry-run: `meta_loop.bat --once` — SUCCESS
- Proposal written: `meta_proposals/2026-05-18_compare_langgraph_120_vs_current.md`
- Scores: 8.03 (OpenRouter) / 7.73 (Mistral) — FLAGGED (below 8.5 threshold)
- meta_queue.txt goal 1 commented out as `# DONE`

## Active Provider Status (during this session)

| Provider | Status |
|---|---|
| LM Studio DeepSeek R1 | SKIP (timeout — LM Studio not running) |
| Gemini 2.5 Flash | FAIL (503 Service Unavailable — transient) |
| Cerebras GPT-OSS 120B | FAIL (still had llama-3.3-70b in code — now fixed) |
| OpenRouter Auto | ✅ Working (23–34s) |
| Mistral Codestral | ✅ Working (7.66s) |

---

## Next Priorities

1. Review `meta_proposals/2026-05-18_compare_langgraph_120_vs_current.md`
2. Run `meta_loop.bat` again for goal 2 (bottleneck finder)
3. Add GROQ_API_KEY to .env manually
4. Add Cloudflare keys to .env manually
5. Star Citizen full support


---
<!-- merged from session_logs/2026-05-18-cc3.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18-cc3

**Handover:** v33 → v34
**Focus:** meta_loop.py real-data injection fix

## What was done

1. Ran meta_loop.bat for goal 2 (bottleneck finder) — FLAGGED 6.23/9 — AI fabricated data
2. Ran meta_loop.bat for goal 3 (provider scorer) — FLAGGED 5.83/9 — AI fabricated data
3. Diagnosed root cause: LLMs can't analyse what they can't see
   - `_inject_file_context` capped at 100 lines — not enough for loop_manager.py
   - `_inject_db_context` triggered only on 4 narrow keywords — missed both goals 2+3
   - DB query missing columns (tags, iterations, game, hardware, created_at)
   - No loop_output report text injected — no real performance data for bottleneck analysis
4. Fixed meta_loop.py:
   - `_inject_file_context`: 100 → 600-line cap, full file, note shows total vs cap
   - `_inject_db_context`: 4 → 14 keywords; all solution_log columns; "no provider metadata" note
   - New `_inject_loop_reports()`: last 3 loop_output reports, 80 lines each, fires on bottleneck/provider/latency keywords
   - Wired `report_ctx` into work_prompt in `run_meta_goal()`

## Files changed
- meta_loop.py — 4 changes (file injection cap, DB keywords, DB columns, new function + wiring)

## Files written (WCCS)
- VKB_SpinDoctor_Handover_v34.md
- wccs_log.md (row 9 added)
- session_logs/2026-05-18-cc3.md (this file)
- sfl_agent.py HANDOVER_FILENAME updated to v34

## Next priorities
1. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat
2. Add GROQ_API_KEY to .env manually
3. Add Cloudflare keys to .env manually
4. Star Citizen full support


---
<!-- merged from session_logs/2026-05-18-cc4.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18-cc4

**Handover:** v34 → v35
**Focus:** mcu_optimizer.py + WCCS step 7

## What was done

1. Confirmed Fix 1 (meta_loop.py real-data injection) in place from cc3 — no rework needed
2. Read mission_control_tasks.json schema: 32 tasks, columns: Up Next/In Progress/Blocked/Backlog/Done
3. Built mcu_optimizer.py:
   - Finds latest handover (highest vNN number), extracts Status + Next Priorities
   - Reads last 3 session logs (capped at 40 lines each)
   - Loads mission_control_tasks.json, splits into active vs Done
   - Sends context to AAFLCore task_type="batch" (Mistral), max_tokens=3000
   - LLM returns reorganised active tasks as JSON array
   - Safety net: re-adds any tasks LLM dropped, strips any LLM-invented tasks, validates column names, never moves out of Done
   - Diffs old vs new (column + priority changes), writes JSON back, prints summary
   - Desktop path detection: tries standard Desktop first, OneDrive\Desktop fallback
4. Fixed 3 bugs during test run:
   - result.cost → result.cost_usd (CallResult attribute name)
   - Unicode arrows (→) → ASCII (->) for Windows cp1252 console
   - Em dash (—) → ASCII hyphen (-) in "no changes" message
5. Test run successful: Mistral 22s, $0.0058, 0 changes (board already optimal), JSON written
6. Added mcu_optimizer.py to WCCS protocol as step 7

## Files created
- mcu_optimizer.py

## Files written (WCCS)
- VKB_SpinDoctor_Handover_v35.md
- wccs_log.md (row 10 added)
- session_logs/2026-05-18-cc4.md (this file)
- sfl_agent.py HANDOVER_FILENAME updated to v35
- mcu_optimizer.py run → mission_control_tasks.json updated (step 7)

## Next priorities
1. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat
2. Add GROQ_API_KEY to .env manually
3. Add Cloudflare keys to .env manually
4. Star Citizen full support


---
<!-- merged from session_logs/2026-05-18-cc5.md on 2026-05-20 19:03 -->

# Session Log -- 2026-05-18-cc5

**Handover:** v36 -> v37
**Focus:** WCCS automation run

## Chat Summary (from chat_latest.txt)

﻿WCCS automation system built — 4 files created this session.

1. wccs_runner.py — standalone WCCS automation script. Reads chat_latest.txt + latest handover, sends to AAFLCore (free LLM, task_type="batch") to generate new CHAT LOG entry + updated NEXT PRIORITIES. Writes vNN+1 handover, session log, appends wccs_log.md, runs mcu_optimizer.py + dashboard_builder.py, updates sfl_agent.py HANDOVER_FILENAME, deletes old handover + chat_latest.txt. Prints PASS/FAIL summary. Follows mcu_optimizer.py pattern.

2. mcc_server.py — stdlib HTTP server on localhost:8080. ThreadingHTTPServer. Endpoints: POST /wccs, POST /capture, GET /captures, GET /status. _wccs_lock prevents concurrent WCCS runs. No external packages.

3. mission_control.html — upgraded to 5 tabs. New WCCS tab: textarea, Capture button, Save & Run WCCS button, PASS/FAIL result, captures display, WCCS stdout output. Top capture banner on ALL tabs: Last capture pill green/yellow/red. Server notice if server unreachable. Server polls every 30s.

4. WCCS.bat — checks port 8080, starts mcc_server.py in background if not running, opens mission_control.html in Chrome.

Tests passed: /status JSON confirmed, /capture working, /captures working, port 8080 LISTENING confirmed.

New ACCA codes: None

Next priorities:
1. Open mission_control.html in Chrome, confirm 5 tabs + WCCS tab working
2. Re-add goals 2+3 to meta_queue.txt and re-run meta_loop.bat
3. Add GROQ_API_KEY to .env manually
4. Add Cloudflare keys to .env manually
5. Star Citizen full support

## Generated Chat Log Entry

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

## Files written (WCCS)
- VKB_SpinDoctor_Handover_v37.md
- wccs_log.md (row appended)
- 2026-05-18-cc5.md (this file)
- sfl_agent.py HANDOVER_FILENAME updated to v37
- mcu_optimizer.py run
- dashboard_builder.py run


---
<!-- merged from session_logs/2026-05-18-cc6.md on 2026-05-20 19:03 -->

# Session Log -- 2026-05-18-cc6

**Handover:** v37 -> v38
**Focus:** WCCS automation run

## Chat Summary (from chat_latest.txt)

SESSION: 18 May 2026 — Chat session 6

KEY DECISIONS:
- WCCS automation system built: wccs_runner.py + mcc_server.py + WCCS.bat + MCC 5th tab. All PASS. v37 written.
- DSP rule agreed: always ask Scott about --dangerously-skip-permissions before every CLAC block, no exceptions.
- DSP rule to be added to handover WCCS Protocol section + wccs-generator skill.
- WCCS fully delegated to AAFL: Chat writes 10-line summary only, AAFL does all file work via free LLM.
- Capture-as-you-go system designed: MCC captures throughout session so end-of-session summary is just a trigger.
- mcc_server.py bridges MCC HTML to filesystem: POST /wccs, POST /capture, GET /captures, GET /status.
- MCC redesign brainstormed: Option A (sidebar HUD) vs Option B (single scroll BI-friendly). Decision pending.
- WCCS must live IN MCC permanently — pinned bottom of every panel, always visible.
- Capture timer (green/yellow/red) in top stats bar on all panels.
- Old handovers v27-v34 still in folder — need deleting. Only v37 needed.

NEW ACCA CODES: None this session

NEXT PRIORITIES:
1. Add DSP rule to handover + wccs-generator skill (2 CLAC blocks ready)
2. Scott decides MCC layout: Option A or B, dark or light theme
3. Build MCC redesign in CLAC
4. Delete old handovers v27-v34 from folder
5. Swap v36 for v37 in Project Files

## Generated Chat Log Entry

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

## Files written (WCCS)
- VKB_SpinDoctor_Handover_v38.md
- wccs_log.md (row appended)
- 2026-05-18-cc6.md (this file)
- sfl_agent.py HANDOVER_FILENAME updated to v38
- mcu_optimizer.py run
- dashboard_builder.py run


---
<!-- merged from session_logs/2026-05-19-cc1.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19 (Claude Code session 1)
**Handover:** v38 → v39

## Built / Changed
- task_router.py added to handover PROJECT STATUS table and PROJECT FILES tree
- Future Modules section added to v38/v39 (10 niche AI tools table)
- Old handovers v27, v29-v34 deleted (7 files)
- DSP rule added to WHO IS SCOTT section in handover
- /wccs slash command created at .claude/commands/wccs.md (7-step WCCS automation)
- v39 handover written with 5-project split plan and 8 providers to sign up

## Mystery Files Identified
- setup_router.py — one-time admin setup, downloads models, sets API keys
- full_auto_setup.py — zero-prompt full autonomous setup
- health_check.py — pings all LiteLLM providers, logs latency
- quick_fix.py — patch script (coder model ordering, Unicode fix)
- archive_logs.py — moves session_logs >30 days to archive/
- task_db.json — model router database (task type → model list)

## Bugs Fixed
- None

## Next Priorities
1. Sign up xAI Grok (phone tomorrow) — add GROK_API_KEY to .env
2. Upload v39 to Project Files (replace v38)
3. Execute 5-project split
4. Build MCC redesign (Option A or B — pending decision)
5. Star Citizen full support via AAFL


---
<!-- merged from session_logs/2026-05-19-cc2.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19 (Claude Code session 2)

**Session type:** Claude Code
**Handover:** v40 → v41

## What was built / changed
- v41 handover written (WCCS only session — no new code)
- chat_latest.txt content captured and incorporated into v41 CHAT LOG
- 5 new MCC features documented in handover: Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue
- MCC confirmed as cross-cutting cockpit layer across all 6 projects — added to BIG VISION section
- ALP_Database.md consolidated to 17 entries (from Chat session)
- wccs_log.md updated (row 16 added)
- sfl_agent.py HANDOVER_FILENAME updated to v41
- mcu_optimizer.py run as WCCS step 6

## Bugs fixed
- None

## Next priorities
1. Build merge_sessions.py + .bat (DSP pending)
2. Execute 5-project split + Master project
3. Build 5 new MCC features (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue)
4. Star Citizen v0.2 benchmark via AAFL autonomous run
5. External post when benchmark passes (r/LocalLLaMA primary)


---
<!-- merged from session_logs/2026-05-19-cc3.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19 (Claude Code session 3)

**Version:** v41 → v42
**Date:** 2026-05-19
**Session type:** WCCS only — Chat session capture

---

## What was built / changed

- New handover v42 written (v41 → v42)
- New ACCA code added: CAWPA = Completely Automate Whats Possible by AI
- WCCS Reliability Upgrade documented in handover WCCS Protocol section:
  - Stage 1: Mini-Save Protocol (every ~10 exchanges in Chat, 5-line passive capture)
  - Stage 2: aafl_wccs.py — free LLM (Mistral) writes handover, zero CLAC allowance burn
  - Stage 3: Chrome extension auto-capture (future — fully removes manual trigger)
- Recovery Path added: open new Chat → search past 24h chats → rebuild WCCS summary
- Pre-flight ALP check protocol added to WCCS Protocol section
- aafl_wccs.py added to CURRENT PROJECT STATUS as ⏸ Planned
- aafl_wccs.py added to PROJECT FILES tree as ⏸ Planned
- NEXT PRIORITIES updated: aafl_wccs.py now priority #1
- RESUME COMMAND updated for v42

---

## Bugs fixed

- None

---

## Next priorities

1. Build aafl_wccs.py — AAFL-powered handover writer (CLAC, DSP confirmed required)
2. Build merge_sessions.py + .bat (DSP confirmed required)
3. Execute 5-project split + create Master project
4. Build 5 new MCC features (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue)
5. Star Citizen v0.2 benchmark via AAFL autonomous run (first public demo)
6. External post when benchmark passes (r/LocalLLaMA primary)
7. Stage 3 — Claude in Chrome auto-capture (future)


---
<!-- merged from session_logs/2026-05-19-cc4.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19 (Claude Code session 4 + WCCS)

**Handover:** v42 → v43
**Session type:** Build + WCCS
**Date:** 2026-05-19

---

## What was built this session

### AAFL Control Panel — MCC Tab 7

6 tasks completed autonomously (CA — no prompts):

**Task 1 — aafl_control_config.json**
- Created in project root
- 14 providers with tier (1=local, 2=free, 3=fallback, 99=paid) and status (working/needs_key/blocked)
- All loop settings: active_provider, fallback_providers (array), task_type, max_iterations, max_cost_usd, timeout_seconds, use_chief_scout, use_db_cache, use_meta_loop, current_goal, run_mode

**Task 2 — mcc_server.py extended (10 new endpoints)**
- POST /run-aafl — reads config, writes goal.txt, spawns loop_manager.py --once, streams to aafl_output/latest.txt
- POST /set-aafl-goal — writes goal.txt + updates current_goal in config
- GET /aafl-status — last 50 lines of latest.txt + last DB row (score/provider/cost)
- GET/POST/DELETE /aafl-queue — read/append/comment-out goals in goal_queue.txt
- GET/POST /aafl-config — read/write aafl_control_config.json
- GET /aafl-providers — returns provider_list with tier and status
- POST /stop-aafl — terminates running subprocess
- Added do_DELETE handler to MCCHandler
- CORS updated to include DELETE

**Task 3 — aafl_output/ directory**
- Created aafl_output/ folder
- Added aafl_output/latest.txt empty placeholder
- Added aafl_output/ to .gitignore

**Task 4 — AAFL Control tab in mission_control.html (tab 7)**
- Dark theme matching existing tabs exactly
- Section 1 Goal Control: full-width input + SET GOAL (blue) / RUN ONCE (green) / RUN QUEUE (orange) / STOP (red)
- Section 2 Provider Control: primary dropdown + 3 fallback dropdowns (all 14 providers, colour-coded green/yellow/red by status) + task type 3-way toggle
- Section 3 Loop Settings: max iterations slider (1–20), max cost slider ($0.01–$1.00), timeout slider (30–300s), Chief Scout / DB Cache / Meta Loop boolean toggles
- Section 4 Goal Queue: scrollable list from goal_queue.txt, status badges, remove buttons, add-to-queue input
- Section 5 Live Output: green-on-black terminal, auto-scroll, polls every 2s, last run summary bar
- Section 6 Run History: collapsible rows, deduped by DB id, max 10
- Config loads from server on tab open. Providers colour-coded (green=working, yellow=needs_key, red=blocked). aaflSaveConfig() fires on every control change.

**Task 5 — Smoke test PASS**
- /aafl-config: active_provider=mistral, 14 providers ✅
- /aafl-queue: 12 entries (10 commented, 2 active) ✅
- /aafl-providers: 14 providers with tier + status ✅

**Task 6 — Handover v42 updated**
- AAFL Control tab added to status table, MCC tabs table, endpoints table, PROJECT FILES

---

## Chat session captured (Chief Scout + MCC Mega-Upgrade)

Key decisions captured from chat summary:
- Opus 4.7 pricing confirmed. AI tier strategy = car gears.
- 29-job outstanding list compiled. aafl_wccs.py = Job 1.
- MCC to .exe via Electron — no rewrite needed.
- MCC Mega-Upgrade fully specced (all 6 tabs, AI selector cards, chain builder, provider health dashboard).
- Chief Scout keybind research = primary near-term use case.

---

## Files created / modified

| File | Action |
|---|---|
| aafl_control_config.json | Created |
| aafl_output/latest.txt | Created |
| mcc_server.py | Extended — 10 new endpoints |
| mission_control.html | Extended — AAFL Control tab added |
| .gitignore | Extended — aafl_output/ added |
| VKB_SpinDoctor_Handover_v43.md | Created |
| wccs_log.md | Row 18 added |
| session_logs/2026-05-19-cc4.md | Created (this file) |

---

## Next priorities

1. Build aafl_wccs.py — Job 1, DSP confirmed required
2. Build merge_sessions.py + .bat — DSP confirmed required
3. MCC Mega-Upgrade — one tab at a time
4. Execute 5-project split + Master project
5. Star Citizen v0.2 benchmark via AAFL autonomous run


---
<!-- merged from session_logs/session_2026-05-18_cc4.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18 cc4

**Focus:** Meta-loop, real-data injection fix, mcu_optimizer, MCC design, ACCA codes
**Handover:** v35 → v36

## What was built

- **meta_loop.py** — AAFL self-improving loop. Dry-run default. --apply writes code changes with auto-snapshot + regression test guard.
- **meta_queue.txt** — 3 starter goals. All 3 processed (# DONE).
- **meta_loop.bat** — launcher. Passes extra args through.
- **meta_proposals/** — proposal output dir. 3 proposals written.
- **Real-data injection fixed** — _inject_file_context raised to 600-line cap. _inject_db_context keywords expanded (4 → 14). New _inject_loop_reports() added. Goals 2+3 ran FLAGGED (hallucinated data before fix).
- **mcu_optimizer.py** — reads handover + session logs + board, sends to Mistral, rewrites JSON. Tested: 22s, $0.0058, 0 changes (board already optimal). Wired into WCCS as step 6.
- **MCC (Mission Control Center) designed** — Central Command concept: dashboard_builder.py + upgraded mission_control.html. 4 tabs: Kanban | Activity Feed | AAFL Runs | Costs. Auto-refresh 10s. Mobile-responsive via OneDrive.

## New ACCA codes

- **WRC** = Write-Run-Check (mini dev cycle: write code, run it, check output)
- **MCC** = Mission Control Center

## Bugs fixed

- Cerebras model in aafl_core.py: llama-3.3-70b → gpt-oss-120b
- mcu_optimizer.py: result.cost → result.cost_usd; unicode arrows → ASCII

## Next

Build dashboard_builder.py + upgrade mission_control.html to Central Command (phase 1, 4 panels).


---
<!-- merged from session_logs/session_2026-05-18b.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-18 (Chat session 2)

**Handover:** v31 → v32
**Tool:** Claude Chat (not CLAC)

## What happened

- Mission Statement formalised: 9 rules. ALP (Allowance Preservation) is Rule No.1 — absolute, no exceptions.
- SuperClaude concept defined: if Claude hits 90% ALP, emergency stop fires. Claude only for big-brain tasks.
- AAFL strategy confirmed as workhorse: free providers (Cerebras, Groq, Gemini, Mistral) do heavy lifting. Claude reserved for complex decisions.
- Tasks 5+6 (API keys) locked as always-manual — security rule, no code touches credentials.
- WS conflict resolved: WRS = Write Software. WS stays as Web Search.
- MCU = Mission Control Update — implied ACCA code formalised.
- CLAC block prepared for tasks 1-4: scout fix, Star Citizen AAFL job, run_aafl.bat test, Mission Control open.
- No Mission Control board changes made in this Chat session.

## New ACCA codes
- WRS = Write Software
- MCU = Mission Control Update

## Files changed
- VKB_SpinDoctor_Handover_v32.md — created
- session_logs/session_2026-05-18b.md — this file
- wccs_log.md — row appended
- sfl_agent.py — HANDOVER_FILENAME updated to v32

## Next
1. Paste tasks 1-4 CLAC block
2. Add GROQ_API_KEY to .env manually
3. Add Cloudflare keys to .env manually


---
<!-- merged from session_logs/session_2026-05-19.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19 (Chat — Master Project strategy)

**Session type:** Chat (not Claude Code)
**Handover:** v39 → v40

## Key decisions
- MAJOR REFRAME: AAFL IS the project. Spin Doctor is the benchmark/test subject.
- Master + 5 sub-projects confirmed. Master = weekly boardroom, sub-projects = daily workshops.
- Master open max 2-3x/week. Daily work stays in lean sub-projects.
- merge_sessions.py + .bat (Option 2) chosen — weekly double-click, ~1 min. Not yet built.
- AAFL now competes with LangGraph, CrewAI, AutoGPT (not Joystick Gremlin).
- Star Citizen v0.2 = AAFL's first real public demo/benchmark.
- External posting plan: r/LocalLLaMA, GitHub, HackerNews — trigger = benchmark passes.
- Story angle locked: "beginner with BI builds self-improving AI agent."

## Ideas discussed
- Promotional path = AI/agent dev communities, not flight sim Discords.
- Scott wants to understand what external posting means in practice before committing.
- Session logs = glue between all 6 projects.
- AAFL auto-merge (Option 3) discussed but Scott prefers manual script (Option 2).

## Next priorities
1. Build merge_sessions.py + .bat (CLAC — DSP not yet confirmed)
2. Execute 5-project split + create Master project
3. Star Citizen benchmark via AAFL autonomous run
4. External post when benchmark passes


---
<!-- merged from session_logs/session_2026-05-19_2.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-19

**Handover:** v43 -> v44
**Method:** aafl_wccs.py  |  Provider: openrouter
**Cost:** $0.00000  |  Time: 80.22s

## Chat summary

SESSION: 2026-05-19 01:51 — Pre-split assessment  KEY DECISIONS: - MCC confirmed as cross-cutting layer across ALL projects — cockpit, bidirectional, AAFL-powered - Next 5 MCC features: Stuck Inbox, Run Now button, Cost Predictor, Memory Inspector, Promotion Queue - External posting plan locked: r/LocalLLaMA primary, post when AAFL passes Star Citizen v0.2 - Story angle confirmed: "beginner with BI builds self-improving AI agent" - Comparison set: LangGraph, CrewAI, AutoGPT - merge_sessions.py + .bat: DSP asked, not yet confirmed - ALP memory consolidated: 11 outdated entries removed, 4 Master...

## Files written

- VKB_SpinDoctor_Handover_v44.md
- session_logs/session_2026-05-19_2.md
- wccs_log.md (row appended)
- sfl_agent.py (updated)
- chat_latest.txt (deleted)

---
<!-- merged from session_logs/session_2026-05-20.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-20

**Session type:** Chat session (v44 truncation fix + handover redesign)
**Handover:** v43 → v45 (v44 skipped — confirmed truncated/corrupt)

## Key decisions
- v44 confirmed truncated: 499 lines vs v43's 1,003. Cut off mid-sentence in PROJECT FILES.
- NEVER-DELETE rule established: old handovers archive to archive_dead/ only, never deleted from disk.
- Handover split architecture designed: INDEX.md (~50 lines) + STATUS.md (~200) + HISTORY.md + ACCA.md.
- ALP saving from split: ~73% reduction in pinned context size.
- aafl_wccs.py full build spec written — Mistral writes STATUS.md, atomic write, END_OF_FILE markers, line-count sanity check, auto git commit.
- Design docs ready: handover_split_design.md + aafl_wccs_spec.md.
- Multiple CLAC terminals = ALP-dangerous (shared pool). One at a time.
- Mission statement reconfirmed: 14 rules total.

## New ACCA codes
- CAP = Copy and Paste

## Files changed
- VKB_SpinDoctor_Handover_v45.md — created (new master)
- VKB_SpinDoctor_Handover_v43.md — archived to archive_dead/
- VKB_SpinDoctor_Handover_v44.md — archived to archive_dead/
- sfl_agent.py — HANDOVER_FILENAME updated to v45
- wccs_log.md — entry #20 appended
- session_logs/session_2026-05-20.md — this file

## ALP entries added
None this session.

## Next priorities
1. CLAC session A — migrate v45 to split structure (handover_split_design.md)
2. CLAC session B — build aafl_wccs.py (aafl_wccs_spec.md, DSP required)
3. Execute 5-project split + create Master project
4. Star Citizen v0.2 benchmark via AAFL


---
<!-- merged from session_logs/session_log_2026-05-15.md on 2026-05-20 19:03 -->

# Session Log — 2026-05-15

## Built / Fixed
- Loop Engine first successful run: goal_met, £0.0038, Gemini planned, Mistral coded
- Cerebras model name fixed → llama3.1-70b (was broken)
- cost_guard cap raised: £0.00 → £0.05
- Handover v23 written

## Decisions Made
- session_saver.py is dead — WCCS (Write Claude Code Save) replaces it entirely
- loop_manager.py gap identified: code writes to DB but NOT to disk — file-write step needed (Option A)
- Walk-away mode confirmed: `claude --dangerously-skip-permissions` — exit with `/exit`
- CRITICAL ALP rule: Chat and Claude Code share the same allowance pool. One big task per Claude Code session, not many small ones.

## New ACCA Codes
- WCCS = Write Claude Code Save
- CLAC = Claude Code

## Next Priorities
1. Add file-write step to loop_manager.py (Option A) — code runs but doesn't land on disk
2. Fix HuggingFace model name (still broken)
3. Install LangGraph on Python 3.14
4. Build Memory Bank (SQLite)


---
<!-- merged from session_logs/2026-05-20-cc1.md on 2026-05-24 00:41 -->

# Session Log -- 2026-05-20-cc1

**Handover:** v42 -> v43
**Focus:** WCCS automation run

## Chat Summary (from chat_latest.txt)

SESSION: 20 May 2026 — aafl_watchdog.py built, Star Citizen 8.33/10 autonomous, Scout Control mega-upgrade brainstormed, MCC tabs reorganization discussed, database-backed handover designed as permanent WCCS fix.

JOB #1 NEXT SESSION: Build database-backed handover (handover.db SQLite + migration from v45). CLAC block ready above. This fixes truncation permanently.

ACCA: SBS = Step By Step

NEXT: File cleanup caps (loop_output 50 max), provider keys (Gemini/Mistral dead), MCC Watchdog+Rewind tab, START_MCC.bat rename.

## Generated Chat Log Entry

### 2026-05-20 (Claude Code session 1)
**Key decisions:** Built aafl_watchdog.py and designed database-backed handover as permanent WCCS fix.
**New ACCA codes:** None
**Ideas discussed:** Scout Control mega-upgrade brainstormed, MCC tabs reorganization discussed.
**Bugs fixed:** None
**Next priorities:** 1. Build database-backed handover (handover.db SQLite + migration from v45). 2. File cleanup caps (loop_output 50 max). 3. Provider keys (Gemini/Mistral dead). 4. MCC Watchdog+Rewind tab. 5. START_MCC.bat rename.

## Files written (WCCS)
- VKB_SpinDoctor_Handover_v43.md
- wccs_log.md (row appended)
- 2026-05-20-cc1.md (this file)
- sfl_agent.py HANDOVER_FILENAME updated to v43
- mcu_optimizer.py run
- dashboard_builder.py run


---
<!-- merged from session_logs/2026-05-24-cc1.md on 2026-05-24 21:26 -->

# Session Log — 2026-05-24 (Claude Code session 1)

**Date:** 2026-05-24
**Tool:** Claude Code (CLAC)
**Focus:** MCC 8-fix run + full project audit + housekeeping

---

## What was done

### 1. mcc_server.py — 7 new endpoints wired

Added GET routes:
- `/aafl/live` — returns last 100 lines of aafl_output/latest.txt + parsed phase (plan/work/verify/store/done) + provider name
- `/aafl/bridge-result` — returns aafl_output/bridge_result.json (AAFL↔Scout bridge result)
- `/aafl/workflow-presets` — returns saved workflow presets from aafl_workflow_presets.json

Added POST routes:
- `/aafl/run-goal` — **fixes "Failed to fetch" bug**: sets goal in goal.txt + aafl_control_config.json then actually launches loop_manager.py via `_run_aafl_bg()`. Root cause was old `/run-now` only queued to goal_queue.txt but never launched AAFL.
- `/scout/strategy` — launches individual scout strategy (ddg/reddit/github/youtube/forum/all) via chief_scout.py
- `/aafl/scout-bridge` — runs chief_scout.py for current goal in background, writes result to bridge_result.json
- `/aafl/workflow` — saves/replaces named workflow preset in aafl_workflow_presets.json

Added 7 handler methods: `_handle_aafl_run_goal`, `_handle_aafl_live`, `_handle_scout_strategy`, `_handle_aafl_scout_bridge`, `_handle_aafl_bridge_result`, `_handle_workflow_presets_get`, `_handle_workflow_save`

### 2. mission_control.html — AAFL Control + Scout tab upgrades

**Run Now button fixed:**
- Changed `onclick="runNow()"` → `onclick="runGoalNow()"`. New `runGoalNow()` calls `/aafl/run-goal` — actually launches AAFL instead of just queuing.

**AAFL Live Output panel added (AAFL Control tab):**
- Monospace scrolling output box (last 100 lines)
- Phase badge (plan/work/verify/store/done)
- Provider badge (→ mistral etc.)
- Running indicator (orange dot)
- Refresh + Clear buttons

**AAFL↔Scout Bridge added (AAFL Control tab):**
- "Run Scout for Current Goal" button → POST /aafl/scout-bridge
- "Show Result" button → GET /aafl/bridge-result
- Status pill (idle/running/done/error)

**Workflow Builder added (AAFL Control tab):**
- Step add/remove with provider + task type dropdowns
- Named preset save/load (backed by /aafl/workflow + /aafl/workflow-presets)
- Run Workflow + Stop buttons
- loadWorkflows() called on DOMContentLoaded

**Scout Strategies section added (Scout tab):**
- Goal input field
- 6 buttons: DDG Search / Reddit / GitHub / YouTube / Forum / All Parallel
- Calls POST /scout/strategy with selected strategy
- Results appear in Scout tab (loadScout() called after 3s)

**JS functions added:** `runGoalNow`, `refreshAaflOutput`, `clearAaflChat`, `triggerScoutBridge`, `loadBridgeResult`, `addWorkflowStep`, `removeWorkflowStep`, `_renderWfSteps`, `saveWorkflow`, `loadWorkflows`, `loadWorkflowPreset`, `runWorkflow`, `stopWorkflow`, `runScoutStrategy`

### 3. Auto-refresh polling (earlier this session)
- `pollCoreData()` — 30s interval, fetches /api/status, /api/history, /api/acca, /api/health + calls tab refresh functions
- `manualRefresh()` + ↻ Refresh button in header
- "Last updated: Xs ago" label, updates every 1s
- `_lastPollAt` global, set on init

### 4. mcc_test.py validation
- Run 1: 134/138 PASS | Run 2: 133/138 PASS
- 5 failures all pre-existing timeout endpoints (/run-mot, /api/wccs, /self-diagnosis)
- Above 130/138 threshold — all clear

### 5. Full project audit — docs/PROJECT_AUDIT.md
- Read every file in root + subfolders
- Classified all files: ACTIVE / DEAD / UNKNOWN
- STATUS.md coverage gaps identified (22 missing items)
- ACCA.md completeness checked against full 38-code list
- DESIGN_RULES.md FFUE confirmed correct
- Built-but-not-in-STATUS items listed
- Unactioned HISTORY ideas catalogued

### 6. STATUS.md updated
- 22 missing built items added (mcu_optimizer, wccs_runner, aafl_watchdog, cost_guard, meta_loop, mcc_full_mot, queue_runner, morning_report, provider_health, source_library_manager, docs/MCC_FULL_GUIDE.md, afna_strategies, auto-refresh, AAFL Live Output, Scout Bridge, Workflow Builder, Scout Strategies, /aafl/run-goal, /scout/strategy, preset_manager, and more)
- mcc_server.py entry updated: "10+ endpoints" → "30+ endpoints"
- 13 new pending items added (aafl_watchdog wiring, meta_proposals review, loop_output cap, AFNA→Stuck Inbox, ACCA cleanup, Stage 3 WCCS, Ko-fi/Itch.io, xAI Grok, n8n investigation, dead file archive)

### 7. ACCA.md housekeeping
- **SBS = Step By Step** added (was in HISTORY.md 2026-05-20, never appended until now)
- **Modes moved to table:** TBLM, DDM, BGM, BPM, EM (were in prose line, now proper table rows)
- **FFUE integrated** into table (was stray block at bottom)
- **4 new codes added:** CLACH = Claude Chat | CNP = Copy and Paste | RIBS = Random Inspirational BrainStorm | SESUM = Session Summary
- **CAP duplicate removed:** CAP (Copy and Paste, pre-split) removed — CNP kept as canonical. CAP and CNP had identical meanings.

### 8. 10 dead files archived to archive_dead/
| File | Reason |
|---|---|
| model_router.py | Historical AAFL prototype — flagged for archive May 23, never moved |
| setup_router.py | One-time admin setup, calls dead model_router |
| quick_fix.py | Old patch script — historical |
| control_panel.py | Early prototype — superseded |
| aafl_loop.py | Original AAFLLoop class — fully superseded by aafl_core.py + loop_manager.py |
| full_auto_setup.py | Setup script calling dead model_router.py — DEAD |
| free_providers.py | Provider registry superseded by aafl_core.py PROVIDERS list |
| VKB_SpinDoctor_Handover_v40.md | Stale handover |
| VKB_SpinDoctor_Handover_v41.md | Stale handover |
| VKB_SpinDoctor_Handover_v43.md | Already in archive_dead/ (skipped) |

### 9. 4 UNKNOWN files assessed
| File | Verdict | Notes |
|---|---|---|
| preset_manager.py | ACTIVE | Build 1 Feature 2 — save/load/list/delete presets in presets/ |
| full_auto_setup.py | DEAD → archived | Called model_router.py (dead) |
| free_providers.py | DEAD → archived | Superseded by aafl_core.py PROVIDERS |
| aafl_loop.py | DEAD → archived | Original prototype, fully superseded |

---

## Files changed

| File | Change |
|---|---|
| mcc_server.py | +3 GET routes, +4 POST routes, +7 handler methods |
| mission_control.html | Run Now fixed, +AAFL Live Output, +Bridge, +Workflow Builder, +Scout Strategies, +13 JS functions, +auto-refresh polling |
| docs/PROJECT_AUDIT.md | Created — full audit |
| STATUS.md | +22 built items, +13 pending items, updated mcc_server.py endpoint count |
| ACCA.md | +SBS, +CLACH, +CNP, +RIBS, +SESUM, modes moved to table, FFUE integrated, CAP removed |
| session_logs/2026-05-24-cc1.md | This file |
| archive_dead/ | +model_router.py, setup_router.py, quick_fix.py, control_panel.py, aafl_loop.py, full_auto_setup.py, free_providers.py, v40/v41 handovers |

---

## Bugs fixed

- **Run Now "Failed to fetch"** — runNow() called /run-now which only queued. Fixed: runGoalNow() calls /aafl/run-goal which actually launches loop_manager.py.
- **Stuck Inbox "Load failed"** — was pre-existing; endpoint /stuck-inbox was already working (test confirms HTTP 200).
- **ACCA codes missing from table** — SBS was in HISTORY but never appended. Modes were in prose. All fixed.
- **CAP/CNP duplicate** — CAP removed, CNP kept.

---

## FFUE confirmed
FFUE = Fluid, Flexible, Upgradeable, Editable. Correctly defined in DESIGN_RULES.md. No change needed.

---

## Next priorities

1. Confirm aafl_watchdog.py + cost_guard.py are wired into loop_manager.py (URGENT before overnight run)
2. Read meta_proposals/ (3 AAFL self-improvement proposals from May 18 — never implemented)
3. Build 2 CLAC block (23 parking lot features)
4. Star Citizen v0.2 benchmark via AAFL
5. Add GROQ + Cloudflare keys to .env (manual — security rule)
6. loop_output file cap (35+ files, 50 max planned never built)


---
<!-- merged from session_logs/2026-05-24-cc2.md on 2026-05-24 21:26 -->

# Session Log — 2026-05-24 (Claude Code session 2)

**Date:** 2026-05-24
**Tool:** Claude Code (CLAC)
**Focus:** CAP/CNP duplicate check + WCCS save attempt

---

## What was done

### 1. CAP/CNP duplicate check

Read ACCA.md. CAP was **already removed** in cc1 — no action needed. CNP = Copy and Paste is present and correct. No duplicate found.

### 2. aafl_wccs.py — FAILED (safety check blocked)

Ran: `python aafl_wccs.py`

Result:
- Pre-flight: chat_latest.txt found — OK
- Mistral Codestral: SKIP (timeout)
- LM Studio Coder 32B: returned 9-line STATUS.md (ratio 5% vs prior 193 lines)
- Safety check: refused to write (< 90% length ratio)
- STATUS.md: untouched (restore confirmed)

Root cause: LM Studio returned a near-empty rewrite. Safety guard worked correctly.

### 3. Manual fallback

Written this session log (cc2) and committing via git add -A + git commit as per fallback plan.

---

## Context: cc1 session (same day, earlier)

The bulk of the day's work was completed in cc1 and committed as **8b72b08**. That session covered:
- MCC test suite (138 tests, 133/138 PASS)
- Auto-refresh polling (30s pollCoreData)
- AAFL Control fixes: Run Now fixed, Live Output panel, Workflow Builder, Scout Bridge
- Scout strategies wired (6 buttons, all 5 chief_scout strategies)
- Full project audit → docs/PROJECT_AUDIT.md
- 10 dead files archived to archive_dead/
- 5 ACCA codes added (CLACH/CNP/RIBS/SESUM/SBS)
- Mode codes reformatted to table (TBLM/DDM/BGM/BPM/EM)
- CAP/CNP duplicate resolved (CAP removed, CNP kept)
- FFUE confirmed: Fluid Flexible Upgradeable Editable

---

## Files changed

| File | Change |
|---|---|
| session_logs/2026-05-24-cc2.md | This file — manual fallback WCCS log |

---

## WCCS outcome

aafl_wccs.py failed — LM Studio returned too-short STATUS.md, safety guard blocked write. Manual git commit used as fallback. STATUS.md and HISTORY.md unchanged from cc1 state.

---

## Next priorities

1. **URGENT:** Confirm aafl_watchdog.py + cost_guard.py wired into loop_manager.py before overnight run
2. Read meta_proposals/ (3 AAFL self-improvement proposals, never actioned)
3. Build 2 CLAC block (23 parking lot features B2-01 through B2-23)
4. Star Citizen v0.2 benchmark via AAFL
5. Add GROQ + Cloudflare keys to .env (manual — security rule)
6. loop_output file cap (35+ files, 50 max planned, never built)

---

### 2026-05-28 — OCB-F

**Goal 1 — Arrow Drag-Drop Fix:**
- Root cause: `llowOnDrop` had `if (data.type !== 'element') return;` — silently dropped all arrow palette drags
- Fix: Added arrow handling branch in `llowOnDrop` — arrow drop sets `LLOW.pendingArrowType`
- Added `LLOW.dragPalette` fallback in drop handler for cross-browser safety
- Active arrow type shown in topbar badge (→ Continue); turns orange when non-default type is active
- `llowPortInClick` now uses `pendingArrowType` when creating connections; resets to `continue` after each use
- All 15 arrow types now draggable onto canvas to set connection mode

**Goal 2 — LLOW Colour Strategy Settings:**
- ⚙️ Settings button added to LLOW topbar → slide-in 4th column panel (220px, does not cover canvas)
- Strategy 1 Phase Flow: horizontal blue/white/red gradient bands across full canvas background
- Strategy 2 Element Mirror: vertical column wash per palette category colour (proportional to element count)
- Strategy 3 Snap Glow: invisible category zones pulse-glow when dragging matching category element
- All three toggle independently; blank canvas is default (all off)
- Starter workflow auto-suggest: basic_research → S1, full_dev_cycle → S2, overnight_aafl → S3 (hint text only, never auto-applies)
- New functions: `llowUpdateArrowBadge`, `llowClearArrowType`, `llowOpenSettings`, `llowCloseSettings`, `llowToggleStrategy`, `llowApplyColourStrategies`, `llowSetupSnapZones`, `llowSnapGlowAt`, `llowSnapGlowOff`, `llowOnDragOver`, `llowSuggestStrategy`

**MOT:** 108/108 ALL CLEAR

**Files changed:** mission_control.html

---

## 2026-05-28 — OCB-G: LLOW Full Rebuild

**OCB-G complete. All 4 phases delivered.**

### Phase 1 — CONNECTORS
- Palette section renamed: "Arrow Types" → "CONNECTORS" with updated tooltip
- Per-type line styles for all 15 connector types in `llowRenderArrows()`:
  - Dotted: `timer`, `scheduled`
  - Dashed: `jump_back`, `jump_forward`, `branch`, `alp_gate`, `approval`, `hard_stop`
  - Bold/solid: `repeat`, `trigger`, `ab_split`, `hard_stop`

### Phase 2 — Junction Boxes
- Added `junctions` category to `data/llow_elements.json` with 8 new types:
  Decision, Merge, Split, Gate, Counter, Logger, Router, Delay
- CSS clip-path shapes per type: diamond, trapezoid (up/down), hexagon, circle, pill, octagon
- Special `llow-jb` CSS class + shape subclasses applied at render time
- Double-click popup (`llowDoubleClickJunction`) for Gate/Counter/Router/Delay editable params
- `llowJBSaveEdit()` saves param values back to step
- Props panel shows current options + "Edit Options" button for JB types

### Phase 3 — Preset Load
- Dropdown placeholder renamed "Preset Load…" (HTML + JS)
- 8 new preset workflow JSON files in `data/llow_workflows/`:
  `tutorial_load.json`, `bug_hunt.json`, `alp_audit_run.json`, `scout_deep_dive.json`,
  `morning_report.json`, `meta_improve.json`, `new_project_bootstrap.json`, `star_citizen_benchmark.json`
- `llowSuggestStrategy()` extended to map all 11 presets to suggested strategies

### Phase 4 — Colour Strategy
- Phase Flow now renders 3 visible zone header labels at canvas top:
  "INPUT — Brainstorm, Research, Scout" | "PROCESS — Run, Evaluate, Route" | "OUTPUT — Save, Handover, Report"
- `llowApplyColourStrategies()` now removes `.llow-phase-label` elements on re-render
- Strict Mode 4th toggle added to Settings panel with GOEB tooltip
- `llowToggleStrategy()` handles strict_mode toggle
- `LLOW_ZONE_CATS` map defines which categories belong to input/process/output zones
- `llowGetZoneForX()`, `llowGetZoneForCat()`, `llowFlashWrongZone()` helpers added
- `llowOnDrop()` enforces strict mode: wrong zone = red zone flash + canvas shake + reject with log message
- `colourStrat` object extended with `strict_mode: false`

**MOT:** 108/108 ALL CLEAR

**Files changed:** mission_control.html, data/llow_elements.json, data/llow_workflows/ (+8 files)
