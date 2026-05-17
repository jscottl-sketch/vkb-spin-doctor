# VKB Spin Doctor — Project Handover v23

**Owner:** Scott (Croydon, England)
**Status:** Loop Engine FIRST SUCCESSFUL RUN. WCCS replaces session_saver. Critical ALP discovery: Chat + Claude Code share the same bucket.
**Last updated:** 15 May 2026 (night)
**Consolidates:** v22 + session updates

---

## LAST SESSION — 15 May 2026 (night)

| | |
|---|---|
| **Loop Engine first run** | goal_met ✅ Cost: £0.0038. Gemini planned, Mistral coded. PROOF OF CONCEPT WORKS. |
| **loop_manager.py gap** | Code is written and goes to database — but NOT saved to disk. File-writing step missing. Option A chosen: add file-write step to loop_manager.py. NOT YET DONE. |
| **Cerebras fixed** | Model name corrected to `llama3.1-70b` for live calls. Now working. |
| **cost_guard cap raised** | From £0.00 → £0.05 to allow real test runs. |
| **WCCS confirmed** | Write Claude Code Save — replaces session_saver.py entirely. session_saver.py is unnecessary, do not use. |
| **Walk-away mode** | `claude --dangerously-skip-permissions` — Claude Code runs without prompting. Exit with `/exit`. |
| **CRITICAL ALP DISCOVERY** | Chat and Claude Code share THE SAME allowance pool. Claude Code costs £0 money but burns message quota from the same bucket as Chat. Give Claude Code ONE big task, not many small ones. |
| **New ACCA codes** | WCCS = Write Claude Code Save. CLAC = Claude Code. |

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
| WCCS | Write Claude Code Save (replaces session_saver.py) |
| CLAC | Claude Code |
| + | Combine codes |
| = | Define a new code |

**Modes:** TBLM (Troubleshoot), DDM (Deep Dive), BGM (Beginner), BPM (Battle Plan), NRM (No-repeat), EM (Evidence)
**Retired:** SL → SFL. session_saver.py → WCCS.

---

## MISSION STATEMENT (locked in)

1. **ALP is RULE NO 1.** Everything passes through this filter. Cost must never exceed return.
2. **BIG AAFL masterminds original mission.** Everything goes through ALP.
3. **ACCA Code** — byproduct, organised later in own project. Save to database whenever mentioned.
4. **Spin Doctor VKB** — last on list. AAFL builds it.
5. **Promotional** — proof of concept first. Every penny earned goes back into Claude.
6. **Fluid and flexible.** Works across projects, programs, software.
7. **Could be bigger platform.** Not building yet — keeping door open.

**The loop:** Free engine → builds product → earns → funds upgrades → Claude pays for itself.

---

## CURRENT STATUS

| Component | Status |
|---|---|
| aafl_core.py (21 KB) | ✅ CONFIRMED WORKING. Timeout fix. Tiered routing. |
| loop_manager.py | ✅ Runs. Goal_met on first try. **GAP: no file-write step — code goes to DB, not disk.** |
| Cerebras model name | ✅ Fixed → llama3.1-70b |
| cost_guard cap | ✅ Raised to £0.05 |
| cost_guard.py | ✅ Built (135 lines, all 3 brakes fire) |
| memory_bank.py | ✅ Built (190 lines, SQLite, self-test passed) |
| session_saver.py | ❌ Unnecessary — replaced by WCCS |
| LiteLLM + python-dotenv | ✅ |
| sfl_agent.py v3 | ✅ 39 KB |
| spin_doctor.py | ✅ ~1057 lines, 3 tabs |
| Knowledge_Engine_Schema_v1.md | ✅ Saved |
| Python 3.13 | ✅ Installed |
| CrewAI (3.13 venv) | ✅ Installed (verify) |
| LangGraph (3.14) | ❌ Not installed yet |
| Memory Bank (SQLite) | ✅ Done — memory_bank.py built |
| Evaluator | ❌ Not built |
| Researcher | ❌ Not built |

---

## ONLINE PROVIDER STATUS

| Provider | Key? | Result | Notes |
|---|---|---|---|
| Gemini 2.5 Flash | ✅ | ✅ OK | 0.87s |
| Mistral Codestral | ✅ | ✅ OK | 0.49s — fastest |
| OpenRouter Auto | ✅ | ✅ OK | 2.21s |
| Cerebras llama3.1-70b | ✅ | ✅ Fixed | Model name corrected this session |
| HuggingFace | ✅ | ❌ | Model renamed — still needs fix |
| Groq | ❌ | ⏸️ SKIP | No API key |

---

