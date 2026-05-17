# VKB Spin Doctor — Project Handover v16 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** AAFL loop engine live. evaluator.py + researcher.py built. loop_manager --once tested and passing. sfl_agent.py v3 (~920 lines). Conductor module live. ED Bind Reset prevention built.
**Last updated:** 17 May 2026 (AAFL loop components, HF fix, LangGraph)
**Consolidates:** v15

---

## WHO IS SCOTT — READ THIS FIRST

- **Brain injury (BI) 2023** — ONE STEP AT A TIME. No exceptions. Never stack steps.
- **Beginner with code** — explain what's being built as you go
- **Always expand acronyms** on first use
- **Always include keyboard shortcuts inline** (e.g. Windows key + X)
- **Tables preferred** for structured info
- **Number all options** — Scott replies with just a number
- **No bullshit** — if something's hard or slow, say so upfront

---

## ACCA CODE

| Code | Meaning |
|---|---|
| DRR | Don't require response |
| DWR | Don't want response |
| YO | Scott asking for Claude's opinion |
| AIO | Claude giving its AI opinion |
| SIB | Summarise in brief |
| CR | Confidence rating 1–10 |
| WMBW | Why might be wrong |
| WCBB | What could be better |
| NRM | No-repeat mode |
| BI | Brain injury |
| SFL | Screenshot Feedback Loop |
| + | Combine codes |
| = | Define a new code |

Modes: TBLM (troubleshoot), DDM (deep dive), BGM (beginner), BPM (battle plan), NRM (no-repeat), EM (evidence)

---

## CURRENT PROJECT STATUS

| Component | Status |
|---|---|
| v0.1 spin fix — War Thunder | ✅ Working |
| usb_power_saver.py | ✅ Built |
| steam_input_conflict.py | ✅ Built |
| core/win_compat.py (pywin32 shim) | ✅ Built |
| data/devices.json (98 VID/PID devices) | ✅ Built |
| Universal_Input_Device_Database.md (44 problems) | ✅ In folder |
| problems/conductor.py (619 lines, 22 problems) | ✅ Built — 3 live conflicts found on Scott's machine |
| spin_doctor.py — 3 tabs (Fix / Conductor / KB) | ✅ ~1057 lines, all tabs confirmed working |
| sfl_agent.py v3 — ACP v1 + handover injection | ✅ ~920 lines, call_aafl() added |
| Claude Code v2.1.119 | ✅ Installed, working |
| Elite Dangerous spin fix | ✅ Fixed at hardware level via VKB DevConfig |
| GUI visual check (RUN_VKB.bat) | ✅ Done |
| ED Bind Reset prevention | ✅ Built as problems/ed_bind_reset.py, wired into GUI Fix Mouse Spin tab |
| aafl_core.py — provider routing | ✅ HuggingFace fixed → Mistral-7B-Instruct-v0.3 |
| loop_manager.py — loop engine | ✅ --once flag, max_loop_iters/max_llm_calls decoupled. Tested: Gemini+Mistral, goal_met=True |
| evaluator.py — result scorer | ✅ Built — completeness/clarity/accuracy, 0-10, pure logic |
| researcher.py — DuckDuckGo search | ✅ Built — ddgs package, fallback on error |
| LangGraph 1.2.0 | ✅ Installed |
| Throttle slider in War Thunder | ⏸ Open (likely PS5/Xbox conflict — unplug and retry) |
| Star Citizen full support | ⏸ Waiting |
| evaluator.py wired into loop_manager | ⏸ Next |
| researcher.py wired into planning step | ⏸ Next |

---

## BIG VISION

Not a VKB-specific tool. A **universal input device assistant** — any hardware, any game, one tool.

> *"The tool that should have existed the moment the first joystick was ever plugged into a PC."*

For each game the tool provides:
- Top 10 most common + least common problems and fixes
- Most popular community keybind preferences
- Downloadable keybind profiles stored locally
- Visual keybinding maps stored locally
- All accessible from the GUI Knowledge Base tab

**The core product:** Steam "Generic Gamepad Configuration Support" is silently breaking joysticks and wheels for millions of players. Fix = uncheck one box. Nobody has built a tool that does this automatically. That's Spin Doctor.

---

## TWO-TOOL STRATEGY

| Tool | Best for | Cost |
|---|---|---|
| Claude Code | Code jobs — reads files as text, edits directly | API credits, very efficient |
| SFL Agent (sfl_agent.py) | Visual tasks — game UIs, screen diagnosis | ~$0.003/screenshot |

