# VKB Spin Doctor — Project Handover v18 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** .env fully loaded. Claude Code fixed to claude.ai subscription. aafl_loop.py updated with load_dotenv.
**Last updated:** 14 May 2026
**Consolidates:** v17 + today

---

## WHO IS SCOTT — READ THIS FIRST

- **Brain injury (BI) 2023** — ONE STEP AT A TIME. No exceptions.
- **Beginner with code** — explain what is being built as you go
- **Always expand acronyms** on first use
- **Always include keyboard shortcuts inline**
- **Tables preferred** for structured info
- **Number all options** — Scott replies with just a number
- **No bullshit** — if something is hard or slow, say so upfront
- **Files:** never use artifacts/downloads — use PowerShell here-strings instead

---

## ACCA CODE

| Code | Meaning |
|---|---|
| DRR | Don't require response |
| DWR | Don't want response |
| YO | Scott asking for Claude's opinion |
| AIO | Claude giving its AI opinion |
| SIB | Summarise in brief |
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
| SIF | Summarise In Full |
| + | Combine codes |
| = | Define a new code |

---

## PRIORITY ORDER

1. ALP — Allowance Preservation. Every decision, cheapest path first.
2. Big SFL / AAFL — Universal AI agent that masterminds Spin Doctor.
3. ACCA Code — grows as byproduct, sorted later in own project.
4. Spin Doctor VKB — resumes once AAFL can run it.

---

## CURRENT PROJECT STATUS

| Component | Status |
|---|---|
| v0.1 spin fix — War Thunder | ✅ Working |
| usb_power_saver.py | ✅ Built |
| steam_input_conflict.py | ✅ Built |
| core/win_compat.py | ✅ Built |
| data/devices.json (98 VID/PID) | ✅ Built |
| Universal_Input_Device_Database.md (44 problems) | ✅ In folder |
| problems/conductor.py (619 lines, 22 problems) | ✅ Built |
| spin_doctor.py — 3 tabs (Fix/Conductor/KB) | ✅ ~1057 lines |
| sfl_agent.py v3 — ACP v1 | ✅ 575 lines |
| Claude Code v2.1.140 | ✅ Installed + fixed to claude.ai subscription |
| model_router.py | ✅ Built |
| control_panel.py | ✅ Built |
| free_providers.py — all 13 providers | ✅ Built |
| aafl_loop.py — load_dotenv added | ✅ Updated 14/05/2026 |
| AAFL test result | ✅ AAFL_OK via Phi-4 in 0.12s, £0 spent |

---

## API KEYS STATUS — ALL IN .env FILE

| Provider | Key starts with | Status |
|---|---|---|
| Anthropic | sk-ant-api03-nZHM... | ✅ In .env |
| Gemini | AIzaSyACbQkMd0_... | ✅ In .env (duplicate line — harmless) |
| Cohere | CpWBrrOXTGiONr... | ✅ In .env |
| HuggingFace | hf_rETEfgpFyyh... | ✅ In .env (key name: HF_API_KEY) |
| OpenRouter | sk-or-v1-e1e6ca... | ✅ In .env |
| Mistral | zg0J56W1XCEwYT... | ✅ In .env |
| Cerebras | csk-tmexcf4899e... | ✅ In .env |
| Cloudflare | cfat_tr2fBN... | ❌ Not recovered — needs re-login to dash.cloudflare.com |
| Groq | N/A | ❌ Auth system broken — skip for now |

.env location: C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\.env

---

## CLAUDE CODE STATUS

- Version: v2.1.140
- Auth: claude.ai subscription (jscottl@hotmail.co.uk) ✅
- NOT API billing ✅
- ALP: £0 per task ✅
- ANTHROPIC_API_KEY removed from Windows User env vars ✅
- To open: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor then claude

---

## AAFL LOOP — HOW IT WORKS

File: aafl_loop.py (updated — load_dotenv added)
File: free_providers.py

Task comes in → detect type → try providers in priority order → fallback if fail → log result → ALP: £0

| Task | Provider order |
|---|---|
| code | LM Studio Coder → Phi-4 → Groq → Cerebras → Mistral → OpenRouter |
| vision | LM Studio VL → Gemini Flash → HuggingFace |
| reason | LM Studio DeepSeek R1 → Groq DeepSeek → Gemini → Cerebras |
| fast | LM Studio Phi-4 → Cerebras → Groq → Gemini |
| batch | Mistral → LM Studio → Gemini → OpenRouter |
| embed | Cohere → LM Studio |

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | Tool |
|---|---|---|
| 1 | Install python-dotenv package | PowerShell: pip install python-dotenv --break-system-packages |
| 2 | Test each online provider one by one | PowerShell |
| 3 | Build Cloudflare Python wrapper | Claude Code |
| 4 | Wire aafl_loop into sfl_agent.py | Claude Code |
| 5 | Build Orchestrator layer | Claude Code |
| 6 | Build handover_writer.py | Claude Code |
| 7 | Retry Groq (try GitHub auth) | Manual |
| 8 | ED spin fix v0.2 | Claude Code |

