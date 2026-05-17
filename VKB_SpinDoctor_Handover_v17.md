# VKB Spin Doctor — Project Handover v17 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** AAFL loop built + tested. 6 of 7 online API keys obtained. All keys in .env.
**Last updated:** 14 May 2026
**Consolidates:** v11 → v16 + today

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
| Claude Code v2.1.119 | ✅ Installed |
| model_router.py | ✅ Built |
| control_panel.py | ✅ Built |
| free_providers.py — all 13 providers | ✅ Built 14/05/2026 |
| aafl_loop.py — AAFL loop manager | ✅ Built + tested 14/05/2026 |
| AAFL test result | ✅ AAFL_OK via Phi-4 in 0.12s, £0 spent |

---

## API KEYS STATUS

| Provider | Key in .env | Notes |
|---|---|---|
| Anthropic | ✅ | Windows env var + .env |
| Gemini | ✅ | Already set |
| Cohere | ✅ | CpWBrrOX... |
| HuggingFace | ✅ | hf_rETEfg... |
| OpenRouter | ✅ | sk-or-v1-e1e6... |
| Mistral | ✅ | zg0J56W1... |
| Cerebras | ✅ | csk-tmexcf... |
| Cloudflare | ✅ | cfat_tr2fBN... + Account ID set |
| Groq | ❌ | Auth system broken — skip for now |

---

## AAFL LOOP — HOW IT WORKS

File: aafl_loop.py (14,110 bytes)
File: free_providers.py (3,082 bytes)

Task comes in → detect type → try providers in priority order → fallback if fail → log result → ALP: £0

Task types: code, vision, reason, fast, embed, batch

| Task | Provider order |
|---|---|
| code | LM Studio Coder → Phi-4 → Groq → Cerebras → Mistral → OpenRouter |
| vision | LM Studio VL → Gemini Flash → HuggingFace |
| reason | LM Studio DeepSeek R1 → Groq DeepSeek → Gemini → Cerebras |
| fast | LM Studio Phi-4 → Cerebras → Groq → Gemini |
| batch | Mistral → LM Studio → Gemini → OpenRouter |
| embed | Cohere → LM Studio |

Usage:
```python
from aafl_loop import AAFLLoop
loop = AAFLLoop()
result = loop.run(task="fix this bug", task_type="code")
print(result.response)
```

---

## NEXT PRIORITIES

| # | Task | Tool |
|---|---|---|
| 1 | Load all API keys from .env into aafl_loop.py | Claude Code |
| 2 | Test each online provider one by one | PowerShell |
| 3 | Build Cloudflare Python wrapper | Claude Code |
| 4 | Wire aafl_loop into sfl_agent.py | Claude Code |
| 5 | Build Orchestrator layer | Claude Code |
| 6 | Retry Groq (try GitHub auth) | Manual |
| 7 | ED spin fix v0.2 | Claude Code |
| 8 | win_hardener module | Claude Code |

---

## HOW TO RUN EVERYTHING
