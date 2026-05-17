# VKB Spin Doctor — Project Handover v22 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** aafl_core.py CONFIRMED WORKING. 3 online providers live. Infinite Loop Engine + Knowledge Engine designed. CrewAI installing. LangGraph next.
**Last updated:** 15 May 2026 (late evening)
**Consolidates:** v21 + full session updates

---

## LAST SESSION — 15 May 2026

| | |
|---|---|
| **Confirmed** | aafl_core.py is COMPLETE (21 KB). Dry-run: all 6 task types route correctly. Timeout fix added — skips dead local providers in 5s instead of hanging forever. |
| **Online providers tested** | Gemini 2.5 Flash ✅ (0.87s), Mistral Codestral ✅ (0.49s), OpenRouter Auto ✅ (2.21s). Cerebras ❌ (model name outdated). HuggingFace ❌ (model renamed). Groq ❌ (no key). |
| **Fix queued** | "Yes fix the Cerebras and HuggingFace model names" pasted into Claude Code — waiting to execute after CrewAI install finishes. |
| **Designed** | Infinite Loop Engine (8 components — Goal Gate, Planner, Researcher, Worker, Evaluator, Memory Bank, Reflector, Loop Manager). Knowledge Engine database schema v1 (7 SQLite tables + ChromaDB). Researcher component (DuckDuckGo + local LLM summariser, YAML rules per enquiry). |
| **Knowledge Engine Schema** | ✅ Saved as Knowledge_Engine_Schema_v1.md in project folder. "Software of Everything" — universal brain. Every component reads/writes here. Project-agnostic. |
| **Research** | Multi-agent frameworks: CrewAI (needs Python <3.14), LangGraph (supports 3.14), Smolagents, AutoGen. CrewAI uses LiteLLM naming (already installed). LangGraph v1.1.x has Python 3.14 support. |
| **Installing** | Python 3.13 ✅ installed alongside 3.14. CrewAI venv created at C:\Users\jscot\OneDrive\Desktop\crewai-env. CrewAI pip install ⏳ running. LangGraph ❌ not yet installed. |
| **Python paths** | 3.14: C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe — 3.13: C:\Users\jscot\AppData\Local\Programs\Python\Python313\python.exe |
| **Key discoveries** | `python` command fails in PowerShell — must use full path (Windows App Execution Alias intercepts). LM Studio was running but no models loaded — timeout fix handles this gracefully. |
| **Mission evolved** | "Software of Everything" — the Knowledge Engine is the universal brain, not just for VKB. Researcher can trawl internet for days at £0. Database + beautiful UI for all future projects. |

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
| sfl_agent.py v3 | ✅ 39 KB |
| Claude Code v2.1.142 | ✅ |
| model_router.py | ✅ |
| control_panel.py | ✅ |
| free_providers.py — 13 providers | ✅ (being replaced by LiteLLM) |
| **aafl_core.py — AAFL spine on LiteLLM** | ✅ CONFIRMED WORKING — timeout fix applied |
| aafl_loop.py (old) | ✅ Replaced by aafl_core.py |
| session_saver.py v2 | ✅ Built (not yet tested) |
| LiteLLM + python-dotenv | ✅ Installed and working |
| Knowledge_Engine_Schema_v1.md | ✅ Saved to project folder |
| Python 3.13 | ✅ Installed |
| CrewAI (in 3.13 venv) | ⏳ pip install running at session end |
| LangGraph (on 3.14) | ❌ Not installed yet |

---

## ONLINE PROVIDER STATUS (tested 15/05/2026)

| Provider | Key? | Result | Speed | Notes |
|---|---|---|---|---|
| Gemini 2.5 Flash | ✅ | ✅ OK | 0.87s | Working |
| Mistral Codestral | ✅ | ✅ OK | 0.49s | Working — fastest |
| OpenRouter Auto | ✅ | ✅ OK | 2.21s | Working — slowest |
| Cerebras Llama 3.3 70B | ✅ | ❌ FAIL | 0.59s | Model name changed — FIX QUEUED in Claude Code |
| HuggingFace Llama Vision | ✅ | ❌ FAIL | 0.87s | Model renamed — FIX QUEUED in Claude Code |
| Groq | ❌ | ⏸️ SKIP | — | No GROQ_API_KEY in .env |

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

8-component system. Runs for days on RTX 5090 at ~40p/day electricity. "Like machine learning but with memory instead of weight updates."

| # | Component | Job | Built? |
|---|---|---|---|
| 1 | Goal Gate | Scott defines "done" before loop starts | ❌ |
| 2 | Planner | Breaks goal into subtasks | Partial (sfl_agent.py) |
| 3 | Researcher | Searches internet for context (DuckDuckGo, £0). Triggers upfront + when stuck. YAML rules per enquiry. | ❌ |
| 4 | Worker | Executes tasks via AAFL routing | ⏳ (aafl_core.py) |
| 5 | Evaluator | Scores output — "does it work?" | ❌ |
| 6 | Memory Bank | Stores every attempt + score (SQLite + ChromaDB) | ❌ |
| 7 | Reflector | Reads history, adjusts approach for next try | ❌ |
| 8 | Loop Manager | Orchestrates cycle, enforces ALP, kill switch | ❌ |

