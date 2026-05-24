# STATUS — VKB Spin Doctor
**Last updated:** 2026-05-23 | **Updated by:** aafl_wccs.py
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
| mission_control.html | MCC — 12 tabs, auto-refresh 10s, mobile-responsive |
| mcc_server.py | Bridges MCC HTML to filesystem. 10+ endpoints. |
| data/devices.json | 98 devices with VID/PID lookup |
| AAFL autonomous runs | 4 goals, scores 8.07-9.33, DB cache hit confirmed |
| Regression test | PASS 8.83/10 |
| ALP_Database.md | 17 entries |
| Handover split | INDEX/STATUS/HISTORY/ACCA applied 2026-05-20 |
| aafl_wccs.py | Built 2026-05-20. Permanent WCCS fix. |
| aafl_watchdog.py | Built 2026-05-23. Star Citizen 8.33/10 autonomous. |
| cost_guard.py | Built 2026-05-23. ALP protection layer. |
| handover.db | Database-backed handover. Migration from v45 complete. |
| merge_sessions.py + .bat | Built 2026-05-23 |
| MCC 17 save features | Built 2026-05-23 (Stuck Inbox, Run Now, Cost Predictor, Memory Inspector, Promotion Queue, ACCA Tab, ALP Counter Tab, Keyboard Shortcuts, Undo on Everything, Sunday Auto-Merge, Home Screen, Provider Health Check, Full System Test, Project Audit, 12 Tabs) |
| JSON error fix | Built 2026-05-21 |
| Provider reliability fix | Built 2026-05-23 |
| merge_sessions auto-weekly | Built 2026-05-23 |
| morning_report.md | Built 2026-05-23. Forgotten but working. |
| queue_runner.py | Built 2026-05-23. Forgotten but working. |
| afna_strategies.json | Built 2026-05-23. Stuck Inbox strategies. |

## CURRENT STATUS — PENDING
| Component | Notes |
|---|---|
| Star Citizen full support | Next benchmark — first public AAFL proof |
| Throttle slider in WT | Likely PS5/Xbox conflict — unplug and retry |
| 5-project split | AAFL Engine, VKB Spin Doctor, Mission Control, Promo, ACCA Database + Master |
| Add GROQ_API_KEY to .env | console.groq.com → API Keys |
| Add Cloudflare keys to .env | CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID |
| MCC Watchdog+Rewind tab | Pending Scout Control upgrade |
| START_MCC.bat rename | Pending file cleanup |
| ACCA tab | Built for MCC |
| ASKC definition | Pending clarification |
| ALP Counter Tab RIBS idea | Built for MCC |
| Scout timed runs | Planned |
| 1TB storage | Planned |

## CURRENT STATUS — ARCHIVE
| Component | Notes |
|---|---|
| model_router.py | Archived 2026-05-23. Historical gold. |
| setup_router.py | Archived 2026-05-23. Historical gold. |
| quick_fix.py | Archived 2026-05-23. Historical gold. |
| control_panel.py | Archived 2026-05-23. Historical gold. |

---

## BIG VISION
AAFL IS THE PROJECT NOW. Spin Doctor is the first proof. AAFL competes with LangGraph, CrewAI, AutoGPT. Story angle: beginner with BI builds self-improving AI agent. Target: r/LocalLLaMA when Star Citizen v0.2 benchmark passes.

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
1. Confirm aafl_watchdog.py + cost_guard.py wired into AAFL
2. Read meta_proposals/ — AAFL's own improvement ideas
3. Wire afna_strategies into Stuck Inbox system
4. Archive dead files: model_router, setup_router, quick_fix, control_panel
5. Test provider health check script manually
6. Add GROQ + Cloudflare API keys to .env
7. Star Citizen v0.2 benchmark via AAFL
8. 5-project split (if AAFL passes Star Citizen)
9. r/LocalLLaMA post (trigger = Star Citizen benchmark passes)
10. Define ASKC

---

## WHAT NOT TO DO
- Don't rebuild anything marked built — find the existing file
- Don't add multiple games at once — one game, full test, then next
- Don't commit to GitHub without Scott's explicit decision
- Don't auto-flash firmware — warn and guide only
- Don't rebuild from scratch — extend what exists
- Don't run long loops without cost_guard active
- Don't pass --apply to meta_loop without reading proposal first
- NEVER delete old handover files — move to archive_dead/ instead
- Don't open multiple CLAC terminals at once — shared ALP pool
- Don't use external packages unless absolutely necessary

<!-- END_OF_FILE -->