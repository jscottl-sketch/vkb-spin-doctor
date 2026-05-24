# MCC Full Guide — Mission Control Center

Last updated: 2026-05-24  
Server: `python mcc_server.py` → http://localhost:8080

---

## What is MCC?

MCC is a local web dashboard that sits in front of the VKB-SpinDoctor project. It saves your work, tracks AI runs, shows system health, and gives you one-click access to every part of the system. It replaces a dozen manual steps with single buttons.

---

## How to Start

```
python mcc_server.py
```

Then open `http://localhost:8080` in your browser.  
The green dot in the header means the server is live. The red dot means it is offline.

---

## Header

| Control | What it does |
|---|---|
| **MCC** title | Nothing — just a label |
| Green/Red dot | Live server indicator — auto-checks every 10 seconds |
| **Connect Data** button | Manually poll the server, load home screen, load instruments |
| **Auto-WCCS** toggle | Automatically saves your session every N minutes |
| **every N min** input | Set the auto-save interval (15–60 min) |

---

## Preset Bar

Lets you save and recall tab states.

| Control | What it does |
|---|---|
| Preset buttons | Click to jump to saved tab state |
| ✕ on each button | Delete that preset |
| Name input field | Type a name before saving |
| **Save** button | Save the current active tab as a named preset (`POST /presets/save`) |
| **Refresh** button | Reload the preset list from server (`GET /presets`) |

---

## Tabs

### 🏠 Home

Overview of the whole system. Auto-refreshes every 30 seconds.

**Quick Action Buttons:**

| Button | What it does | Endpoint |
|---|---|---|
| 🏥 Run Health Check | Runs `provider_health.py` in background | `POST /run-health-check` |
| 🔭 Start Scout | Starts Scout timer with default goal | `POST /scout-timer/start` |
| 🔄 Run AAFL Goal | Prompts for a goal, queues it | `POST /run-now` |
| 💾 Save WCCS | Saves current session to STATUS.md | `POST /api/wccs` |

**Instrument Row (6 gauges):**

| Instrument | What it shows | Endpoint |
|---|---|---|
| Provider Health gauge | % of green providers | `GET /health-status` |
| Show Details button | Expands per-provider list | `GET /health-status` |
| AAFL Score gauge | Last AI run score /10 | `GET /dashboard-data/aafl_runs.json` |
| Costs (7d) chart | Response-time bars for active providers | `GET /health-status` |
| Scout Activity sparkline | 7-day scout run count | `GET /dashboard-data/scout.json` |
| ALP Savings bar | Count of logged savings vs target | `GET /alp-data` |
| System Status lights | MCC / AAFL Engine / Scout green/yellow/red | multiple |

**Home Cards:** Click any card to jump to that tab.

**Refresh Cards** button — force-reloads all cards (`GET /dashboard-data/*.json`).

**Project Files section:**

| Button | What it does | Endpoint |
|---|---|---|
| 📋 Copy STATUS.md | Copies STATUS.md to clipboard | `GET /api/status` |
| 📋 Copy HISTORY.md | Copies HISTORY.md to clipboard | `GET /api/history` |

---

### 💾 WCCS (Write Claude Code Save)

This is the main save tab. Every session save writes STATUS.md and backs it up.

**Pill buttons (drill-down panels):**

| Pill | Panel | What it shows | Endpoint |
|---|---|---|---|
| Auto-Save Log | Table of last 20 saves from wccs_log.md | `GET /wccs/save-log` |
| History Search | Search HISTORY.md and ACCA.md | `GET /wccs/history-search?q=` |
| Session Logs | Browse session_logs/ folder | `GET /wccs/session-logs` |
| Rewind + Edit | Select old backup, edit, restore | `GET /wccs/versions`, `POST /wccs/restore` |
| Diff Viewer | Compare any two backups | `POST /wccs/diff` |

**Main controls:**

| Control | What it does | Endpoint |
|---|---|---|
| 💾 Save Session Now | Runs aafl_wccs.py, saves STATUS.md backup | `POST /api/wccs` |
| 📋 Copy STATUS.md for Claude | Copies STATUS.md to clipboard | `GET /api/status` |
| Auto-WCCS badge | Shows ON/OFF, links to header toggle | `GET /api/auto-wccs` |
| Next save countdown | Live countdown to next auto-save | — |