How it learns: every attempt scored + stored. Reflector reads last N attempts, picks best approach. Over hundreds of iterations overnight, converges. Evolution, not training.

Safety rails: kill switch (Ctrl+C or STOP file), hard budget cap, max iterations cap, Scott-approval gate, stagnation detector (stop if score hasn't improved in N cycles), progress log.

Morning report: iterations, best score, best approach, files created, cost, waiting for Scott approval.

---

## KNOWLEDGE ENGINE — DESIGNED (NOT BUILT)

"Software of Everything" — universal brain. Schema: Knowledge_Engine_Schema_v1.md.

| Layer | Tech | Cost |
|---|---|---|
| Structured data | SQLite (7 tables: knowledge, tags, loop_runs, research_jobs, acca_codes, devices, cost_log) | £0 |
| Semantic search | ChromaDB (2 collections: knowledge_vectors, research_vectors) | £0 |
| Embeddings | Local model on RTX 5090 (nomic-embed-text via LM Studio) | £0 |
| Web search | DuckDuckGo (pip install duckduckgo-search, no API key) | £0 |
| Summarisation | Local LLM on RTX 5090 | £0 |
| UI | Streamlit on localhost (beautiful, searchable, filterable) | £0 |

Design principles: everything is a knowledge entry, tags make it flexible, two layers (SQLite + ChromaDB), every component reads/writes here, project-agnostic, research rules in YAML.

Build order: Database first → Researcher second → Rules system third → UI last.

---

## STANDALONE RESEARCHER — DESIGNED (NOT BUILT)

Can run for days/weeks autonomously. Give it a topic + rules, walk away.

Free search options (ALP ranked): DuckDuckGo (£0, no key), Brave (2k/month free), SearXNG (self-hosted), Tavily (1k/month free), Google (100/day free).

Rate limited: 1 request per 10 seconds = 8,600 pages/day. Rotates search engines. Stores summaries only. Quality scored 1-10, below 5 discarded. ChromaDB deduplication (>90% similar = skip).

YAML rules per enquiry: topic, subtopics, domain filters, date range, quality threshold, depth, rate limits, stop conditions.

---

## MULTI-AGENT FRAMEWORKS — RESEARCHED

| Framework | Python 3.14? | Best for | Status |
|---|---|---|---|
| CrewAI | ❌ Needs <3.14 | Role-based teams, YAML config | ⏳ Installing in Python 3.13 venv |
| LangGraph | ✅ v1.1.x supports 3.14 | Graph-based workflows, state management | ❌ Install next |
| Smolagents | ✅ | Code-first, data/code tasks | Not installed |
| AutoGen | ✅ | Research, conversational agents | Not installed |

Decision: Install both. Neither used yet — learn later. Steal CrewAI's YAML config pattern for aafl_core.py without the dependency.

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
- **Python command fails in PowerShell** — always use full path
- **Python 3.14 path:** C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe
- **Python 3.13 path:** C:\Users\jscot\AppData\Local\Programs\Python\Python313\python.exe
- **CrewAI venv:** C:\Users\jscot\OneDrive\Desktop\crewai-env

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | How | Status |
|---|---|---|---|
| 1 | **Check CrewAI install finished** | Open Claude Code, check output | ⏳ Was installing at session end |
| 2 | **Check Cerebras + HuggingFace fix applied** | Was queued in Claude Code | ⏳ Was queued at session end |
| 3 | **Install LangGraph on Python 3.14** | Claude Code: use full Python path, pip install langgraph --break-system-packages | Not done |
| 4 | **Wire aafl_core.py into sfl_agent.py** | Claude Code | Not done |
| 5 | **Build Memory Bank (SQLite)** | Foundation for Loop Engine + Knowledge Engine | Not done |
| 6 | **Build Evaluator** | Scores output — "does the code run?" | Not done |
| 7 | **Build Researcher** | DuckDuckGo + local LLM summariser + YAML rules | Not done |
| 8 | **Build Loop Manager** | Ties everything together | Not done |
| 9 | **Test one overnight loop** | Proof of concept on RTX 5090 | Not done |

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
| model_router.py | 19 KB | Model routing |
| Knowledge_Engine_Schema_v1.md | 10 KB | Database schema — SOFTWARE OF EVERYTHING |
| .env | 1 KB | All API keys |

---

## IMPORTANT NOTES FOR NEXT SESSION

1. **Python command:** Never use `python` in PowerShell. Always use full path.
2. **LM Studio:** Doesn't need to be running for testing. Close to save GPU. Only open for overnight loops.
3. **CrewAI venv:** Separate from main Python. Activate: `C:\Users\jscot\OneDrive\Desktop\crewai-env\Scripts\Activate.ps1`
4. **aafl_core.py replaces aafl_loop.py** — always use aafl_core.py, never the old one.
5. **Knowledge Engine Schema** must stay in project folder — every future component references this structure.
6. **Everything we build must have the Knowledge Engine in mind** — one brain for all projects.

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