---

## IMPORTANT — TASK 1 FIRST

aafl_loop.py now has load_dotenv() but python-dotenv package may not be installed.
Run this FIRST next session before anything else:@'
# VKB Spin Doctor — Project Handover v18 (MASTER)
Owner: Scott (Croydon, England)
Status: .env loaded. Claude Code on claude.ai subscription. aafl_loop.py updated with load_dotenv.
Last updated: 14 May 2026

## PRIORITY ORDER
1. ALP - Allowance Preservation. Cheapest path first always.
2. Big AAFL - Universal AI agent that masterminds Spin Doctor.
3. ACCA Code - byproduct, sort later.
4. Spin Doctor VKB - last.

## ACCA CODE
DRR=Dont require response, DWR=Dont want response, YO=Scott asking opinion, AIO=Claude opinion, SIB=Summarise brief, CR=Confidence rating, WMBW=Why might be wrong, WCBB=What could be better, NRM=No-repeat mode, BI=Brain injury, SFL=Screenshot Feedback Loop, AAFL=AI Agent Feedback Loop, ALP=Allowance Preservation, CA=Completely Automate, WS=Web Search, WSF=Web Search Finding, WYM=What You Mean, SIF=Summarise In Full

## CLAUDE CODE STATUS
Version: v2.1.140
Auth: claude.ai subscription jscottl@hotmail.co.uk - NOT API billing - FREE
ANTHROPIC_API_KEY removed from Windows User env vars
To open: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor then type: claude

## API KEYS - ALL IN .env
ANTHROPIC_API_KEY=sk-ant-api03-nZHM... (in .env)
@'
# VKB Spin Doctor — Project Handover v18 (MASTER)
Owner: Scott (Croydon, England)
Status: .env loaded. Claude Code on claude.ai subscription. aafl_loop.py updated with load_dotenv.
Last updated: 14 May 2026

## PRIORITY ORDER
1. ALP - Allowance Preservation. Cheapest path first always.
2. Big AAFL - Universal AI agent that masterminds Spin Doctor.
3. ACCA Code - byproduct, sort later.
4. Spin Doctor VKB - last.

## ACCA CODE
DRR=Dont require response, DWR=Dont want response, YO=Scott asking opinion, AIO=Claude opinion, SIB=Summarise brief, CR=Confidence rating, WMBW=Why might be wrong, WCBB=What could be better, NRM=No-repeat mode, BI=Brain injury, SFL=Screenshot Feedback Loop, AAFL=AI Agent Feedback Loop, ALP=Allowance Preservation, CA=Completely Automate, WS=Web Search, WSF=Web Search Finding, WYM=What You Mean, SIF=Summarise In Full

## CLAUDE CODE STATUS
Version: v2.1.140
Auth: claude.ai subscription jscottl@hotmail.co.uk - NOT API billing - FREE
ANTHROPIC_API_KEY removed from Windows User env vars
To open: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor then type: claude

## API KEYS - ALL IN .env
ANTHROPIC_API_KEY=sk-ant-api03-nZHM... (in .env)
GEMINI_API_KEY=AIzaSyACbQkMd0_... (in .env, duplicate line harmless)
COHERE_API_KEY=CpWBrrOXTGiONr99QulNS4WneduOgiDfBh0Gulsu (in .env)
HF_API_KEY=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 (in .env)
OPENROUTER_API_KEY=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 (in .env)
MISTRAL_API_KEY=zg0J56W1XCEwYThQFIENpr502CJGAbKO (in .env)
CEREBRAS_API_KEY=csk-tmexcf4899ejvpftmkctrxjphjtwdy2pw2m2cmf2xrp4nhh8 (in .env)
CLOUDFLARE=NOT RECOVERED - re-login dash.cloudflare.com next session
GROQ=SKIP - auth broken

## FILES BUILT
spin_doctor.py ~1057 lines, sfl_agent.py 575 lines, aafl_loop.py (load_dotenv added 14/05), free_providers.py, model_router.py, control_panel.py, usb_power_saver.py, steam_input_conflict.py, win_compat.py, devices.json (98 VID/PID), conductor.py 619 lines

## NEXT SESSION - DO IN ORDER
1. Install python-dotenv - run: python.exe -m pip install python-dotenv
   Full path: C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe -m pip install python-dotenv
2. Test aafl_loop.py runs without error
3. Test each online provider one by one
4. Build Cloudflare Python wrapper (Claude Code)
5. Wire aafl_loop into sfl_agent.py (Claude Code)
6. Build Orchestrator layer (Claude Code)
7. Build handover_writer.py - auto handover at session end (Claude Code)