## CLAUDE CODE — ALP RULES (NEW)

- **Walk-away mode:** `claude --dangerously-skip-permissions` — no prompts, runs solo. Exit: `/exit`
- **CRITICAL:** Chat and Claude Code share the SAME allowance pool. Claude Code burns Chat quota.
- **Rule:** Give Claude Code ONE big task per session. Not 10 small ones. Batch everything.
- To open: `cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor` then `claude`
- **Sonnet not Opus** — Sonnet gives 3-5x more messages for same allowance. Only use Opus for complex reasoning.
- **Max 1-2 screenshots per message** — images eat thousands of tokens each. Describe the rest in words.
- **New chat for new topics** — long chats cost more per message. Start fresh when switching subjects.
- **Combine questions** — 3 short messages cost more than 1 combined message.
- **Remove old handovers from Project Files** — keep only the latest. Old ones load and burn tokens every message.
- **Extended Thinking off for simple tasks** — toggle off in model selector unless doing complex reasoning.
- **WCCS (updated):** `Read chat_latest.txt in this folder. Compare it against the existing handover and ALP_Database.md. Update ONLY the sections that have new information — do not rewrite anything else. Add new ALP savings to ALP_Database.md. Write a session log under 30 lines in session_logs/ summarizing what changed. Delete chat_latest.txt when done.`
- **Session log format** — WCCS now writes 30-line logs in session_logs/ instead of full handover rewrites. Weekly merge to master.
- **n8n self-hosted (NEW DISCOVERY)** — free, visual AI workflow builder, 400+ integrations, built-in AI nodes (Gemini/Mistral/Ollama). Could replace hand-coded AAFL loop with visual drag-and-drop. Investigate as potential AAFL foundation next session.

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | Notes | Status |
|---|---|---|---|
| 1 | **Add file-write step to loop_manager.py** | Option A — code runs but doesn't save to disk yet | ❌ Next |
| 2 | **Fix HuggingFace model name** | Still broken from last session | ❌ |
| 3 | **Install LangGraph on Python 3.14** | Full path: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install langgraph` | ❌ |
| 4 | **Wire aafl_core.py into sfl_agent.py** | Main agent orchestration link | ❌ |
| 5 | **Build Memory Bank (SQLite)** | Foundation for Loop + Knowledge Engine | ✅ Done |
| 6 | **Build Evaluator** | "Does the code run?" scoring | ❌ |
| 7 | **Build Researcher** | DuckDuckGo + local LLM + YAML rules | ❌ |
| 8 | **Test one overnight loop** | RTX 5090, LM Studio running | ❌ |

---

## KEY FILES

| File | Size | Purpose |
|---|---|---|
| aafl_core.py | 21 KB | AAFL spine — CONFIRMED WORKING |
| loop_manager.py | — | Loop Engine orchestrator — needs file-write step |
| memory_bank.py | 190 lines | SQLite memory bank (knowledge + tags tables) |
| cost_guard.py | 135 lines | ALP brake — £0.05 cap, loop detector, call logger |
| sfl_agent.py | 39 KB | Agent orchestrator |
| spin_doctor.py | 47 KB | Main app — 3 tabs |
| conductor.py | ~20 KB | 22 problems engine |
| control_panel.py | 30 KB | Control panel |
| model_router.py | 19 KB | Model routing |
| Knowledge_Engine_Schema_v1.md | 10 KB | Database schema |
| .env | 1 KB | All API keys |

---

## IMPORTANT NOTES

1. **Python:** Never use `python` in PowerShell. Full path always.
   - 3.14: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe`
   - 3.13: `C:\Users\jscot\AppData\Local\Programs\Python\Python313\python.exe`
2. **CrewAI venv:** `C:\Users\jscot\OneDrive\Desktop\crewai-env\Scripts\Activate.ps1`
3. **ALP in Claude Code:** One big task per session. Never chain small ones.
4. **LM Studio:** Only open for overnight loops. Close otherwise to save GPU.
5. **session_saver.py is dead.** Use WCCS (Write Claude Code Save) instead.
6. **Loop Engine gap:** loop_manager.py writes to DB but not disk. Fix this FIRST.

---

## 5 SISTER PROJECTS

| # | Project | Priority | Status |
|---|---|---|---|
| 1 | ALP (Allowance Preservation) | **#1 ALWAYS** | Active |
| 2 | BIG AAFL (AI Agent Feedback Loop) | #2 | Loop Engine first run ✅ |
| 3 | ACCA Code | Byproduct | Growing |
| 4 | Spin Doctor VKB | Last — AAFL builds it | On hold |
| 5 | Promotional | After proof of concept | Not started |

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
