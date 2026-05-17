# VKB Spin Doctor — Project Handover v25

**Owner:** Scott (Croydon, England)
**Status:** 6 custom skills uploaded. WCCS v2 with logging active. Loop Engine proven.
**Last updated:** 17 May 2026
**Consolidates:** v24 + session logs 2026-05-17

---

## LAST SESSION — 17 May 2026

| | |
|---|---|
| **6 skills uploaded** | All 6 custom skills uploaded via Chrome browser (+ button → Skills → Add skill → upload zip). Skills management at claude.ai/customize/skills. |
| **WCCS skill v2 deployed** | Replaced old WCCS skill with v2 — now includes version incrementing and wccs_log.md logging automatically. |
| **RUN_WCCS.bat built** | One-click batch file for end-of-session saves. Lives in VKB-SpinDoctor folder. |
| **Skills upload path found** | + button in chat → Skills → Add skill → upload zip. Management: claude.ai/customize/skills. |
| **ALP #13 added** | Research Anthropic docs FIRST for any platform question. One search costs less than 5 guesses. |
| **ALP violations logged** | Multiple messages wasted guessing UI paths; batch file errors caused repeated rebuilds; should have built zip server-side from start. |

---

## WHO IS SCOTT — READ THIS FIRST

- **Brain injury (BI) 2023** — ONE STEP AT A TIME. No exceptions.
- **Beginner with code** — explain what is being built as you go
- **Always expand acronyms** on first use. **Tables preferred. Number all options.**
- **Always include keyboard shortcuts inline**
- **No bullshit** — if something is hard or slow, say so upfront

---

## ACCA CODE

| Code | Meaning | Code | Meaning |
|---|---|---|---|
| DRR | Don't require response | DWR | Don't want response |
| YO | Scott's opinion request | AIO | Claude's AI opinion |
| SIB | Summarise in brief | SIF | Summarise in full |
| CR | Confidence rating 1-10 | WMBW | Why might be wrong |
| WCBB | What could be better | NRM | No-repeat mode |
| SFL | Screenshot Feedback Loop | AAFL | AI Agent Feedback Loop |
| ALP | Allowance Preservation | CA | Completely Automate |
| WS | Web Search | WSF | Web Search Finding |
| WCCS | Write Claude Code Save | CLAC | Claude Code |
| BI | Brain injury | WYM | What You Mean |
| SIFFS | SIF This Session (≤50-line summary before WCCS) | | |
| + | Combine codes | = | Define a new code |

**Modes:** TBLM (Troubleshoot), DDM (Deep Dive), BGM (Beginner), BPM (Battle Plan), NRM (No-repeat), EM (Evidence)
**Retired:** SL → SFL. session_saver.py → WCCS.

---

## MISSION STATEMENT (locked in)

1. **ALP is RULE NO 1.** Cost must never exceed return.
2. **BIG AAFL masterminds original mission.** Everything goes through ALP.
3. **ACCA Code** — byproduct, organised later in own project. Save to database whenever mentioned.
4. **Spin Doctor VKB** — last on list. AAFL builds it.
5. **Promotional** — proof of concept first. Every penny earned goes back into Claude.
6. **Fluid and flexible.** Works across projects and software.

**The loop:** Free engine → builds product → earns → funds upgrades → Claude pays for itself.

---

## CURRENT STATUS

| Component | Status |
|---|---|
| aafl_core.py (21 KB) | ✅ CONFIRMED WORKING — timeout fix, tiered routing, 13 providers |
| loop_manager.py | ✅ Runs. Goal_met on first try. **GAP: no file-write step — code to DB only, not disk.** |
| memory_bank.py | ✅ Built (190 lines, SQLite, self-test passed) |
| cost_guard.py | ✅ Built (135 lines, £0.05 cap, all 3 brakes fire) |
| ALP_Database.md | ✅ Created (13 entries, grows each WCCS run) |
| session_logs/ | ✅ Active — 30-line logs per session |
| LiteLLM + python-dotenv | ✅ |
| sfl_agent.py v3 | ✅ 39 KB |
| spin_doctor.py | ✅ ~1057 lines, 3 tabs |
| Knowledge_Engine_Schema_v1.md | ✅ On disk — removed from Project Files (ALP saving) |
| 6 custom skills | ✅ Uploaded via Chrome — verify all toggles ON |
| WCCS skill v2 | ✅ Includes version incrementing + wccs_log.md logging |
| RUN_WCCS.bat | ✅ Built — one-click end-of-session save |
| Python 3.13 / 3.14 | ✅ Both installed |
| CrewAI (3.13 venv) | ✅ Installed (verify on next use) |
| LangGraph (3.14) | ❌ Not installed yet |
| Evaluator | ❌ Not built |
| Researcher | ❌ Not built |
| session_saver.py | ❌ Dead — replaced by WCCS |

---

## ONLINE PROVIDER STATUS

