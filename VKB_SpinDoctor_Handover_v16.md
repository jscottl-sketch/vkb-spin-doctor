# VKB Spin Doctor — Project Handover v16 (MASTER)

**Owner:** Scott (Croydon, England)
**Status:** AI Control Panel built. Model Router live. 3 AI models downloading. GUI 3 tabs working. ACP v1 in sfl_agent.
**Last updated:** 13 May 2026
**Consolidates:** v11 → v15 + today's session

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
| ALP | Allowance Preservation — save money, spend only when necessary |
| CA | Completely Automate — build software that does the task end to end, zero input needed |
| + | Combine codes |
| = | Define a new code |

Modes: TBLM (troubleshoot), DDM (deep dive), BGM (beginner), BPM (battle plan), NRM (no-repeat), EM (evidence)

---

## PROJECT PRIORITIES — NEW FRAMEWORK (set 13 May 2026)

| Priority | Name | Rule |
|---|---|---|
| 1 — ALP | Allowance Preservation | Every decision on every Anthropic tool — cheapest path first. If it costs more than it generates, it stops. |
| 2 — Big SFL | Universal AI agent | Masterminds Spin Doctor. Must pass ALP check before every action. |
| 3 — ACCA Code | Shorthand system | Grows as byproduct. Sorted later in its own project. |
| 4 — Spin Doctor VKB | The product | Resumes once Big SFL can run it. Anything that accelerates the build jumps the queue. |

**Rule:** Everything in priority 2, 3, 4 must pass priority 1 (ALP) first.

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
| sfl_agent.py v3 — ACP v1 + handover injection | ✅ 575 lines, all tests green |
| Claude Code v2.1.119 | ✅ Installed, working |
| Elite Dangerous spin fix | ✅ Fixed at hardware level via VKB DevConfig |
| model_router.py — routes tasks to cheapest AI | ✅ Built 13/05/2026 |
| control_panel.py — plain English GUI, AI info dropdowns | ✅ Built 13/05/2026 |
| full_auto_setup.py — CA downloads + setup | ✅ Built 13/05/2026 |
| setup_router.py — model download + API key setup | ✅ Built 13/05/2026 |
| task_db.json — task-to-model routing database | ✅ Created on Scott's machine |
| Qwen2.5-VL 32B download (Vision AI) | 🔄 Downloading now (~21GB) |
| Qwen2.5-Coder 32B download (Code AI) | 🔄 Queued |
| Phi-4 14B download (Fast AI local) | 🔄 Queued |
| DeepSeek R1 70B (Thinking AI) | ✅ Already on machine |
| Groq API key (Fast AI online) | ❌ Not set — get free at console.groq.com |
| Gemini API key (Vision backup) | ❌ Not set — get free at aistudio.google.com/apikey |
| Orchestrator (manager AI layer) | ⏸ Next build |
| Throttle slider in War Thunder | ⏸ Open (likely PS5/Xbox conflict — unplug and retry) |
| ED Bind Reset prevention | ⏸ v0.2 |
| Star Citizen full support | ⏸ Waiting |
| Rename handover constant → PROJECT_HANDOVER.md | ⏸ Quick Claude Code job |

---

## AI CONTROL PANEL — WHAT WAS BUILT TODAY

### Architecture — 3 layers

```
Layer 1 — Orchestrator (NOT YET BUILT)
  Takes a goal → breaks into tasks → delegates → reports back
  Brain: DeepSeek R1 70B (free, local)

Layer 2 — Model Router  (model_router.py) ✅
  Takes a task → picks cheapest AI → escalates if it fails → logs result
  Paid API OFF by default — toggle required

Layer 3 — AI Models
  Vision AI  — Qwen2.5-VL 32B     (local, free)
  Code AI    — Qwen2.5-Coder 32B  (local, free)
  Thinking AI— DeepSeek R1 70B    (local, free)
  Fast AI    — Llama 3.3 70B Groq (online, free)
  Fallback   — Claude Sonnet      (paid, OFF by default)
```