**Rule:** Code jobs → Claude Code. Eyes-on-screen → SFL Agent.

---

## HOW TO RUN

### Claude Code
Admin terminal (Windows key + X → Terminal (Admin)):
```
cd "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor"
```
```
claude
```

### SFL Agent
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\sfl_agent.py"
```

With token budget (for long tasks):
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\sfl_agent.py" --budget 30k
```

### Loop Manager (one iteration test)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\loop_manager.py" --once
```

### GUI
Double-click `RUN_VKB.bat`

---

## SFL AGENT — KEY FEATURES

sfl_agent.py is reusable on any project — copy it to a new folder and create a PROJECT_HANDOVER.md there.

| Feature | What it does |
|---|---|
| Path injection | Project folder injected into every Claude message |
| Running memory | Claude sees all previous commands + outputs each loop |
| Extend at limit | At 50 iterations asks "keep going?" instead of stopping |
| Ask user | Claude can pause mid-task and ask Scott a question |
| Log file | Every session saves to `sfl_logs/` |
| Safe-op allow-list | Fewer Y/N prompts for obvious read-only ops |
| Flags | `--note`, `--folder`, `--budget` flags available |
| Handover injection | Loads PROJECT_HANDOVER.md into system prompt on startup |
| call_aafl(prompt) | Convenience wrapper — routes any prompt through AAFLCore |

### Autonomy Control Panel v1 (built into sfl_agent)

| Feature | What it does |
|---|---|
| Heartbeats | Prints one-line status every 30s. No per-step approvals needed. |
| Safe-op allow-list | Whitelist: reads, --help, --dry-run, --check, py_compile, git status. >5 files or wildcard = always asks. |
| Auto-snapshot | Copies .py/.json/.xml to backups/auto_YYYYMMDD_HHMMSS/ before any edit. Keeps last 20. |
| Token budget | Soft cap 80% = finish current task, stop new ones. Hard cap 100% = kill. |

---

## AAFL — PROVIDER ROUTING

aafl_core.py routes all LLM calls cheapest-first. Loop engine: loop_manager.py.

### Provider Status (as of 17 May 2026)

| Provider | Model | Tier | Status |
|---|---|---|---|
| LM Studio Coder 32B | openai/qwen2.5-coder-32b-instruct | 1 (local) | ✅ When LM Studio running |
| LM Studio VL 32B | openai/qwen2.5-vl-32b-instruct | 1 (local) | ✅ When LM Studio running |
| LM Studio DeepSeek R1 | openai/deepseek-r1-70b | 1 (local) | ✅ When LM Studio running |
| LM Studio Phi-4 14B | openai/phi-4-14b | 1 (local) | ✅ When LM Studio running |
| Cerebras Llama 3.1 70B | cerebras/llama3.1-70b | 2 (free) | ⚠️ Model renamed — fails currently |
| Groq Llama 3.3 70B | groq/llama-3.3-70b-versatile | 2 (free) | Key needed |
| Groq DeepSeek R1 | groq/deepseek-r1-distill-llama-70b | 2 (free) | Key needed |
| Gemini 2.5 Flash | gemini/gemini-2.5-flash | 2 (free) | ✅ Working |
| Mistral Codestral | mistral/codestral-latest | 2 (free) | ✅ Working |
| OpenRouter Auto | openrouter/openrouter/auto | 3 (fallback) | Key needed |
| HuggingFace Mistral-7B | huggingface/mistralai/Mistral-7B-Instruct-v0.3 | 3 (fallback) | Key needed |
| Cohere Embeddings | cohere/embed-english-v3.0 | 3 (embed) | Key needed |
| Claude Sonnet (PAID) | claude-sonnet-4-6 | 99 (paid) | Blocked unless allow_paid=True |

### Loop Engine Components

| File | Role |
|---|---|
| aafl_core.py | Provider routing, LiteLLM wrapper, cheapest-first |
| loop_manager.py | Plan→Work→Verify→Store loop. --once flag for single iteration |
| evaluator.py | Scores results 0-10 (completeness/clarity/accuracy). Pure logic. |
| researcher.py | DuckDuckGo search via ddgs. Returns top 5 results. Fallback on error. |
| memory_bank.py | SQLite store — data/knowledge_engine.db |
| cost_guard.py | Cost + iteration brake. Raises CostGuardError before cap exceeded. |

---

## ENGINE ARCHITECTURE — MICROKERNEL

Drop a .py file into `/problems/` — engine picks it up automatically. No registration needed.

| Module ID | Name | Problems covered | Status |
|---|---|---|---|
| spin_fix | Spin Bug (Mouse Axis) | Removes mouse double-bind from flight axes | ✅ Working (War Thunder) |
| usb_power_saver | USB Power Saver | Disables Windows USB port power-off mid-session | ✅ Built |
| steam_input_conflict | Steam Input Conflict | Turns Steam Input OFF for WT, ED, MSFS, DCS, IL-2, AC7 | ✅ Built |
| conductor | Process Conductor | 22 problems — companion software, input mappers, overlays, launch order | ✅ Built |
| win_hardener | Windows Hardener | 9 problems (USB power, registry, polling rate) | ⏸ v0.2 |
| identity | Device Identity | 7 problems (device naming, VID/PID, config name mismatch) | ⏸ v0.3 |
| config | Config Mediator | 6 problems (game config files — WT spin fix lives here) | ⏸ v0.2 |
| physical | Physical Diagnostics | 5 problems (USB port, hub, power — detect only) | ⏸ v0.4 |

### Conductor module — what it covers (22 problems, 4 groups)

| Group | What it scans |
|---|---|
| A | Companion software: G HUB, LGS, Synapse, iCUE, SteelSeries, Armoury Crate, MSI Center, TARGET, VKB DevCfg |
| B | Input mappers: DS4Windows, Xpadder, JoyToKey, Joystick Gremlin, vJoy, X360CE, Steam overlay |
| C | Overlay processes: GeForce Experience, Adrenalin, Discord, OBS, Xbox Game Bar |
| D | Launch order advisory, HidHide state, compounded multi-companion warning |

**Live conflicts found on Scott's machine:** Corsair iCUE, Steam overlay, NVIDIA GeForce Experience.

Never auto-kills anything. Pure stdlib.

---

## UNIVERSAL INPUT DEVICE DATABASE — SUMMARY

File: `Universal_Input_Device_Database.md` — 44 problems across all gaming hardware types.
13 fully auto-fixable. 8 partially. 3 guide only.

### Top 8 Universal Problems (cover ~80% of all complaints)

| Rank | Problem | Auto-Fix? |
|---|---|---|
| 1 | Device not detected / seen as Xbox pad | ✅ Full |
| 2 | Bindings reset after update | ✅ Backup/restore |
| 3 | Double input / controller conflict | ✅ Full |
| 4 | Sensitivity wrong | ✅ Starter values |
| 5 | Axis drift at rest | ⚠️ Partial |
| 6 | Inverted axes | ✅ Full |
| 7 | Steam Input interfering | ✅ Full |
| 8 | Wrong device name in config | ✅ Full |

---

## THE 6 FIX CHAINS

| Chain | Root cause | What it fixes |
|---|---|---|
| 1 | Steam Generic Gamepad ON | Problems #1, #3, #7 — three fixes from one Registry key |
| 2 | Wrong USB port / hub | Detection failures, drift, FFB death |
| 3 | Companion software conflict (G Hub vs Synapse vs iCUE) | Input lag, broken remaps, 1-second delay |
| 4 | Device name changed post-update | Bindings silently ignored |
| 5 | Polling rate stuck at 125Hz (8ms lag) | Sluggish feel — free fix, nobody tells beginners |
| 6 | joy.cpl corruption (from registry cleaners) | All joystick calibration broken |

---

## PROJECT FILES

```
VKB-SpinDoctor/
├── spin_doctor.py                     # ~1057 lines. Tabs: Fix / Conductor / Knowledge Base
├── sfl_agent.py                       # v3 — ~920 lines. ACP v1 + handover injection + call_aafl()
├── aafl_core.py                       # Provider routing — 13 providers, cheapest-first
├── loop_manager.py                    # Loop engine — Plan→Work→Verify→Store. --once flag.
├── evaluator.py                       # Result scorer 0-10. Pure logic. No APIs.
├── researcher.py                      # DuckDuckGo search via ddgs. Top 5 results.
├── memory_bank.py                     # SQLite knowledge store
├── cost_guard.py                      # Cost + iteration brake
├── model_router.py                    # Model routing helpers
├── free_providers.py                  # Free provider list
├── sl_loop.py                         # Gemma 4 local SFL
├── goal.txt                           # Current loop goal
├── RUN_VKB.bat                        # Double-click GUI launcher
├── GIT_BACKUP.bat                     # git add -A + commit + push
├── Universal_Input_Device_Database.md # 44 problems, all hardware types
├── PROJECT_HANDOVER.md                # This file — read by sfl_agent on startup
├── problems/
│   ├── __init__.py
│   ├── conductor.py                   # Module 04 ✅ 619 lines
│   └── ed_bind_reset.py               # ED Bind Reset prevention ✅
├── data/
│   ├── devices.json                   # 98 devices with VID/PID lookup
│   ├── knowledge_engine.db            # SQLite — loop attempt results
│   └── cost_log.txt                   # CostGuard event log
├── loop_output/                       # Loop results (timestamped .txt files)
├── backups/                           # Auto-snapshots (vNN_<slug>/ naming)
├── sfl_logs/                          # SFL agent session logs
└── session_logs/                      # WCCS session logs
```

---

## GAME CONFIG FILE PATHS

| Game | Path | Format |
|---|---|---|
| War Thunder | `C:\Users\jscot\OneDrive\My Documents\My Games\WarThunder\Saves\226494292\production\` | .blk |
| Elite Dangerous | `C:\Users\jscot\AppData\Local\Frontier Developments\Elite Dangerous\Options\Bindings\` | .binds (XML) |
| Star Citizen | `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Controls\Mappings\` | .xml |
| Arma Reforger | `Documents\My Games\ArmaReforger\profile\.save\settings\customInputConfigs\` | .json |

---

## ELITE DANGEROUS — KEY NOTES

- Spin bug already fixed at hardware level via VKB DevConfig. No .binds edit needed for spin.
- No custom .binds file exists yet — game uses built-in "KeyboardMouseOnly" default.
- .binds file is only created once Scott launches ED and customises one binding.
- When fixing spin via file: set `<MouseXMode Value="Bindings_MouseRoll" />` and `<MouseYMode>` to `Value=""`.
- ED Bind Reset prevention: rename the .binds file — ED never overwrites renamed files.

---

## KEYBINDING PROFILE LIBRARY (for v0.5)

### Ready to use

| Game | Source | Notes |
|---|---|---|
| Star Citizen | SubliminalsTV GitHub (github.com/SubliminalsTV/Subs-Curated-Bindings) | Free, updated every patch. Latest: 4.4 LIVE |
| Star Citizen Enhanced | Gumroad (subliminalstv.gumroad.com/l/Enhanced_VKB_NXT) | Requires Joystick Gremlin. Patch 4.5 PTU |
| War Thunder | WT Live community (live.warthunder.com/post/1112657/en) | Single stick simulator preset |
| DCS World | DCS file repo (digitalcombatsimulator.com/en/files — filter: VKB NXT) | Multiple aircraft |
| X4: Foundations | Built into game (in-game preset menu) | Zero install — added in 7.0 update |
| Falcon BMS | BMS forum (forum.falcon-bms.com/topic/26999) | F-16 focused |
| Arma Reforger | Workshop (reforger.armaplatform.com/workshop/660604C2DBCF99E2) | Helicopter only |
| Elite Dangerous | Frontier Forums (forums.frontier.co.uk/threads/618833) | USB device ID needs auto-fix |

---

## COMPETITIVE LANDSCAPE

| Tool | Problem |
|---|---|
| Joystick Gremlin | Complex, requires vJoy driver, power-users only |
| VKB DevConfig | Brand-locked to VKB, "obscure and arcane" |
| TARGET (Thrustmaster) | Thrustmaster hardware only |
| devreorder | Solves device order only, no GUI |
| antimicro | Generic, no game awareness, no auto-detect |

**The gap:** Nobody auto-detects AND fixes the full range of problems for beginners in one tool.

---

## MARKET EVIDENCE

| Game | Evidence |
|---|---|
| War Thunder | VKB's own forum has dedicated threads. Multiple Steam discussions. |
| Elite Dangerous | Steam thread from years ago still getting replies: "ship just flips in circles" |
| DCS World | "Two controllers control your pitch axis at the same time and fight each other" |
| X4: Foundations | "Started after installing my new X52. If I unplugged it the problem went away" |
| Battlefield 6 | Community 56-link evidence pack — 12,900 upvotes, 12,000 views, 1,200 comments |

---

## FULL ROADMAP

| Phase | Version | What gets built |
|---|---|---|
| ✅ Done | v0.1 | Spin bug fix — War Thunder |
| ✅ Done | v0.3-alpha | Engine architecture, 4 modules, 98 VID/PID devices, win_compat shim |
| ✅ Done | v0.3-alpha | Knowledge Base tab in GUI (War Thunder, ED, Star Citizen cards) |
| ✅ Done | v0.3-alpha | Conductor module (22 problems), ACP v1, 3-tab GUI |
| ✅ Done | v0.3-alpha | AAFL loop engine (aafl_core, loop_manager, evaluator, researcher) |
| Next | v0.2 | Spin fix → Elite Dangerous + Star Citizen; ED Bind Reset prevention |
| Soon | v0.3 | win_hardener module (9 problems) |
| Soon | v0.4 | LM Studio + local AI wired in (Gemma 4 / Qwen2.5-VL) |
| Soon | v0.5 | ChromaDB vector memory — AI learns your setup |
| Future | v0.6 | Keybinding profile library — detect game, auto-install community profile |
| Future | v0.7 | AI learns preferences, builds custom profiles, warns about patch breakage |
| Future | v1.0 | Public release — any hardware, any game. Package as .exe (no Python needed). |

---

## HARDWARE & STACK

| Item | Detail |
|---|---|
| Joystick | VKB Gladiator NXT EVO (Right-hand), arrived 25 April 2026 |
| GPU | NVIDIA RTX 5090 (32GB VRAM) |
| RAM | 48GB DDR5 |
| OS | Windows 11 |
| Python | 3.14 at `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| Terminal | Run as Admin — Windows key + X → Terminal (Admin) |
| Claude Code | v2.1.119 — installed, working |
| LM Studio | v0.4.12 — models dir `D:\lm-models` |
| Gemma 4 | Loaded, Think mode OFF |
| Packages | mss, lmstudio, Pillow, anthropic, litellm, python-dotenv, langgraph, ddgs |
| API key | Windows environment variable `ANTHROPIC_API_KEY` |
| API model | claude-sonnet-4-6 |
| API cost | ~$0.003/screenshot (SFL agent). Claude Code much cheaper (text only). |
| Balance | $20.00 loaded 12/05/2026 |
| Console | https://console.anthropic.com/settings/billing |

