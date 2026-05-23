# STATUS — VKB Spin Doctor
**Last updated:** 2026-05-23 | **Updated by:** WCCS Recovery
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
| mission_control.html | MCC — 19+ tabs, JS audit complete, zero missing functions |
| mcc_server.py | Bridges MCC HTML to filesystem. 10+ endpoints. |
| data/devices.json | 98 devices with VID/PID lookup |
| AAFL autonomous runs | 4 goals, scores 8.07-9.33, DB cache hit confirmed |
| Regression test | PASS 8.83/10 |
| ALP_Database.md | 17 entries |
| Handover split | INDEX/STATUS/HISTORY/ACCA applied 2026-05-20 |
| aafl_wccs.py | Built 2026-05-20. Permanent WCCS fix. |
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

## CURRENT STATUS — PENDING
| Component | Notes |
|---|---|
| merge_sessions.py + .bat | Built — DSP required to run |
| Star Citizen full support | Next benchmark — first public AAFL proof |
| Throttle slider in WT | Likely PS5/Xbox conflict — unplug and retry |
| 5-project split | AAFL Engine, VKB Spin Doctor, Mission Control, Promo, ACCA Database + Master |
| Add GROQ_API_KEY to .env | console.groq.com → API Keys |
| Add Cloudflare keys to .env | CLOUDFLARE_API_KEY + CLOUDFLARE_ACCOUNT_ID |
| **Build 2 — Parking Lot (23 features)** | CLAC block pending — next session |
| B2-01: Kanban task dependencies + sub-tasks | Kanban tab |
| B2-02: Kanban templates + bulk actions + auto-archive | Kanban tab |
| B2-03: Activity Feed — all 12 filters + AI summarise + export | Activity tab |
| B2-04: AAFL Runs — compare mode + failure analysis + success patterns | AAFL Runs tab |
| B2-05: AAFL Runs — tag/notes on runs | AAFL Runs tab |
| B2-06: AAFL Control — step-by-step + pause mode | AAFL Control tab |
| B2-07: AAFL Control — chain builder + notification settings | AAFL Control tab |
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
1. Test aafl_wccs.py — run: python aafl_wccs.py --dry-run
2. Build merge_sessions.py + .bat (DSP required)
3. Build 2 CLAC block (23 parking lot features)
4. Star Citizen v0.2 benchmark via AAFL autonomous run
5. Add GROQ + Cloudflare keys to .env (manual — security rule)
6. Post on r/LocalLLaMA when Star Citizen benchmark passes

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