**Chat Summary textarea:** Paste your Claude chat summary here before clicking Save. The text is written to `chat_latest.txt` before the save runs. Optional but recommended.

**Recent Saves list:** Last 5 saves. Click any to open the Diff Viewer for that point.

**Feature Cards:** Shortcuts to the 5 drill-down panels plus Sunday Auto-Merge.

**Status Copy Reminder:** After a successful save, a flashing red banner appears reminding you to update the STATUS.md file in Claude Project Files.

---

### 📋 Kanban

Shows the project board from `dashboard_data/kanban.json`.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload kanban data | `GET /dashboard-data/kanban.json` |

---

### 🔄 AAFL Runs

Shows completed AI goal runs from `dashboard_data/aafl_runs.json`.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload AAFL run history | `GET /dashboard-data/aafl_runs.json` |
| Load (Retry Log) | Load retry log from health_results/ | `GET /retry-log` |

---

### 🔭 Scout

Web research runner powered by `chief_scout.py`.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload scout dashboard data | `GET /dashboard-data/scout.json` |

**Timed Scout section:**

| Control | What it does | Endpoint |
|---|---|---|
| Goal input | Topic for scout to research | — |
| Hours input | 0 = run indefinitely | — |
| Interval input | How often to run (minutes) | — |
| Start | Starts `scout_timer.py` in background | `POST /scout-timer/start` |
| Stop | Writes stop flag file | `POST /scout-timer/stop` |
| Status | Check if timer is running | `GET /scout-timer/status` |

**Source Library section:**

| Control | What it does | Endpoint |
|---|---|---|
| Filter by topic input | Filter sources | — |
| Load | Load filtered source library | `GET /sources-library?topic=` |
| Discover | Run scout in discovery mode | `POST /run-scout` |
| URL + Description inputs | New source to add | — |
| + Add Source | Adds URL to library | `POST /sources-library/add` |

---

### 💰 Costs

Shows cost data from `dashboard_data/costs.json`.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload cost data | `GET /dashboard-data/costs.json` |

---

### ⚙️ AAFL Control

Run AI goals, manage settings, clear stuck items.

**Run Now section:**

| Control | What it does | Endpoint |
|---|---|---|
| Goal text input | The goal to run | — |
| Provider dropdown | Choose AI provider or Auto | — |
| ▶ Run Now | Queues goal to `goal_queue.txt` | `POST /run-now` |
| Cost preview | Shows estimated tokens/cost/time | — (client-side) |

**Smart Suggester:**

| Control | What it does | Endpoint |
|---|---|---|
| Suggest Provider | Analyses goal and suggests best provider | `POST /suggest-provider` |

**Chain Mode:**

| Control | What it does | Endpoint |
|---|---|---|
| Run Chain | Runs `chain_runner.py` with the goal | `POST /run-chain` |
| Status | Shows chain running/last goal | `GET /chain-status` |
| Log | Shows last 10 chain run entries | `GET /chain-log` |

**AAFL Settings:**

| Control | What it does | Endpoint |
|---|---|---|
| Confidence Threshold | Min score to accept (0–10) | — |
| Cost Cap (USD) | Max spend per goal | — |
| Max Retries | How many times to retry | — |
| Load | Load current settings | `GET /aafl-settings` |
| Save | Save settings to `aafl_config.json` | `POST /aafl-settings` |

**Stuck Inbox:**

Goals that failed too many times. Severity pills show High/Med/Low counts.

| Control | What it does | Endpoint |
|---|---|---|
| Bulk Resolve All | Marks all stuck items resolved | `POST /stuck-inbox/bulk-resolve` |
| Resolve (per item) | Marks one item resolved | `POST /resolve-stuck` |

---

### 🧠 Memory

Read-only view of the knowledge database (`data/knowledge_engine.db`).

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload all three tables | `GET /memory/knowledge`, `GET /memory/solutions`, `GET /memory/sources` |
| Knowledge Bank search | Filter rows by any text | — (client-side) |
| Solution Log search | Filter solution rows | — (client-side) |

**Three tables:**
- **Knowledge Bank** — learnt facts, titles, sources
- **Solution Log** — past AI solutions with scores and providers
- **Source Reputation** — domain URLs with trust scores

---

### ⭐ Promo

