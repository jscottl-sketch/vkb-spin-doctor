# VKB Spin Doctor — Project Handover v20 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** aafl_core.py ~90% built by Claude Code. Session saver v2 done. LiteLLM research complete. Mission statement locked in.
**Last updated:** 14 May 2026 (late evening)
**Consolidates:** v19 + research session + AAFL spine build

---

## LAST SESSION — 14 May 2026 late evening

| | |
|---|---|
| **Built** | aafl_core.py — the AAFL spine — being written by Claude Code (~90% done at session end). SETUP_AAFL.bat (backup, not needed if using Claude Code). |
| **Research** | 3 web searches: LiteLLM confirmed right glue layer in 2026, free tiers stack to ~5,000 req/day at £0, "Ralph Loop" verify pattern is the 2026 agent standard. |
| **Brainstormed** | 4-pass "what needs doing" list (30 items), then 4 rounds of WMBW+WCBB. All converged on one decision: build the AAFL spine on LiteLLM first. |
| **Decisions** | LiteLLM is the backbone (replaces fragile custom provider code). aafl_core.py replaces aafl_loop.py. Wire aafl_core.py into sfl_agent.py — NOT old aafl_loop.py. Claude Code writes the files directly — no dragging files, no manual steps. |
| **Key insight** | Without a verify step, an agent "spins in infinite guesses." aafl_core.py has a verify() hook stub built in — deliberately dumb for now (just checks non-empty), extend later. |
| **Session saver v2** | ✅ Fully built in earlier Claude Code session. Not yet tested (needs AutoHotkey + config URL). |
| **Blockers** | aafl_core.py build not yet confirmed complete. AutoHotkey not installed. claude_project_url not set in session_saver_config.json. |

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

## MISSION STATEMENT (locked in this session)

1. **ALP is priority period.** Cost must never exceed return. This project is proof of concept.
2. **BIG AAFL masterminds original mission.** Everything goes through ALP.
3. **ACCA Code** — byproduct, organised later in own project.
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
| sfl_agent.py v3 | ✅ 575 lines |
| Claude Code v2.1.140 | ✅ |
| model_router.py | ✅ |
| control_panel.py | ✅ |
| free_providers.py — 13 providers | ✅ (being replaced by LiteLLM via aafl_core.py) |
| aafl_loop.py | ✅ (being replaced by aafl_core.py) |
| **aafl_core.py — new AAFL spine on LiteLLM** | ⏳ ~90% built by Claude Code |
| session_saver.py v2 | ✅ Built (not yet tested) |
| SAVE_SESSION_NOW.bat | ✅ |
| SAVE_SESSION_HOTKEY.ahk | ✅ (needs AutoHotkey) |
| SETUP_AAFL.bat | ✅ Backup bootstrap (not needed if using Claude Code) |
| LiteLLM + python-dotenv | ⏳ Being installed by Claude Code |

---

## aafl_core.py — WHAT IT IS

The AAFL spine. One clean file, one entry point: `AAFLCore().run(task, task_type)`.

| Feature | What it does |
|---|---|
| LiteLLM backbone | Talks to all providers in one format |
| Skips dead providers | No key in .env? Silently skips — no crash |
| Local-first routing | LM Studio → free online → paid (ALP order) |
| Dry-run mode | `dry_run=True` shows the plan, spends £0 |
| Cost tracker | Running total_cost tally, real numbers |
| Error log | Every success/failure to aafl_log.txt |
| Verify hook | Stub — clean slot to add real checks later |
| Project-agnostic | Zero "VKB" in it — works for any project |

Task type routing:

| Task type | Provider order (cheapest first) |
|---|---|
| code | LM Studio → Cerebras → Groq → Mistral → OpenRouter → Gemini |
| fast | LM Studio → Cerebras → Groq → Gemini |
| reason | LM Studio → Groq → Gemini → Cerebras |
| vision | LM Studio → Gemini |
| batch | Mistral → Gemini → OpenRouter |
| embed | Cohere |

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
| xAI Grok | ❌ | Credits $25+$150/mo |
| NVIDIA NIM | ❌ | Credits 1k-5k |
| SambaNova | ❌ | Permanent free |
| GitHub Models | ❌ | Permanent free |
| Ollama | ❌ | Local free |
| Together AI | ❌ | Credits $1 |
| Fireworks AI | ❌ | Permanent free |
| DeepSeek API | ❌ | Permanent free |

.env location: C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\.env

**ALP rule:** Local first → permanent free → credits → paid only if earning.

---

## RESEARCH FINDINGS (this session)

| # | Finding |
|---|---|
| 1 | LiteLLM: still the right glue layer. 100+ providers, one interface, built-in fallback/retry/cooldown. pip install litellm. |
| 2 | Free tier stack: ~5,000 req/day at £0. Gemini 1,500/day, Groq 30/min, OpenRouter ~200/day/model, Cerebras 2,000 TPS, Cloudflare 10k neurons/day. |
| 3 | 2026 agent pattern ("Ralph Loop"): plan → act → VERIFY → loop until done. Without a verify signal, agents spin in infinite guesses. |
| 4 | Human-on-the-loop: agents need a Scott-approval gate before irreversible actions. |