### Files built today

| File | What it does |
|---|---|
| `full_auto_setup.py` | CA — downloads all models, creates task_db.json, starts LM Studio, tests router. Zero prompts. |
| `setup_router.py` | Interactive setup — downloads models, asks for API keys |
| `model_router.py` | Routes any task to cheapest model. Logs to task_db.json. Importable from any script. |
| `control_panel.py` | Plain English GUI. Click AI cards for dropdowns. Switch project button. Paid API toggle. |
| `panel_config.json` | Auto-created. Stores project name/path. Edit to switch projects. |
| `task_db.json` | Auto-created. Task types → model chains. Logs every call. Gets smarter over time. |

### How the router works

1. Task comes in as text
2. Keywords matched against task_db.json — FREE, no API call
3. Cheapest model tried first
4. If it fails → next model tried automatically
5. Paid models skipped unless toggle is ON
6. Every result logged — success rate tracked per model

### Task types and keywords

| Type | Triggered by |
|---|---|
| vision | screenshot, screen, image, see, look, UI, window, visual, game, display |
| code | python, code, write, edit, file, function, bug, fix, .py, script, .blk, .xml |
| plan | plan, strategy, should, how to, decide, architect, design, best way, roadmap |
| fast | everything else (catch-all) |

### How to use router from any script

```python
from model_router import ModelRouter
router = ModelRouter()
response = router.run("Write a Python function to read a .blk file")
print(response)

# Turn paid API on if needed
router.toggle_paid(True)

# Check stats
router.stats()
router.cost_report()
```

### How to add a new task type

```python
router.add_task_type(
    name        = "game_config",
    description = "Read or edit game config files",
    keywords    = [".blk", ".binds", "config", "keybind"],
    models      = [
        {"name": "qwen2.5-coder-32b-instruct", "provider": "lmstudio",  "cost_per_call": 0,    "attempts": 0, "successes": 0},
        {"name": "llama-3.3-70b-versatile",    "provider": "groq",      "cost_per_call": 0,    "attempts": 0, "successes": 0},
        {"name": "claude-sonnet-4-6",           "provider": "anthropic", "cost_per_call": 0.01, "attempts": 0, "successes": 0},
    ]
)
```

### How to use control panel on a different project

Option A — point it at a folder:
```
python control_panel.py --project "C:\path\to\project"
```

Option B — click Switch Project button inside the panel. Saves choice to panel_config.json.

Option C — edit panel_config.json directly.

---

## FREE AI MODELS — RANKED BEST TO WORST

| Rank | Model | Label | Best for | VRAM | Cost |
|---|---|---|---|---|---|
| 1 | Qwen2.5-VL 32B | Vision AI | Reads game UIs, screenshots | 20GB | FREE local |
| 2 | Qwen2.5-Coder 32B | Code AI | Writes/fixes Python | 20GB | FREE local |
| 3 | Groq Llama 3.3 70B | Fast AI | Quick tasks, 500 tok/sec | None | FREE online |
| 4 | DeepSeek R1 70B | Thinking AI | Planning, reasoning | 28GB | FREE local |
| 5 | Gemini 2.5 Pro | Vision backup | Vision when Qwen offline | None | FREE online |
| 6 | Phi-4 14B | Fast local | Quick tasks without internet | 9GB | FREE local |
| 7 | Gemma 4 | Old fallback | Last resort only | low | FREE local |

---

## ALP COST MAP — CHEAPEST TO MOST EXPENSIVE

| Job | Cheapest tool | Cost | Fallback |
|---|---|---|---|
| Write/edit Python | Qwen2.5-Coder 32B local | FREE | Groq Llama 3.3 → Claude Code API |
| Read game UI | Qwen2.5-VL 32B local | FREE | Gemini free → SFL + Claude API |
| Plan/decide | DeepSeek R1 70B local | FREE | Groq Llama → this chat |
| Quick question | Groq Llama 3.3 | FREE | Phi-4 local |
| This chat | Claude.ai Pro | Flat fee already paid | — |