---

## TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `python` not found | Use full path: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| `localhost:1234` refused | Use `127.0.0.1:1234` |
| LM Studio server drops | Don't reload models while server is running |
| Gemma 4 empty replies | Think mode eating tokens — Think OFF + MAX_TOKENS = 3000 |
| Model not found (404) | Model string must be `claude-sonnet-4-6` |
| Credits too low (400) | Top up at console.anthropic.com/settings/billing |
| Agent guesses wrong path | Path injection is in v3 — if broken, check PROJECT_HANDOVER.md is present |
| Task into PS prompt wrong order | Run agent first, THEN paste task at the `>` prompt |
| Claude Code auth conflict | Detected both claude.ai token + API key — uses API key. Working fine. |
| Cerebras model fails | Model renamed — llama3.1-70b no longer valid. Check Cerebras docs for new name. |
| loop_manager --once stops mid-loop | Normal: LLM call count hit cap. Fixed: max_loop_iters/max_llm_calls are now separate. |

---

## WHAT NOT TO DO

- Don't rebuild anything marked ✅ — it exists, find the file
- Don't add multiple games at once — one game, test fully, then next
- Don't use external packages unless absolutely necessary (Tkinter is sufficient for now)
- Don't commit to GitHub without Scott's explicit decision
- Don't auto-flash firmware — warn and guide only, never auto-flash
- Don't rebuild from scratch — extend what's there

---

## NEXT PRIORITIES

| # | Task | Tool |
|---|---|---|
| 1 | Wire evaluator.py into loop_manager.py result scoring | Claude Code |
| 2 | Wire researcher.py into loop planning step | Claude Code |
| 3 | Fix Cerebras provider model name (llama3.1-70b renamed) | Claude Code |
| 4 | win_hardener module (9 problems) | Claude Code |
| 5 | Star Citizen full support | Claude Code |
| 6 | Verify all 6 skills toggles ON at claude.ai/customize/skills | Manual |

---

## RESUME COMMAND

> "Continuing VKB Spin Doctor. Read PROJECT_HANDOVER.md v16. AAFL loop engine live — loop_manager.py --once tested and passing (Gemini Flash plan + Mistral Codestral work). evaluator.py and researcher.py built. Next: wire evaluator into loop_manager scoring, fix Cerebras model name, then win_hardener module."