---

## BRAINSTORM — FULL "WHAT NEEDS DOING" LIST (30 items, 4 passes)

**Pass 1 — known:** 1. Update config URL, 2. Install AutoHotkey, 3. Test session saver v2, 4. Install LiteLLM, 5. Wire into sfl_agent, 6. Build Orchestrator, 7. Build handover_writer, 8. Cloudflare wrapper, 9. Sign up remaining providers, 10. Retry Groq, 11. ED spin fix v0.2

**Pass 2 — gaps:** 12. Rebuild aafl_loop ON LiteLLM (→ aafl_core.py ✅), 13. Verify step, 14. Real cost tracker, 15. One shared .env loader, 16. Error logging, 17. Dry-run mode

**Pass 3 — research-informed:** 18. Skip dead providers auto, 19. Complexity routing (cheap for easy, strong for hard), 20. Rate-limit awareness, 21. Scott-approval gate, 22. AGENTS.md patterns file

**Pass 4 — structural:** 23. Decide AAFL architecture (library), 24. Single config source of truth, 25. One entry point, 26. Separate 3 layers (routing/orchestration/verification), 27. Zero "VKB" hardcoded, 28. Plan for "all providers exhausted"

---

## WMBW/WCBB CONCLUSIONS (4 rounds)

| Round | Risk | Fix applied |
|---|---|---|
| 1 | Building everything at once = overwhelm | Build spine ONLY first ✅ |
| 2 | LiteLLM had supply-chain note (Trivy, now contained) | Install normally, it's resolved |
| 3 | Verify step could become a rabbit hole | Start dumb: non-empty check + Scott approval ✅ |
| 4 | AAFL routes to unconfigured providers and crashes | Skip providers with no key from line 1 ✅ |

---

## SESSION SAVER

**v2 (built, not tested):** Ctrl+Shift+S → auto Ctrl+A/C → saves chat → Haiku API summary → handover file → opens project page
**Before first use:** Set `claude_project_url` in session_saver_config.json (currently points to generic projects page)
**Needs:** AutoHotkey installed for hotkey to work

---

## CLAUDE CODE STATUS

- Version: v2.1.140
- Auth: claude.ai subscription (jscottl@hotmail.co.uk) ✅
- NOT API billing ✅
- ALP: £0 per task ✅
- To open: cd C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor then type: claude

---

## NEXT PRIORITIES — PICK UP HERE

| # | Task | How | Status |
|---|---|---|---|
| 1 | **Check aafl_core.py build finished** | Open Claude Code, check output | ⏳ was ~90% |
| 2 | **Run aafl_core.py dry-run test** | `python aafl_core.py` — spends nothing | Waiting on 1 |
| 3 | **Update claude_project_url** in session_saver_config.json | Paste into Claude Code: set URL to your project page | Not done |
| 4 | **Install AutoHotkey** | Paste into Claude Code: `winget install AutoHotkey.AutoHotkey` | Not done |
| 5 | **Wire aafl_core.py into sfl_agent.py** | Paste into Claude Code: wire AAFLCore.run() into sfl_agent | Not done |
| 6 | **Test session saver v2** | Run SAVE_SESSION_NOW.bat — interactive, needs Scott there | Not done |
| 7 | Build Orchestrator layer | Claude Code | Not started |
| 8 | Sign up remaining providers | Browser: xAI, NVIDIA, SambaNova, GitHub, Fireworks, DeepSeek | Not done |

**Combined paste for tasks 3+4+5 (ready when task 2 passes):**
> Three setup tasks, do them in order without asking me to confirm each step:
> 1. Open session_saver_config.json and set claude_project_url to: [PASTE YOUR PROJECT URL]
> 2. Install AutoHotkey: winget install AutoHotkey.AutoHotkey
> 3. Wire aafl_core.py into sfl_agent.py so the agent routes through AAFLCore.run(). Use aafl_core.py NOT old aafl_loop.py. Show what changed.
> Report back in a short table.

---

## SL IDEA (SAVED)

Claude Code → text capture → Claude API → instruction back. Not screenshots. Build after session saver v2. Small API cost per loop.

---

## 4 SISTER PROJECTS

| # | Project | Priority | Status |
|---|---|---|---|
| 1 | ALP (Allowance Preservation) | **#1 always** | Active — all builds £0 |
| 2 | BIG AAFL (AI Agent Feedback Loop) | #2 | aafl_core.py 90% built |
| 3 | ACCA Code (database of shortcodes) | Byproduct | Growing naturally |
| 4 | Spin Doctor VKB (the actual product) | Last — AAFL builds it | On hold |
| 5 | Promotional (monetisation) | After proof of concept | Not started |

---

## GitHub

Account: jscottl-sketch | Repo: vkb-spin-doctor (empty, .git removed)
Future: make PRIVATE, add .gitignore excluding .env, use for backup only.
