# Knowledge Engine — Database Schema v1

**Project:** VKB Spin Doctor / AAFL / Software of Everything
**Owner:** Scott
**Created:** 15 May 2026
**Purpose:** Universal database schema. Every component stores here, reads from here. One brain for all projects.

---

## Design Principles

1. **Everything is a knowledge entry** — research findings, loop attempts, ACCA codes, device data, game configs, errors, fixes. All stored the same way.
2. **Tags make it flexible** — no rigid categories. Tag anything with anything. New project? New tags. No schema changes needed.
3. **Two layers** — SQLite for structured queries ("show me all entries tagged 'elite-dangerous' scored above 7"). ChromaDB for semantic search ("find me anything similar to this joystick drift problem").
4. **Every component reads and writes here** — Researcher, Worker, Evaluator, Reflector, Loop Manager, UI. One source of truth.
5. **Project-agnostic** — zero hardcoded project names. Works for VKB, works for the next thing, works for anything.

---

## SQLite Tables

### 1. knowledge

The core table. Everything lives here.

| Column | Type | Purpose |
|---|---|---|
| id | TEXT (UUID) | Unique ID |
| created_at | DATETIME | When it was stored |
| updated_at | DATETIME | Last modified |
| project | TEXT | Which project ("vkb", "aafl", "acca", or any future one) |
| source_type | TEXT | Where it came from: "research", "loop_attempt", "manual", "import" |
| source_url | TEXT (nullable) | URL if from web research |
| title | TEXT | Short description |
| content | TEXT | The actual knowledge — summary, code, finding, whatever |
| quality_score | REAL (nullable) | 0-10 rating from Evaluator. NULL if not scored |
| status | TEXT | "active", "superseded", "discarded" |
| parent_id | TEXT (nullable) | Links to the entry this was built from (for iteration chains) |
| metadata | TEXT (JSON) | Anything extra — flexible bag for future needs |

### 2. tags

Flexible tagging. Any entry can have any number of tags.

| Column | Type | Purpose |
|---|---|---|
| id | INTEGER | Auto-increment |
| knowledge_id | TEXT | FK → knowledge.id |
| tag | TEXT | The tag: "elite-dangerous", "joystick", "spin-bug", "fix", "acca-code", "device" |

### 3. loop_runs

One row per Loop session (overnight run, multi-day run, etc).

| Column | Type | Purpose |
|---|---|---|
| id | TEXT (UUID) | Unique run ID |
| started_at | DATETIME | When the loop started |
| ended_at | DATETIME (nullable) | When it stopped (NULL if still running) |
| goal | TEXT | What Scott asked it to do |
| goal_met | BOOLEAN | Did it succeed? |
| total_iterations | INTEGER | How many cycles it ran |
| best_score | REAL (nullable) | Highest score achieved |
| best_attempt_id | TEXT (nullable) | FK → knowledge.id of the best attempt |
| total_cost | REAL | Total £ spent (should be 0.00 most of the time) |
| stop_reason | TEXT | "goal_met", "killed", "stagnated", "budget", "max_iterations" |
| config | TEXT (JSON) | The rules/config used for this run |

### 4. research_jobs

One row per research enquiry.

| Column | Type | Purpose |
|---|---|---|
| id | TEXT (UUID) | Unique job ID |
| started_at | DATETIME | When research began |
| ended_at | DATETIME (nullable) | When it finished |
| topic | TEXT | What to research |
| rules | TEXT (JSON) | The rules for this job (see Rules Format below) |
| status | TEXT | "running", "paused", "complete", "stopped" |
| total_pages_fetched | INTEGER | How many pages it read |
| total_entries_created | INTEGER | How many knowledge entries it produced |
| total_duplicates_skipped | INTEGER | How many it discarded as duplicates |

### 5. acca_codes

The ACCA code database. Grows naturally.

| Column | Type | Purpose |
|---|---|---|
| code | TEXT (PK) | The shortcode: "ALP", "AAFL", "SFL" |
| meaning | TEXT | Full expansion |
| category | TEXT | "mode", "action", "operator", "status", "retired" |
| created_at | DATETIME | When it was added |
| retired | BOOLEAN | FALSE by default. TRUE if replaced |
| replaced_by | TEXT (nullable) | If retired, what replaced it |
| notes | TEXT (nullable) | Any extra context |

### 6. devices

Migrated from devices.json (98 entries). Grows as new hardware is discovered.

