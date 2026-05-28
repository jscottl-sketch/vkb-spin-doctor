# CLAUDE.md — VKB Spin Doctor / AAFL / AASKC Project Orientation

## What This Project Is

**AAFL** (AI Agent Feedback Loop) is a self-improving AI agent framework built by Scott (beginner coder, brain injury 2023).
**Spin Doctor** is the first proof-of-concept: it fixes joystick mouse-spin in War Thunder, Elite Dangerous, Star Citizen.
**AASKC** (Autonomous AI Simultaneous Knowledge Connection) is the product brand for the full platform.

## Working With Scott

- Brain injury (BI) 2023 — ONE STEP AT A TIME. Never stack steps.
- Beginner with code — explain what's being built as you go.
- Always expand acronyms on first use.
- Number all options — Scott replies with just a number.
- DSP rule — before any CLAC block, ask: "DSP? (claude --dangerously-skip-permissions)"
- WCCS triggered automatically — never ask.

## Key Files

| File | Purpose |
|---|---|
| `mission_control.html` | MCC — 19+ tabs, main UI (served by mcc_server.py at localhost:8080) |
| `mcc_server.py` | HTTP server (port 8080), 30+ REST endpoints |
| `aafl_core.py` | 14-provider AI routing spine (LiteLLM) |
| `loop_manager.py` | Plan-Work-Verify-Store loop engine |
| `system_monitor.py` | CPU/RAM/GPU/Disk monitoring |
| `STATUS.md` | Single source of truth — what's built and what's pending |
| `HISTORY.md` | Full build history log |
| `data/knowledge_engine.db` | SQLite — knowledge, solution_log, source_reputation |
| `data/project_awareness.json` | Auto-built from STATUS.md — project snapshot |
| `data/aafl_error_db.json` | Provider error log (max 500 entries) |

## Architecture

```
User → mission_control.html (browser)
         ↕ REST (localhost:8080)
       mcc_server.py
         ↕ Python
       aafl_core.py → LiteLLM → Providers (LM Studio / Cerebras / Mistral / Gemini / OpenRouter / Claude)
         ↕
       loop_manager.py → evaluator.py → memory_bank.py → knowledge_engine.db
```

## Provider Tiers

- **Tier 1** (local): LM Studio (Coder 32B, VL 32B, DeepSeek R1, Phi-4 14B) — free, unlimited
- **Tier 2** (free online): Cerebras, Groq, Gemini, Mistral, Cloudflare
- **Tier 3** (fallback): OpenRouter, HuggingFace
- **Tier 99** (paid, blocked by default): Claude Sonnet

## Running

```bash
python mcc_server.py          # Start MCC server (port 8080)
python mcc_full_mot.py        # Run 108-check MOT test suite
python system_monitor.py      # Standalone resource monitor
python provider_health.py     # Check all AI providers
```

## ACCA Shorthand Codes (key ones)

| Code | Meaning |
|---|---|
| AAFL | AI Agent Feedback Loop |
| MCC | Mission Control Center |
| LLOW | Loop Logic Orchestration Workspace |
| WCCS | Write Claude Code Save |
| STORM | Selective Targeted Output Remove Merge |
| AASKC | Autonomous AI Simultaneous Knowledge Connection |
| OCB | Operation Code Build (e.g. OCB-L = current build) |
| CLAC | Claude Code CLI invocation block |
| DSP | --dangerously-skip-permissions flag |
| ALP | Allowance Preservation (budget rule #1) |

## Current Build

OCB-L — 7 phases: System monitor fix, AI status bar overhaul, drill-down panels, Help tab, Settings persistence.
MOT target: 108/108.

## Do NOT

- Touch `backups/` or `archive_dead/` — dead code, ignore
- Run anything with `allow_paid=True` without confirming with Scott
- Wipe `data/knowledge_engine.db` or `data/aafl_error_db.json`
- Skip WCCS after any OCB — always save
