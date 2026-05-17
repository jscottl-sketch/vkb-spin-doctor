# VKB Spin Doctor — Project Handover v21 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** aafl_core.py CONFIRMED WORKING. 3 online providers live. Infinite Loop Engine + Knowledge Engine designed. CrewAI + LangGraph being installed.
**Last updated:** 15 May 2026
**Consolidates:** v20 + this session

---

## LAST SESSION — 15 May 2026

| | |
|---|---|
| **Confirmed** | aafl_core.py is COMPLETE (21 KB). Dry-run: all 6 task types route correctly. Timeout fix added — skips dead local providers in 5s instead of hanging. |
| **Online providers tested** | Gemini 2.5 Flash ✅, Mistral Codestral ✅, OpenRouter Auto ✅. Cerebras ❌ (model name outdated — fix pending). HuggingFace ❌ (model renamed — fix pending). Groq ❌ (no key). |
| **Designed** | Infinite Loop Engine (8 components). Knowledge Engine database schema (saved as Knowledge_Engine_Schema_v1.md). Researcher component (web trawling agent). |
| **Research** | Multi-agent orchestration frameworks: CrewAI, LangGraph, Smolagents, AutoGen, Google ADK. CrewAI needs Python <3.14 (won't work on 3.14.4). LangGraph supports 3.14. |
| **Installing** | Python 3.13 + CrewAI (in venv, for future use). LangGraph on Python 3.14 (next). |
| **Mission** | "Software of Everything" — Knowledge Engine is the universal brain. Every component reads/writes to it. Project-agnostic. |
| **Decisions** | Keep building custom aafl_core.py (option 4). Steal CrewAI's YAML config idea without the dependency. LangGraph as orchestration framework for later. |
| **Blockers** | Cerebras + HuggingFace model names need updating. LangGraph install not done yet. CrewAI install in progress. |

---

## WHO IS SCOTT — READ THIS FIRST

- **Brain injury (BI) 2023** — ONE STEP AT A TIME. No exceptions.
- **Beginner with code** — explain what is being built as you go
- **Always expand acronyms** on first use
- **Always include keyboard shortcuts inline**
- **Tables preferred** for structured info
- **Number all options** — Scott replies with just a number
- **No bullshit** — if something is hard or slow, say so upfront

---

## ACCA CODE

| Code | Meaning |
|---|---|
| DRR | Don't require response |
| DWR | Don't want response |
| YO | Scott asking for Claude's opinion |
| AIO | Claude giving its AI opinion |
| SIB | Summarise in brief |
| SIF | Summarise in full |
| CR | Confidence rating 1-10 |
| WMBW | Why might be wrong |
| WCBB | What could be better |
| NRM | No-repeat mode |
| BI | Brain injury |
| SFL | Screenshot Feedback Loop |
| AAFL | AI Agent Feedback Loop |
| ALP | Allowance Preservation |
| CA | Completely Automate |
| WS | Web Search |
| WSF | Web Search Finding |
| WYM | What You Mean |
| + | Combine codes |
| = | Define a new code |

**Modes:** TBLM (Troubleshoot), DDM (Deep Dive), BGM (Beginner), BPM (Battle Plan), NRM (No-repeat), EM (Evidence)
**Retired:** SL → replaced by SFL

---

## MISSION STATEMENT (locked in)

1. **ALP is RULE NO 1. Absolute king.** Everything passes through this filter — no hesitation, no shortcuts. Applies across chat, code, co-work, and any Anthropic product. Cost must never exceed return.
2. **BIG AAFL masterminds original mission.** Everything goes through ALP.
3. **ACCA Code** — byproduct, organised later in own project. Save to database whenever mentioned.
4. **Spin Doctor VKB** — last on list. AAFL builds it.
5. **Promotional** — proof of concept first. Every penny earned goes back into Claude.
6. **Fluid and flexible.** Works across projects, programs, software. Simple but effective.
7. **Could be bigger platform.** Not building yet — keeping door open.

**The loop:** Free engine → builds product → earns → funds upgrades → Claude pays for itself.
**If it costs nothing:** fun, like playing a game, but not worth paying extra.
**If it generates:** really interesting. Top tier of everything until fully owned.

---

## CURRENT STATUS

| Component | Status |
|---|---|
| v0.1 spin fix — War Thunder | ✅ |
| usb_power_saver.py | ✅ |
| steam_input_conflict.py | ✅ |
| core/win_compat.py | ✅ |
| data/devices.json (98 VID/PID) | ✅ |
| Universal_Input_Device_Database.md (44 problems) | ✅ |
| problems/conductor.py (619 lines, 22 problems) | ✅ |
| spin_doctor.py — 3 tabs (Fix/Conductor/KB) | ✅ ~1057 lines |
| sfl_agent.py v3 | ✅ 39 KB (updated by Claude Code) |
| Claude Code v2.1.142 | ✅ |
| model_router.py | ✅ |
| control_panel.py | ✅ |
| free_providers.py — 13 providers | ✅ (being replaced by LiteLLM) |
| **aafl_core.py — AAFL spine on LiteLLM** | ✅ CONFIRMED WORKING 15/05/2026 |
| aafl_loop.py (old) | ✅ Replaced by aafl_core.py |
| session_saver.py v2 | ✅ Built (not yet tested) |
| SAVE_SESSION_NOW.bat | ✅ |
| SAVE_SESSION_HOTKEY.ahk | ✅ (needs AutoHotkey) |
| LiteLLM + python-dotenv | ✅ Installed and working |
| Knowledge_Engine_Schema_v1.md | ✅ Saved to project folder |
| Python 3.13 | ⏳ Installing alongside 3.14 |
| CrewAI (in 3.13 venv) | ⏳ Installing — future use only |
| LangGraph (on 3.14) | ❌ Not installed yet |

---

## ONLINE PROVIDER STATUS (tested 15/05/2026)

| Provider | Key? | Result | Speed | Notes |
|---|---|---|---|---|
| Gemini 2.5 Flash | ✅ | ✅ OK | 0.87s | Working |
| Mistral Codestral | ✅ | ✅ OK | 0.49s | Working — fastest |
| OpenRouter Auto | ✅ | ✅ OK | 2.21s | Working — slowest |
| Cerebras Llama 3.3 70B | ✅ | ❌ FAIL | 0.59s | Model name changed — fix needed |
| HuggingFace Llama Vision | ✅ | ❌ FAIL | 0.87s | Model renamed — fix needed |
| Groq Llama / DeepSeek | ❌ | ⏸️ SKIP | — | No GROQ_API_KEY in .env |

---

## aafl_core.py — CONFIRMED WORKING

21 KB, self-test passed. Timeout fix applied (5s local, 30s online).

| Feature | Status |
|---|---|
| LiteLLM backbone | ✅ |
| Tiered routing (local → free → paid) | ✅ |
| All 6 task types route correctly | ✅ |
| Timeout handling (skip dead providers) | ✅ Fixed this session |
| ALP enforcement (paid blocked) | ✅ |
| Dry-run mode | ✅ |
| Cost tracker | ✅ |
| Error log (aafl_log.txt) | ✅ |
| Verify hook (stub) | ✅ |
| Project-agnostic | ✅ |

---

## INFINITE LOOP ENGINE — DESIGNED (NOT BUILT)

8-component system that runs for days on RTX 5090 at ~40p/day electricity.

| # | Component | Job | Built? |
|---|---|---|---|
| 1 | Goal Gate | Scott defines "done" | ❌ |
| 2 | Planner | Breaks goal into tasks | Partial (sfl_agent.py) |
| 3 | Researcher | Searches internet for context (DuckDuckGo, £0) | ❌ |
| 4 | Worker | Executes tasks via AAFL routing | ⏳ (aafl_core.py) |
| 5 | Evaluator | Scores output | ❌ |
| 6 | Memory Bank | Stores every attempt + score (SQLite) | ❌ |
| 7 | Reflector | Reads history, adjusts approach | ❌ |
| 8 | Loop Manager | Orchestrates, enforces ALP, kill switch | ❌ |

Safety rails: kill switch (Ctrl+C or STOP file), hard budget cap, max iterations cap, Scott-approval gate, stagnation detector, progress log.

---

## KNOWLEDGE ENGINE — DESIGNED (NOT BUILT)

"Software of Everything" — universal database. Schema saved in Knowledge_Engine_Schema_v1.md.

| Layer | Tech | Cost |
|---|---|---|
| Structured data | SQLite | £0 |
| Semantic search | ChromaDB | £0 |
| Embeddings | Local model on RTX 5090 | £0 |
| Web search | DuckDuckGo | £0 |
| Summarisation | Local LLM | £0 |
| UI | Streamlit on localhost | £0 |

7 tables: knowledge, tags, loop_runs, research_jobs, acca_codes, devices, cost_log.
Research rules in YAML per enquiry (topic, filters, quality, depth, rate limits, stop conditions).

---

## MULTI-AGENT FRAMEWORKS — RESEARCHED

| Framework | Python 3.14? | Best for | ALP |
|---|---|---|---|
| CrewAI | ❌ Needs <3.14 | Role-based teams, YAML config, easiest to learn | £0 |
| LangGraph | ✅ Supports 3.14 | Graph-based workflows, state management, production-grade | £0 |
| Smolagents (HuggingFace) | ✅ | Code-first, data/code tasks | £0 |
| AutoGen (Microsoft) | ✅ | Research, conversational agents | £0 |

Decision: Install both CrewAI (Python 3.13 venv) and LangGraph (Python 3.14). Learn later.

---

## API KEYS — ALL IN .env

| Provider | In .env | Type |
|---|---|---|
| Anthropic | ✅ | Credits |
| Gemini | ✅ | Permanent free |
| Cohere | ✅ | Permanent free |
| HuggingFace | ✅ | Permanent free |
| OpenRouter | ✅ | Permanent free |
| Mistral | ✅ | Permanent free |
| Cerebras | ✅ | Permanent free |
| Cloudflare | ❌ | Needs re-login to dash.cloudflare.com |
| Groq | ❌ | Auth broken — skip |

.env location: C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\.env

---

## CLAUDE CODE STATUS

- Version: v2.1.142
- Auth: claude.ai subscription (jscottl@hotmail.co.uk) ✅
- NOT API billing ✅
- ALP: £0 per task ✅
- To open: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor then type: claude

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | How | Status |
|---|---|---|---|
| 1 | **Fix Cerebras + HuggingFace model names** | Claude Code: "Yes fix the Cerebras and HuggingFace model names" | Not done |
| 2 | **Finish CrewAI install** | Let current Claude Code session complete | ⏳ In progress |
| 3 | **Install LangGraph on Python 3.14** | Claude Code: pip install langgraph --break-system-packages | Not done |
| 4 | **Wire aafl_core.py into sfl_agent.py** | Claude Code | Not done |
| 5 | **Build Memory Bank (SQLite)** | Foundation for Infinite Loop Engine | Not done |
| 6 | **Build Evaluator** | Scores output — "does the code run?" | Not done |
| 7 | **Build Researcher** | DuckDuckGo + local LLM summariser | Not done |
| 8 | **Build Loop Manager** | Ties everything together | Not done |
| 9 | **Test one overnight loop** | Proof of concept | Not done |

---

## 5 SISTER PROJECTS

| # | Project | Priority | Status |
|---|---|---|---|
| 1 | ALP (Allowance Preservation) | **#1 ALWAYS — RULE NO 1** | Active — all builds £0 |
| 2 | BIG AAFL (AI Agent Feedback Loop) | #2 | aafl_core.py ✅, Loop Engine designed |
| 3 | ACCA Code (database of shortcodes) | Byproduct | Growing naturally |
| 4 | Spin Doctor VKB (the actual product) | Last — AAFL builds it | On hold |
| 5 | Promotional (monetisation) | After proof of concept | Not started |

---

## KEY FILES

| File | Size | Purpose |
|---|---|---|
| aafl_core.py | 21 KB | AAFL spine — CONFIRMED WORKING |
| sfl_agent.py | 39 KB | Agent orchestrator |
| spin_doctor.py | 47 KB | Main app — 3 tabs |
| conductor.py | ~20 KB | 22 problems engine |
| control_panel.py | 30 KB | Control panel |
| free_providers.py | 4 KB | Being replaced by LiteLLM |
| model_router.py | 19 KB | Model routing |
| Knowledge_Engine_Schema_v1.md | 10 KB | Database schema for everything |
| .env | 1 KB | All API keys |

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