High-scoring AI results (≥9.0) auto-queue here for human review.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload promo queue | `GET /promo-queue` |
| ✓ Approve | Marks item approved | `POST /approve-promo` |
| ✗ Reject | Marks item rejected | `POST /reject-promo` |

Both actions support Undo (10s window).

---

### ⚡ Instructions & Codes (ACCA Tab)

Two sections: (1) plain-English instructions for every tab, and (2) ACCA shorthand codes.

**ACCA Codes table:**

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload codes from ACCA.md | `GET /acca-codes` |
| Search box | Filter codes by any text | — (client-side) |

Codes are parsed from `ACCA.md` pipe-table format.

---

### 🛡️ ALP (Accrued Learning Points)

Tracks money/time savings from this project.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload ALP database | `GET /alp-data` |
| Entry input | Describe the saving | — |
| + Add Entry | Appends row to `ALP_Database.md` | `POST /alp-add` |

Supports Undo (10s window — but file cannot auto-delete, message tells you to remove manually).

---

### 💽 Storage

Monitor disk quota slots defined in `storage_config.json`.

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload slot data | `GET /storage` |
| Weekly Report | Load weekly storage report | `GET /storage/report` |

Each slot shows a bar: used GB / quota GB, colour-coded green/amber/red.

---

### 🔧 Self-Diagnosis

Internal system health cockpit.

**Section 1: Last MOT Results**

| Control | What it does | Endpoint |
|---|---|---|
| 🔍 Run Full MOT | Runs `mcc_full_mot.py`, shows pass rate | `POST /run-mot` |
| Score + bar | Pass % from last MOT report | — |
| Failure list | Shows which tests failed | — |

**Section 1b: Module Manager**

| Control | What it does | Endpoint |
|---|---|---|
| Refresh | Reload module list | `GET /modules` |
| Checkbox per module | Enable/disable a module | `POST /toggle-module` |

**Section 2: Known Issues**

| Control | What it does | Endpoint |
|---|---|---|
| Description input | Issue description | — |
| Severity dropdown | Low / Medium / High | — |
| + Add | Adds issue to `known_issues.json` | `POST /known-issues` (action: add) |
| Mark Fixed | Changes status to fixed | `POST /known-issues` (action: set_status) |
| Reopen | Changes status back to open | `POST /known-issues` (action: set_status) |
| Delete | Removes issue | `POST /known-issues` (action: delete) |

**Section 3: System Info** — auto-populated from `/self-diagnosis`:
Python version, project path, file count, line count, disk usage, last git commit.

**Section 4: File Health Table** — all `.py` files, sortable by name/lines/modified/import status.

---

## Keyboard Shortcuts

| Key | Action |
|---|---|
| 1–9 | Jump to tab 1–9 |
| R | Refresh current tab |
| C | Connect Data |
| Esc | Close dialog/overlay |
| Shift+? | Show keyboard help |

---

## Data Flow

### How a WCCS save works

```
1. You paste chat summary into WCCS tab textarea
2. Click "Save Session Now"
3. POST /api/wccs  →  server writes chat to chat_latest.txt
4. Server runs aafl_wccs.py
5. aafl_wccs.py updates STATUS.md + HISTORY.md
6. Server copies STATUS.md → archive_dead/STATUS_YYYYMMDD_HHMMSS.md
7. MCC shows "PASS" toast + flashing reminder to update Claude Project Files
8. You click "Copy STATUS.md for Claude" → clipboard
9. Go to Claude.ai → Project Files → delete old STATUS.md → paste new one
```

### How Auto-WCCS works

```
Header toggle ON  →  POST /api/auto-wccs {"action":"start","interval":30}
Every N minutes:  →  server fires _auto_wccs_fire() in background thread
                  →  runs aafl_wccs.py
                  →  logs result to _auto_wccs_log (last 5 entries)
Toggle OFF        →  POST /api/auto-wccs {"action":"stop"}
```

### How handover data reaches MCC

```
WCCS save        →  STATUS.md updated by aafl_wccs.py
Timeline         →  GET /api/timeline scans archive_dead/STATUS_*.md
Dashboard cards  →  GET /dashboard-data/*.json (written by external scripts)
ACCA codes       →  GET /acca-codes parses ACCA.md pipe-table
ALP entries      →  GET /alp-data parses ALP_Database.md pipe-table
```

