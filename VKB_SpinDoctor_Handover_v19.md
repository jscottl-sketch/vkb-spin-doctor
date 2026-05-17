# VKB Spin Doctor — Project Handover v18 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** Session saver built via Claude Code. AAFL loop working. Full AI library researched.
**Last updated:** 14 May 2026
**Consolidates:** v17 + mission update + AI library + session saver

---

## LAST SESSION — 14 May 2026 evening

| | |
|---|---|
| **Built** | session_saver.py v1 via Claude Code — 4 files created in VKB folder |
| **Decisions** | GitHub approach abandoned (nearly leaked API keys via public repo). Claude Code is the correct build path. |
| **Ideas** | Session saver v2: auto-clipboard + Anthropic API auto-handover. SL idea: Claude Code → API → Claude Code text loop. |
| **ACCA codes** | WYM = What You Mean |
| **Next steps** | 1. Test session saver. 2. Upgrade to v2 with API. 3. Install AutoHotkey. 4. Wire LiteLLM into AAFL. |
| **Blockers** | AutoHotkey not installed. v2 upgrade may still be running in Claude Code. |

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

## MISSION STATEMENT

1. **ALP is priority period.** Cost must never exceed return.
2. **BIG AAFL masterminds original mission.** Everything goes through ALP.
3. **ACCA Code** — byproduct, organised later.
4. **Spin Doctor VKB** — last on list.
5. **Promotional** — proof of concept first.
6. **Fluid and flexible.** Works across projects.
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
| sfl_agent.py v3 | ✅ 575 lines |
| Claude Code v2.1.140 | ✅ |
| model_router.py | ✅ |
| control_panel.py | ✅ |
| free_providers.py — 13 providers | ✅ |
| aafl_loop.py | ✅ Tested, £0 spent |
| session_saver.py v1 | ✅ Built via Claude Code |
| SAVE_SESSION_NOW.bat | ✅ |
| SAVE_SESSION_HOTKEY.ahk | ✅ (needs AutoHotkey) |
| Session saver v2 (API auto-handover) | ⏳ Upgrade sent to Claude Code |
| LiteLLM | ❌ Not installed |

---

## SESSION SAVER

**v1 (working):** 6 questions → saves to session_logs/ + handover/LATEST_HANDOVER.md
**v2 (upgrading):** Auto-clipboard + API auto-handover via claude-haiku (~1p per save)

Files: session_saver.py, SAVE_SESSION_NOW.bat, SAVE_SESSION_HOTKEY.ahk, session_saver_config.json

---

## API KEYS

| Provider | In .env | Type |
|---|---|---|
| Anthropic | ✅ | Credits |
| Gemini | ✅ | Permanent free |
| Cohere | ✅ | Permanent free |
| HuggingFace | ✅ | Permanent free |
| OpenRouter | ✅ | Permanent free |
| Mistral | ✅ | Permanent free |
| Cerebras | ✅ | Permanent free |
| Cloudflare | ✅ | Permanent free |
| Groq | ❌ | Permanent free — auth broken |
| xAI Grok | ❌ | Credits $25+$150/mo |
| NVIDIA NIM | ❌ | Credits 1k-5k |
| SambaNova | ❌ | Permanent free |
| GitHub Models | ❌ | Permanent free |
| Ollama | ❌ | Local free |
| Together AI | ❌ | Credits $1 |
| Fireworks AI | ❌ | Permanent free |
| DeepSeek API | ❌ | Permanent free |

**ALP rule:** Local first → permanent free → credits → paid only if earning.

---

## LITELLM — GLUE LAYER (NOT YET INSTALLED)

Auto-routes between all providers. Auto-fallback. Install: `pip install litellm`

AAFL → aafl_loop.py → LiteLLM → providers

---

## NICHE AI MODULES (Toggleable, build when needed)

Gaming (Tryll), Hardware (LocalAI), OCR (Tesseract/OCR.Space), Voice (Whisper), Agents (LangGraph/CrewAI), Embeddings (Cohere+ChromaDB), Community (Reddit PRAW), Code (Fireworks/Cerebras), Windows (Ollama), Device (LiteRT)

---

## AAFL TASK ROUTING

| Task | Provider order |
|---|---|
| code | LM Studio Coder → Phi-4 → Groq → Cerebras → Mistral → OpenRouter |
| vision | LM Studio VL → Gemini Flash → HuggingFace |
| reason | LM Studio DeepSeek R1 → Groq DeepSeek → Gemini → Cerebras |
| fast | LM Studio Phi-4 → Cerebras → Groq → Gemini |
| batch | Mistral → LM Studio → Gemini → OpenRouter |
| embed | Cohere → LM Studio |

---

## SL IDEA (SAVED)

Claude Code → text capture → Claude API → instruction back. Not screenshots. Build after session saver v2. Small API cost per loop.

---

## NEXT PRIORITIES

| # | Task | Tool |
|---|---|---|
| 1 | Test session saver v1 | Manual |
| 2 | Check/finish session saver v2 upgrade | Claude Code |
| 3 | Install AutoHotkey | autohotkey.com |
| 4 | Install LiteLLM + wire into AAFL | Claude Code |
| 5 | Sign up xAI, NVIDIA NIM, SambaNova, GitHub Models | Browser |
| 6 | Install Ollama | Manual |
| 7 | Sign up Fireworks, DeepSeek | Browser |
| 8 | Retry Groq via GitHub auth | Manual |
| 9 | Load new API keys into aafl_loop.py | Claude Code |
| 10 | Wire aafl_loop into sfl_agent.py | Claude Code |
| 11 | Build Orchestrator | Claude Code |

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