| Provider | Key? | Result | Notes |
|---|---|---|---|
| Gemini 2.5 Flash | ✅ | ✅ OK | 0.87s |
| Mistral Codestral | ✅ | ✅ OK | 0.49s — fastest |
| OpenRouter Auto | ✅ | ✅ OK | 2.21s |
| Cerebras llama3.1-70b | ✅ | ✅ Fixed | Model name corrected v23 session |
| HuggingFace | ✅ | ❌ | Model renamed — still needs fix |
| Groq | ❌ | ⏸️ SKIP | No API key |

---

## ALP RULES — CRITICAL

- **Sonnet not Opus** — 3-5x more messages for same allowance. Opus only for complex reasoning.
- **Chat + Claude Code share THE SAME pool.** Claude Code is £0 money but burns quota.
- **One big task per Claude Code session.** Never chain 10 small ones. Batch everything.
- **Walk-away mode:** `claude --dangerously-skip-permissions` — no prompts. Exit: `/exit`
- **Max 1-2 screenshots per message** — each image eats thousands of tokens. Describe the rest.
- **New chat for new topics** — long chats cost more per message. Start fresh when switching.
- **Combine questions** — 3 short messages cost more than 1 combined message.
- **Remove old handovers from Project Files** — keep latest only. Old ones load silently every message.
- **Extended Thinking off** for simple tasks — toggle in model selector.
- **n8n self-hosted** — free, visual, 400+ AI integrations. Investigate as potential AAFL replacement.
- **Research docs FIRST** — for any platform/UI question, search Anthropic docs before guessing. One search beats 5 wrong guesses. (ALP #13)
- **WCCS flow:** First type SIFFS in Chat (get ≤50-line session summary). Then paste that summary + this block into Claude Code: `Read chat_latest.txt in this folder. Compare against the existing handover and ALP_Database.md. Update ONLY sections with new information. Add new ALP savings to ALP_Database.md. Write a session log under 30 lines in session_logs/. Delete chat_latest.txt when done.`

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | Notes | Status |
|---|---|---|---|
| 1 | **Verify all 6 skill toggles ON** | Open claude.ai/customize/skills — check each is enabled | ❌ Next |
| 2 | **Test skills in a fresh chat** | Open new chat, try each skill trigger phrase | ❌ |
| 3 | **Add file-write step to loop_manager.py** | Option A — code runs but doesn't save to disk yet | ❌ |
| 4 | **Fix HuggingFace model name** | Still broken from v22 session | ❌ |
| 5 | **Investigate n8n self-hosted** | Free visual AI workflows — could replace hand-coded AAFL | ❌ |
| 6 | **Install LangGraph on Python 3.14** | `...pythoncore-3.14-64\python.exe -m pip install langgraph` | ❌ |
| 7 | **Wire aafl_core.py into sfl_agent.py** | Main orchestration link | ❌ |
| 8 | **Build Evaluator** | 0-10 quality scoring | ❌ |
| 9 | **Build Researcher** | DuckDuckGo + local LLM + YAML rules | ❌ |
| 10 | **Test overnight loop** | RTX 5090, LM Studio running, real goal.txt | ❌ |

---

## KEY FILES

| File | Size | Purpose |
|---|---|---|
| aafl_core.py | 21 KB | AAFL spine — confirmed working |
| loop_manager.py | — | Loop Engine orchestrator — needs file-write step |
| memory_bank.py | 190 lines | SQLite memory bank (knowledge + tags tables) |
| cost_guard.py | 135 lines | ALP brake — £0.05 cap, loop detector, call logger |
| sfl_agent.py | 39 KB | Agent orchestrator |
| spin_doctor.py | 47 KB | Main app — 3 tabs |
| conductor.py | ~20 KB | 22 problems engine |
| ALP_Database.md | — | Living ALP savings database — grows each session |
| Knowledge_Engine_Schema_v1.md | 10 KB | Database schema (on disk only — not in Project Files) |
| RUN_WCCS.bat | — | One-click end-of-session save batch file |
| skill_*.zip (×6) | Downloads\ | Custom skills — uploaded via Chrome |
| .env | 1 KB | All API keys |

---

## IMPORTANT NOTES

1. **Python full path always** — never just `python` in PowerShell.
   - 3.14: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe`
   - 3.13: `C:\Users\jscot\AppData\Local\Programs\Python\Python313\python.exe`
2. **CrewAI venv:** `C:\Users\jscot\OneDrive\Desktop\crewai-env\Scripts\Activate.ps1`
3. **LM Studio:** Only open for overnight loops. Close otherwise to save GPU.
4. **Loop Engine gap:** loop_manager.py writes to DB but NOT disk. Fix this FIRST next session.
5. **SFL for images only** — don't use vision model to read Chat text. Export chat as text instead.
6. **Skills management:** claude.ai/customize/skills — upload via + button in chat → Skills → Add skill.

---

## 5 SISTER PROJECTS

| # | Project | Priority | Status |
|---|---|---|---|
| 1 | ALP (Allowance Preservation) | **#1 ALWAYS** | Active |
| 2 | BIG AAFL (AI Agent Feedback Loop) | #2 | Loop Engine proven ✅ |
| 3 | ACCA Code | Byproduct | Growing |
| 4 | Spin Doctor VKB | Last — AAFL builds it | On hold |
| 5 | Promotional | After proof of concept | Not started |

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