### What auto-populates vs what needs manual action

| Auto-populates | Needs manual action |
|---|---|
| Server status dot (10s poll) | Paste chat summary before save |
| Home instruments (30s refresh) | Click Save Session Now |
| WCCS countdown timer | Click Copy STATUS.md after save |
| Dashboard cards (30s refresh) | Update Claude Project Files |
| ACCA codes (from ACCA.md) | Add new ACCA codes to ACCA.md directly |
| ALP entry count | Click + Add Entry for each saving |
| MOT score (after you run it) | Click Run Full MOT manually |

---

## Complete Endpoint Reference

### GET endpoints

| Endpoint | Returns | Used by |
|---|---|---|
| `GET /` | mission_control.html | Browser navigation |
| `GET /status` | Last WCCS result, last capture time | Server dot check |
| `GET /captures` | chat_latest.txt content | WCCS tab |
| `GET /scout-result` | Scout output text | Scout tab |
| `GET /scout-config` | Scout config JSON | Scout tab |
| `GET /scout-presets` | Scout presets list | Scout tab |
| `GET /aafl-status` | AAFL running status + DB last run | AAFL Control |
| `GET /aafl-queue` | goal_queue.txt parsed | AAFL Control |
| `GET /aafl-config` | aafl_control_config.json | AAFL Control |
| `GET /aafl-providers` | Provider list from config | AAFL Control |
| `GET /api/timeline` | Backup history with stats | WCCS tab |
| `GET /api/backup?f=` | Single backup file content | Rewind panel |
| `GET /api/diff?a=&b=` | Diff hunks between two files | Diff viewer |
| `GET /api/session-logs` | archive_dead/session_logs/ list | Sessions panel |
| `GET /api/session-log?f=` | Single session log content | Sessions panel |
| `GET /api/search?q=&section=` | Search HISTORY.md + ACCA.md | Search tab |
| `GET /api/auto-wccs` | Auto-WCCS state + log | Header + WCCS tab |
| `GET /health-status` | Provider health from JSON | Provider Health |
| `GET /dashboard-data/` | List JSON files in dashboard_data/ | Home screen |
| `GET /dashboard-data/<file>` | Serve specific dashboard JSON | Home cards |
| `GET /stuck-inbox` | Non-resolved stuck items | AAFL Control |
| `GET /memory/knowledge` | knowledge DB rows | Memory tab |
| `GET /memory/solutions` | solution_log DB rows | Memory tab |
| `GET /memory/sources` | source_reputation DB rows | Memory tab |
| `GET /promo-queue` | promo_queue.json items | Promo tab |
| `GET /acca-codes` | ACCA.md parsed codes | ACCA tab |
| `GET /alp-data` | ALP_Database.md parsed rows | ALP tab |
| `GET /self-diagnosis` | System info + file list + MOT | Self-Diagnosis |
| `GET /known-issues` | known_issues.json | Self-Diagnosis |
| `GET /modules` | module_registry.json | Self-Diagnosis |
| `GET /presets` | Presets from preset_manager | Preset bar |
| `GET /presets/load?name=` | Single preset state | Preset bar |
| `GET /aafl-settings` | aafl_config.json settings | AAFL Control |
| `GET /retry-log` | retry_log.json | AAFL Runs tab |
| `GET /chain-status` | chain_runner status | AAFL Control |
| `GET /chain-log` | chain_log.json | AAFL Control |
| `GET /scout-timer/status` | scout_timer status | Scout tab |
| `GET /sources-library` | sources_library.json | Scout tab |
| `GET /stuck-inbox/summary` | Severity counts | AAFL Control |
| `GET /storage` | Storage slot data | Storage tab |
| `GET /storage/report` | Weekly storage report | Storage tab |
| `GET /wccs/save-log` | wccs_log.md last 20 entries | WCCS drill-down |
| `GET /wccs/history-search?q=` | Search HISTORY+ACCA | WCCS drill-down |
| `GET /wccs/session-logs` | session_logs/ with content | WCCS drill-down |
| `GET /wccs/versions` | archive_dead STATUS backups | WCCS drill-down |
| `GET /api/status` | STATUS.md full content | Copy button, MCP |
| `GET /api/history` | HISTORY.md full content | Copy button, MCP |
| `GET /api/acca` | ACCA.md full content | MCP |
| `GET /api/health` | Quick health summary | MCP |

