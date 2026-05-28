# WCYA — What Can You Add — Build 3 Ideas
*For Scott to review. Ideas only — no code here.*
*Categories: Data Visualization | User Experience | AI Intelligence | Automation | Commercial Readiness*

---

## Data Visualization

| # | Idea | Effort |
|---|---|---|
| 1 | **3D provider map** — Three.js globe showing which providers are online by geography (Cerebras=US, Mistral=EU, etc). Spins slowly. Green dots = live, red = offline. | Big |
| 2 | **AAFL score heatmap calendar** — GitHub-style contribution grid. Each day = one square coloured by average AAFL score. Instantly shows "good weeks" vs "bad weeks". | Medium |
| 3 | **Token spend river chart** — Sankey diagram showing how budget flows: Total → Provider tier → Individual provider → Goal type. Makes it obvious where money goes. | Big |
| 4 **Goal complexity radar chart** — Spider/radar chart per goal run: speed, accuracy, research depth, cost efficiency, provider reliability. 5-axis at-a-glance quality view. | Medium |
| 5 | **Live latency sparklines** — Each provider card shows a 60-second rolling sparkline of response times. Instant degradation detection without running a health check. | Quick |
| 6 | **Cost-per-score efficiency scatter** — X axis = cost, Y axis = AAFL score. Each dot = one run. Ideal runs are top-left (cheap AND high score). Identify wasted expensive runs instantly. | Medium |

---

## User Experience

| # | Idea | Effort |
|---|---|---|
| 7 | **Smart search across all tabs** — Global Ctrl+F search bar that searches Kanban cards, AAFL run notes, Scout results, session logs, and ACCA codes simultaneously. Shows results grouped by tab. | Medium |
| 8 | **Quick note sticky** — Floating sticky note widget (top-right corner). Click once to expand a text area. Notes auto-save to a quick_notes.json. Never lose a thought mid-session. | Quick |
| 9 | **Session timer** — Visible running clock in the header showing time since MCC opened. At 90 minutes, amber warning: "Long session — consider WCCS now". At 120 min, red. | Quick |
| 10 | **Drag-and-drop Kanban** — Click and drag cards between To Do / Doing / Done columns instead of button clicks. Industry-standard UX improvement. | Medium |
| 11 | **Tab pinning** — Right-click any tab to pin it (bold border). Pinned tabs always stay visible even on small screens. Saves scrolling on the tab bar. | Quick |
| 12 | **Responsive mobile view** — Sidebar collapses, tabs scroll horizontally, text scales up. Makes MCC usable on a tablet or phone for checking status away from the desk. | Big |

---

## AI Intelligence

| # | Idea | Effort |
|---|---|---|
| 13 | **Goal quality predictor** — Before running AAFL, paste a goal and click "Score This Goal". Free Mistral predicts: likely AAFL score, suggested provider, estimated time, risk of failure. ALP saver. | Medium |
| 14 | **Auto-tagging** — After every AAFL run, Mistral reads the goal and auto-tags it (game config / research / bug fix / optimisation). Tags appear on run cards. Makes filtering instant. | Quick |
| 15 | **Trend narrator** — Weekly AI-generated plain-English paragraph: "This week you ran 8 goals, 6 passed. Cerebras was fastest. Your Star Citizen runs cost 3x more than your VKB runs." Reads like a manager's briefing. | Medium |
| 16 | **Smart goal suggestions from Kanban** — When a card moves to Done, Mistral reads it and suggests 2 follow-up AAFL goals based on what was just completed. One-click to queue them. | Medium |
| 17 | **Provider personality profiles** — AI-generated summaries per provider: "Cerebras: best for speed, tends to skip nuance. Mistral: most accurate for code, slowest on research." Built from run history. | Big |

---

## Automation

| # | Idea | Effort |
|---|---|---|
| 18 | **Auto-Scout on goal queue** — When AAFL queues a goal, automatically run a 30-second quick Scout for that goal first. Feed top 3 results as context into the AAFL prompt. Better results, same cost. | Medium |
| 19 | **Daily digest email/notification** — At 8am, send a summary to Scott's hotmail: yesterday's AAFL scores, costs, any provider outages, top Kanban moves. Windows Task Scheduler + smtplib. | Medium |
| 20 | **Auto-archive completed runs** — AAFL runs older than 30 days and scoring below 6.0 auto-move to archive_dead/. Keeps the runs tab clean without manual housekeeping. | Quick |
| 21 | **Webhook trigger** — POST to a user-configured URL after every AAFL run completes. Enables n8n, Zapier, or Discord bot integrations without extra code. | Quick |
| 22 | **Overnight batch scheduler** — Set up to 10 goals to run overnight (e.g. start at midnight, max 3 hours). MCC manages sleep/wake, logs results, sends morning summary. Combines queue_runner + scout_timer concepts. | Big |

---

## Commercial Readiness

| # | Idea | Effort |
|---|---|---|
| 23 | **Multi-project switcher** — Dropdown in the header to switch between project folders (VKB Spin Doctor / AAFL Engine / etc). Each project has its own STATUS.md, Kanban, runs. One MCC controls all. | Big |
| 24 | **Onboarding wizard** — First-run modal: "Welcome to MCC. Step 1: Add your first API key. Step 2: Run a Health Check. Step 3: Queue your first goal." 3-step setup. Lowers barrier for new users. | Medium |
| 25 | **Export as PDF report** — One-click PDF: AAFL scores, costs, Scout findings, Kanban status. Uses browser print API. Professional deliverable for clients or portfolio. | Quick |
| 26 | **White-label mode** — Settings to change project name, logo, accent colour, and hide any tabs. Lets the MCC be reskinned for different clients or products without code changes. | Medium |

---

*26 ideas total. Review and score by value vs effort before adding to Kanban.*