---

## BIG VISION

Not a VKB-specific tool. A **universal input device assistant** — any hardware, any game, one tool.

> *"The tool that should have existed the moment the first joystick was ever plugged into a PC."*

**The core product:** Steam "Generic Gamepad Configuration Support" silently breaks joysticks for millions of players. Fix = uncheck one box. Nobody has built a tool that does this automatically. That's Spin Doctor.

---

## HOW TO RUN EVERYTHING

### Control Panel (new — recommended)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe control_panel.py
```

### Full Auto Setup (run once or after reinstall)
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe full_auto_setup.py
```

### Claude Code
Admin terminal (Windows key + X → Terminal (Admin)):
```
cd "C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor"
claude
```

### SFL Agent
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe sfl_agent.py
```
With budget:
```
C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe sfl_agent.py --budget 30k
```

### Spin Doctor GUI
Double-click `RUN_VKB.bat`

---

## PROJECT FILES — COMPLETE

```
VKB-SpinDoctor/
├── spin_doctor.py                     # ~1057 lines. Tabs: Fix / Conductor / Knowledge Base
├── sfl_agent.py                       # v3 — 575 lines. ACP v1 + handover injection
├── sl_loop.py                         # Gemma 4 local SFL (old)
├── RUN_VKB.bat                        # Double-click launcher
├── control_panel.py                   # ✅ NEW — Universal AI Control Panel GUI
├── model_router.py                    # ✅ NEW — Routes tasks to cheapest AI
├── full_auto_setup.py                 # ✅ NEW — CA full setup, zero prompts
├── setup_router.py                    # ✅ NEW — Interactive setup
├── task_db.json                       # ✅ NEW — Task-to-model routing database
├── panel_config.json                  # ✅ NEW — Project switcher config
├── .env                               # ✅ NEW — API keys (Groq, Gemini)
├── Universal_Input_Device_Database.md # 44 problems, all hardware types
├── VKB_SpinDoctor_Handover_v16.md     # THIS FILE — sfl_agent reads this
├── problems/
│   ├── __init__.py
│   ├── spin_fix.py                    # Module 01 ✅
│   ├── usb_power_saver.py             # Module 02 ✅
│   ├── steam_input_conflict.py        # Module 03 ✅
│   └── conductor.py                   # Module 04 ✅ 619 lines
├── core/
│   └── win_compat.py                  # pywin32 shim
├── data/
│   └── devices.json                   # 98 devices with VID/PID lookup
├── backups/                           # Auto-snapshots
└── sfl_logs/                          # Agent session logs
```

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
| DeepSeek R1 70B | Already downloaded to D:\lm-models |
| Qwen2.5-VL 32B | Downloading — 21GB |
| Qwen2.5-Coder 32B | Queued download — 20GB |
| Phi-4 14B | Queued download — 8GB |
| D: drive free | 5.28TB — plenty of space |
| Packages | mss, lmstudio, Pillow, anthropic, requests |
| API key | Windows environment variable `ANTHROPIC_API_KEY` |
| API model | claude-sonnet-4-6 |
| API cost | ~$0.003/screenshot (SFL). Claude Code cheaper. Router free by default. |
| Balance | $20.00 loaded 12/05/2026 |
| Console | https://console.anthropic.com/settings/billing |

---

## API KEYS STATUS

| Key | Status | Where to get |
|---|---|---|
| ANTHROPIC_API_KEY | ✅ Set (Windows env var) | Already done |
| GROQ_API_KEY | ❌ Missing | console.groq.com — free, no card |
| GEMINI_API_KEY | ❌ Missing | aistudio.google.com/apikey — free |

Both missing keys go in `.env` file in project folder. Run `setup_router.py` to add them interactively.

---

## ENGINE ARCHITECTURE — MICROKERNEL (Spin Doctor modules)

| Module ID | Name | Status |
|---|---|---|
| spin_fix | Spin Bug fix | ✅ Working (War Thunder) |
| usb_power_saver | USB Power Saver | ✅ Built |
| steam_input_conflict | Steam Input | ✅ Built |
| conductor | Process Conductor (22 problems) | ✅ Built |
| win_hardener | Windows Hardener (9 problems) | ⏸ v0.2 |
| identity | Device Identity (7 problems) | ⏸ v0.3 |
| config | Config Mediator (6 problems) | ⏸ v0.2 |
| physical | Physical Diagnostics (5 problems) | ⏸ v0.4 |

---

## GAME CONFIG FILE PATHS

| Game | Path | Format |
|---|---|---|
| War Thunder | `C:\Users\jscot\OneDrive\My Documents\My Games\WarThunder\Saves\226494292\production\` | .blk |
| Elite Dangerous | `C:\Users\jscot\AppData\Local\Frontier Developments\Elite Dangerous\Options\Bindings\` | .binds (XML) |
| Star Citizen | `C:\Program Files\Roberts Space Industries\StarCitizen\LIVE\USER\Client\0\Controls\Mappings\` | .xml |
| Arma Reforger | `Documents\My Games\ArmaReforger\profile\.save\settings\customInputConfigs\` | .json |

---

## TROUBLESHOOTING

| Problem | Fix |
|---|---|
| `python` not found | Use full path: `C:\Users\jscot\AppData\Local\Python\pythoncore-3.14-64\python.exe` |
| `localhost:1234` refused | Use `127.0.0.1:1234` |
| LM Studio server drops | Don't reload models while server is running |
| Model not found (404) | Model string must be `claude-sonnet-4-6` |
| Credits too low (400) | Top up at console.anthropic.com/settings/billing |
| Router says all models failed | LM Studio not running or no model loaded. Start server, load a model. |
| Groq fails | GROQ_API_KEY missing in .env — run setup_router.py |
| Model download fails in full_auto_setup | Use LM Studio app to download manually. Search: qwen/qwen2.5-coder-32b |
| control_panel shows Router not loaded | task_db.json missing — run full_auto_setup.py first |

---

## WHAT NOT TO DO

- Don't rebuild anything marked ✅ — it exists, find the file
- Don't add multiple games at once — one game, test fully, then next
- Don't use external packages unless necessary
- Don't commit to GitHub without Scott's decision
- Don't auto-flash firmware — warn and guide only
- Don't rebuild from scratch — extend what's there
- Don't turn Paid API on unless free models have genuinely failed

---

## NEXT PRIORITIES

| # | Task | Tool | Notes |
|---|---|---|---|
| 1 | Wait for model downloads to finish | Automatic | full_auto_setup.py running |
| 2 | Get Groq API key | Manual | console.groq.com — free, 2 mins |
| 3 | Test control_panel.py — send first task | Manual | Load a model in LM Studio first |
| 4 | Build Orchestrator (manager AI layer) | Claude Code | DeepSeek R1 as brain |
| 5 | Get Gemini API key | Manual | aistudio.google.com/apikey — free |
| 6 | ED spin fix — Elite Dangerous | Claude Code | |
| 7 | ED Bind Reset prevention | Claude Code | |
| 8 | win_hardener module | Claude Code | |

---

## RESUME COMMAND

> "Continuing VKB Spin Doctor + Universal AI Control Panel. Read Handover v16. Model router built (model_router.py). Control panel built with AI info dropdowns and project switcher (control_panel.py). Models downloading via full_auto_setup.py. Groq + Gemini keys still needed. Next: wait for downloads, get Groq key, test control panel, then build Orchestrator layer."
