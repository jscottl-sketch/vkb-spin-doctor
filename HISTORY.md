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

<!-- END_OF_FILE -->