### POST endpoints

| Endpoint | Body | Does |
|---|---|---|
| `POST /wccs` | raw text | Write chat → run wccs_runner.py |
| `POST /capture` | raw text | Append to chat_latest.txt |
| `POST /run-scout` | `{goal?, ...}` | Run chief_scout.py in background |
| `POST /scout-config` | config object | Merge into chief_scout_config.json |
| `POST /run-aafl` | — | Run loop_manager.py --once in background |
| `POST /set-aafl-goal` | `{goal}` | Write goal.txt + update aafl config |
| `POST /aafl-queue` | `{goal}` | Append to goal_queue.txt |
| `POST /aafl-config` | config object | Merge into aafl_control_config.json |
| `POST /stop-aafl` | — | Terminate AAFL subprocess |
| `POST /api/wccs` | `{chat?}` | Main save: run aafl_wccs.py |
| `POST /api/restore` | `{filename, content?}` | Restore STATUS.md from backup |
| `POST /api/auto-wccs` | `{action, interval}` | Start/stop auto-WCCS timer |
| `POST /resolve-stuck` | `{item_id}` | Mark stuck item resolved |
| `POST /run-now` | `{goal}` | Append goal to goal_queue.txt |
| `POST /approve-promo` | `{item_id}` | Mark promo item approved |
| `POST /reject-promo` | `{item_id}` | Mark promo item rejected |
| `POST /alp-add` | `{entry}` | Append row to ALP_Database.md |
| `POST /run-mot` | — | Run mcc_full_mot.py, return report |
| `POST /known-issues` | `{action, ...}` | Add/delete/set_status on known_issues.json |
| `POST /run-health-check` | — | Run provider_health.py in background |
| `POST /run-merge-sessions` | — | Run merge_sessions.py in background |
| `POST /toggle-module` | `{id, enabled}` | Toggle module via module_loader |
| `POST /presets/save` | `{name, state}` | Save preset via preset_manager |
| `POST /presets/delete` | `{name}` | Delete preset via preset_manager |
| `POST /aafl-settings` | settings object | Merge into aafl_config.json |
| `POST /suggest-provider` | `{goal}` | smart_suggester → suggested provider |
| `POST /run-chain` | `{goal}` | Run chain_runner.py in background |
| `POST /scout-timer/start` | `{goal, hours, interval_minutes}` | Start scout_timer.py |
| `POST /scout-timer/stop` | — | Write scout_timer_stop.flag |
| `POST /sources-library/add` | `{url, domain, description, tags}` | Add source via source_library_manager |
| `POST /stuck-inbox/bulk-resolve` | `{item_ids}` | Bulk resolve via stuck_inbox module |
| `POST /wccs/restore` | `{filename, content?}` | Restore STATUS.md (WCCS drill-down) |
| `POST /wccs/diff` | `{a, b}` | Diff two archive files (WCCS drill-down) |

### DELETE endpoints

| Endpoint | Body | Does |
|---|---|---|
| `DELETE /aafl-queue` | `{index}` | Comment out that line in goal_queue.txt |

---

## File Locations

| File | Purpose |
|---|---|
| `STATUS.md` | Current project state — updated every save |
| `HISTORY.md` | Running history log |
| `ACCA.md` | Shorthand codes table |
| `ALP_Database.md` | Accrued savings log |
| `chat_latest.txt` | Clipboard for chat text before save |
| `goal_queue.txt` | Queue of AAFL goals to process |
| `goal.txt` | Current single AAFL goal |
| `aafl_control_config.json` | AAFL engine config |
| `aafl_config.json` | AAFL settings (confidence, cost cap, etc.) |
| `stuck_inbox.json` | Failed/stuck goal items |
| `promo_queue.json` | High-scoring items awaiting review |
| `chief_scout_config.json` | Scout configuration + presets |
| `data/knowledge_engine.db` | SQLite: knowledge, solutions, source rep |
| `dashboard_data/*.json` | Card data for home screen |
| `health_results/latest_health.json` | Provider health results |
| `archive_dead/STATUS_*.md` | STATUS.md backup history |
| `archive_dead/session_logs/*.md` | Archived session logs |
| `session_logs/*.md` | Current session logs |
| `wccs_log.md` | WCCS save history log |