| Column | Type | Purpose |
|---|---|---|
| id | INTEGER | Auto-increment |
| vid | TEXT | Vendor ID (USB) |
| pid | TEXT | Product ID (USB) |
| vendor_name | TEXT | e.g. "VKB", "Thrustmaster", "Logitech" |
| product_name | TEXT | e.g. "Gladiator NXT EVO" |
| device_type | TEXT | "joystick", "throttle", "wheel", "pedals", "controller", "mouse" |
| known_issues | TEXT (JSON) | Array of known problem IDs |
| metadata | TEXT (JSON) | Anything else — firmware versions, notes |

### 7. cost_log

ALP tracking. Every penny accounted for.

| Column | Type | Purpose |
|---|---|---|
| id | INTEGER | Auto-increment |
| timestamp | DATETIME | When the cost was incurred |
| component | TEXT | "researcher", "worker", "evaluator", "reflector" |
| provider | TEXT | "local", "cerebras", "groq", "anthropic" etc |
| model | TEXT | Which model was used |
| tokens_in | INTEGER | Input tokens |
| tokens_out | INTEGER | Output tokens |
| cost_gbp | REAL | Cost in £. Should be 0.00 for local/free |
| task_ref | TEXT (nullable) | FK → knowledge.id or loop_runs.id |

---

## ChromaDB Collections

Alongside SQLite, ChromaDB stores vector embeddings for semantic search.

| Collection | What it embeds | Use case |
|---|---|---|
| knowledge_vectors | content field from knowledge table | "Find me anything similar to this problem" |
| research_vectors | Summaries from research jobs | "What did we find about joystick drift?" |

Each ChromaDB entry stores: the embedding vector + the knowledge.id as metadata, so you can look up the full entry in SQLite.

Embedding model: runs locally on RTX 5090 (e.g. nomic-embed-text via LM Studio) = £0.

---

## Research Rules Format (YAML)

Each research job gets a rules file. Plain text, no code knowledge needed.

```yaml
topic: "Elite Dangerous joystick configuration"
subtopics:
  - "spin bug fix"
  - "axis mapping"
  - "deadzone settings"

filters:
  date_after: "2024-01-01"
  domains_include: []              # empty = allow all
  domains_exclude:
    - "pinterest.com"
    - "facebook.com"
  must_contain_any:
    - "joystick"
    - "HOTAS"
    - "controller"
  language: "en"

quality:
  min_score: 5                     # discard anything below 5/10
  prefer_official_docs: true       # boost score for official sources
  prefer_code_examples: true       # boost score if contains code

depth:
  max_links_deep: 2                # follow links 2 levels from search results
  max_pages_per_subtopic: 100
  max_total_pages: 500

rate_limit:
  seconds_between_requests: 10     # 1 request per 10 seconds
  search_engine_rotation:
    - "duckduckgo"
    - "brave"

stop_conditions:
  max_hours: 72                    # stop after 3 days
  no_new_info_after: 50            # stop if 50 pages in a row add nothing new
  manual_stop_file: "STOP_RESEARCH"  # create this file to stop immediately

output:
  save_to_database: true
  export_summary: true             # generate a summary report at the end
  summary_format: "markdown"
```

---

## How Every Component Connects

```
┌─────────────────────────────────────────────┐
│                 SCOTT (UI)                   │
│          Streamlit on localhost               │
│   Search, browse, filter, export, set goals  │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│            KNOWLEDGE ENGINE                  │
│         SQLite + ChromaDB                    │
│     The single brain. Everything lives here  │
└──┬───────┬───────┬───────┬───────┬──────────┘
   │       │       │       │       │
   ▼       ▼       ▼       ▼       ▼
Researcher Worker Evaluator Reflector Loop Mgr
   │       │       │       │       │
   └───────┴───────┴───────┴───────┘
                   │
            aafl_core.py
          (routes to cheapest
           provider — ALP)
```

---

## File Locations (when built)

| File | Location |
|---|---|
| knowledge_engine.db (SQLite) | C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\data\ |
| chromadb/ (vector store) | C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\data\chromadb\ |
| research_rules/ (YAML configs) | C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\research_rules\ |
| ui/ (Streamlit app) | C:\Users\jscot\OneDrive\Desktop\VKB-SpinDoctor\ui\ |

---

## ALP Cost Summary

| Part | Cost |
|---|---|
| SQLite | £0 — built into Python |
| ChromaDB | £0 — pip install, runs locally |
| Embeddings | £0 — local model on RTX 5090 |
| DuckDuckGo search | £0 — no API key needed |
| Local LLM summarisation | £0 — RTX 5090 |
| Streamlit UI | £0 — pip install, runs on localhost |
| **Total** | **£0 + electricity** |
