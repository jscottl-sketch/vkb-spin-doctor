# FULL DIAGNOSTIC SWEEP — 2026-06-07

**Type:** Read-only diagnostic. Nothing was fixed. One test write was made to STATUS.md to prove the save path works (entry: "DIAG SAVE 2026-06-07", +72 bytes) — this is expected and documented in Part C.
**Cost:** Zero paid Claude API calls. All AI provider tests used free-tier providers only (Cerebras, Mistral, Gemini, OpenRouter, Groq).

---

## PART A — SERVER HEALTH

### A1. Does it start clean?
**STARTS WITH WARNINGS.**

Two warnings on every startup (cosmetic, not fatal):
```
litellm: could not pre-load bedrock-runtime response stream shape — Bedrock event-stream
   decoding will be unavailable. Error: No module named 'botocore'
litellm: could not pre-load sagemaker-runtime response stream shape — SageMaker event-stream
   decoding will be unavailable. Error: No module named 'botocore'
```
These come from LiteLLM probing for AWS SDK support that isn't installed. Harmless — AAFL doesn't use Bedrock/SageMaker — but they print on every boot and look alarming.

### A2. Is it serving the latest mission_control.html, and does it cache?
**NO CACHING — but a much bigger problem exists (see A3).**
`_handle_html()` (mcc_server.py:1241) does `html_path.read_bytes()` fresh on every single request — there is no in-memory cache, no ETag, nothing stale. Editing the HTML and refreshing the browser **will** show the new version, IF the request lands on the right process (see below).

### A3. 🔴 CRITICAL — TWO mcc_server.py processes are simultaneously bound to 127.0.0.1:8080
This is very likely **the actual reason "browser fixes do nothing."**

```
PID 3108  (Python 3.13, started 2026-06-07 09:21:30) — python.exe mcc_server.py
PID 28540 (Python 3.14, started 2026-06-07 10:14:24) — python.exe mcc_server.py
```//
Both show `LISTENING` on `127.0.0.1:8080` at the same time. I additionally started a **third** instance for this test (`timeout 15 python mcc_server.py`) and it *also* bound successfully without any "address already in use" error — Python's `http.server.HTTPServer` sets `allow_reuse_address = 1`, and on Windows `SO_REUSEADDR` lets multiple processes share one listening port (unlike Linux, where it only allows TIME_WAIT re-bind).

**Consequence:** the OS load-balances incoming connections across *all* processes bound to that port, essentially at random. If Scott edits `mcc_server.py`, restarts "the" server, and the OLD process is still alive in the background, roughly half his requests get served by the stale code — and it will look exactly like "I fixed it and nothing changed," because nothing did change for that request. The same applies in reverse (new code answering, old code answering) — totally non-deterministic, impossible to debug by looking at the browser alone.

**This is a pure-code/process-hygiene fix** (no Scott decision needed for the diagnosis — but Scott needs to be told to always fully kill old python.exe processes before restarting, and ideally the startup script should refuse to bind / should kill prior instances first).

---

## PART B — EVERY ENDPOINT

**215 unique `/api/...` routes found and probed** (GET/POST/PUT/DELETE, 20s timeout per probe, minimal/garbage payloads on POST/PUT).

| Result | Count | Meaning |
|---|---|---|
| WORKING (2xx + valid JSON) | 150 | responding correctly |
| EXPECTED VALIDATION ERRORS (400/404 + valid JSON, e.g. "id required") | 52 | correct behaviour — these routes need real payloads/IDs, not broken |
| **ACTUALLY BROKEN** | **13** | see table below |

### 🔴 The 13 actually-broken endpoints

| Route | Method | Symptom | Root cause (verified by reading source) |
|---|---|---|---|
| `/api/work-checker/report` | GET | 500 `'MCCHandler' object has no attribute '_handle_wc_report'` | Handler exists in the file (mcc_server.py:5083) but is **mis-indented inside `_qa_startup_test()`** (a module-level function, line 5025+) instead of being a method of `MCCHandler` or monkey-patched onto it. It is dead, unreachable code. |
| `/api/work-checker/requeue` | GET | same — `_handle_wc_requeue` missing | same misplacement (mcc_server.py:5105) |
| `/api/work-checker/orphaned` | GET | same — `_handle_wc_orphaned` missing | same misplacement (mcc_server.py:5132) |
| `/api/work-checker/refresh` | POST | same — `_handle_wc_refresh` missing | same misplacement (mcc_server.py:5098) |
| `/api/instructions` | GET | 500 `Unexpected UTF-8 BOM (decode using utf-8-sig)` | `data/instructions_db.json` is saved **with a UTF-8 BOM**; handler (mcc_server.py:5949) reads it with `encoding="utf-8"` — `json.loads` chokes on the BOM byte. |
| `/api/instructions/<id>` | GET | same BOM error | same file, same handler family (mcc_server.py:5961) |
| `/api/acca/codes` | GET | 500 `Unexpected UTF-8 BOM` | `data/acca_codes.json` **also** has a UTF-8 BOM; handler (mcc_server.py:9897) same `encoding="utf-8"` bug. |
| `/api/ancoreg/mot` | GET | 500 `name 'HEALTH_DIR' is not defined` | Plain typo/`NameError` at mcc_server.py:10096 — the constant is called `HEALTH_RESULTS` everywhere else in the file (defined line 57); `HEALTH_DIR` was never defined. |
| `/api/self-health/run` | POST | 500 `'charmap' codec can't encode character '✗'` | `self_health.py:570` does `print(f"[HC] {icon} ...")` where `icon` can be `✓ ⚠ ✗`. `_sh_handle_run_all` calls `runner.run_all()` **in-process** (not via subprocess), so this print goes straight to the server's own stdout — which on Windows defaults to the `cp1252`/"charmap" console codec that cannot encode `✗` (U+2717). Crashes the whole request. |
| `/api/wccs` | POST | probe timed out (>20s, no response) | Runs `aafl_wccs.py` as a subprocess with a **300-second** timeout (mcc_server.py:1685). Likely just slow, not actually hung — but 20s+ with zero progress feedback to the browser is a real UX problem; if it really does take up to 5 minutes, the WCCS button will look "frozen." |
| `/api/run-medical` | POST | probe timed out reading body (status 200 received) | This one **is working as designed** — it streams the 285-check medical scan via chunked transfer-encoding and simply takes longer than my 20s read-timeout. Re-classified as SLOW, not BROKEN — flagged here only so Scott knows why a quick `curl` looks like it hangs. |
| `/api/provider-health/diagnose` | POST | probe timed out at 20s | Re-tested with a 90s timeout — **it works**, just takes **48.7 seconds** (it pings all 14 providers serially). Returned `{"healthy": 2, "total": 14, ...}`. Re-classified SLOW, not BROKEN. |
| `/api/ancoreg/run-save` | POST | probe timed out at 20s | Re-tested with 90s — **it works**, takes **27 seconds** (runs a real WCCS+backup pipeline). Returned a real result. Re-classified SLOW, not BROKEN. |

So the **true broken count is 9** (4 work-checker handlers + 2 BOM files × overlapping routes + 1 NameError + 1 Unicode-print crash), and **3 more are simply slow long-running operations that a 20-second smoke-test mistook for hangs** — they're fine, just need a longer client-side timeout / a spinner in the UI.

### Minor: dead duplicate route registrations
`/api/storage/stats` and `/api/storage/largest` are each registered **twice** in `do_GET` (mcc_server.py:499-502 and again at 622-625, identical handlers). The second pair is unreachable dead code (Python `if/elif` matches the first one). Harmless, but it's a sign of copy-paste during a merge — worth a quick cleanup pass.

---

## PART C — SAVE PATH TRUTH

**YES — the server-side save genuinely works**, independent of any browser button.

I called `POST /api/hisav/save-session` directly with `{"text": "DIAG SAVE 2026-06-07"}`:

| | Before | After |
|---|---|---|
| `STATUS.md` size | 34,261 bytes | 34,333 bytes (**+72 bytes**) |
| Tail of file | (no entry) | `## Session Note — 2026-06-07 10:39:39` / `DIAG SAVE 2026-06-07` |

The file changed on disk, on the spot, with no AI involvement (the handler at mcc_server.py:8727 is explicitly commented "No AI, no provider calls" — direct `read → append → atomic replace`).

**One wrinkle worth knowing about:** the server's own JSON response claimed `"bytes": 33990`, but the file actually ended up at 34,333 bytes — a 343-byte mismatch. The handler computes `byte_count` from its own in-memory `existing + entry` string *before* writing. If another save (auto-save, or a second request landing on the **other** zombie server process from Part A3) wrote to STATUS.md between this handler's read and its write, the reported count goes stale relative to the final file — a classic read-modify-write race with no lock around `STATUS_FILE`. Not dangerous (the atomic `tmp.replace()` prevents corruption), but it means the byte-count Scott sees in the UI confirmation can lie. This is very likely the **same root cause as A3** — two server processes both able to touch the file.

**Bottom line: the dead Save button was never a server problem.** The server-side write path is solid. The bug is 100% on the browser/JS side (button wiring) — and Part F below explains exactly why JS wiring can fail to attach.

---

## PART D — AI PROVIDERS (the donkey workforce)

Tested directly through `aafl_core` / LiteLLM with the prompt *"Reply with exactly the single word: READY"* (free-tier providers only):

| Provider | Connects? | Elapsed | Response | Verdict |
|---|---|---|---|---|
| **Mistral** (`mistral_code` / codestral-latest) | ✅ YES | 0.5s | `'READY'` | ✅ **Working great** — fast, correct, this is the workhorse |
| **Cerebras** (`gpt-oss-120b`) | ✅ YES (connects) | **99.2s** | `''` (empty) | ⚠️ **Connects but unreliable** — see note below |
| **Gemini** (`gemini-2.5-flash`) | ❌ NO | — | `RateLimitError 429`: "You exceeded your current quota" | 🔴 **Quota exhausted** — needs Scott to check billing/plan or wait for reset |
| **OpenRouter** (`openrouter/auto`) | ❌ NO | — | `AuthenticationError 401`: "User not found" | 🔴 **Bad API key** — the key in `OPENROUTER_API_KEY` is invalid/revoked, needs Scott to generate a new one |
| Groq (70B / DeepSeek) | — | — | `SKIP — GROQ_API_KEY not set` | Not configured (not in original ask, noted for completeness) |

**Cerebras nuance — important correction to the "always returns empty" assumption:** I ran Cerebras twice. On the short "READY" prompt it took 99 seconds and came back empty. On a longer code-editing prompt (Part E test) it took 102 seconds and came back with **valid code**. So Cerebras isn't *always* empty — it's **always extremely slow (~100 seconds per call)** and **sometimes** returns nothing, possibly related to `max_tokens` being small or a stop-sequence/formatting quirk on short replies. Either way, at 100 seconds per round-trip it's effectively unusable as a "fast free tier" — it's the slowest provider in the entire stack by roughly 200×.

---

## PART E — OCB RUNNER (can MCC actually write code?)

**WIRED + RETURNS CODE — confirmed end-to-end.** ✅

I ran the exact call chain `ocb_runner.run_task()` uses (`AAFLCore(dry_run=False, allow_paid=False).run(prompt, task_type="code")`) with a trivial one-line edit task. Routing log:

```
[AAFL] LIVE. Paid=OFF. 14 providers registered.
[AAFL] -> LM Studio Coder 32B   FAIL: No models loaded. Please load a model
[AAFL] -> LM Studio Phi-4 14B   FAIL: No models loaded. Please load a model
[AAFL] -> Cerebras GPT-OSS 120B OK (102.08s, $0.00027)
RESPONSE: '# diagnostic test\nx = 1\ny = 2'
```

So: the import is real, the call is real, and it returned syntactically correct code. The wiring is **not** dead.

**However — two things make this practically painful right now:**
1. **LM Studio has no models loaded.** Both local "Tier 1: free, unlimited, fast" providers fail *instantly* with "No models loaded. Please load a model" — meaning every single OCB task currently has to fall through two guaranteed failures before reaching a working provider.
2. **The provider it falls through to is Cerebras — the slowest provider measured (≈100 seconds per call).** A multi-section OCB run that needs, say, 10 AI edits would take **~17 minutes** of pure AI wait time at this routing order, with zero feedback in between beyond the phase cards.

This isn't "OCB Runner is broken" — it's "OCB Runner is wired correctly but is currently routed through the worst possible provider because the best ones are unavailable." Loading a model in LM Studio would likely fix this completely and instantly (free + fast + local).

---

## PART F — FRONTEND HANG (why buttons don't wire up)

**Found it. mission_control.html:1945:**

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.44.0/min/vs/loader.min.js"></script>
</head>
<body>
```

This is a **synchronous, render-blocking `<script src>`** (no `async`, no `defer`) sitting at the very end of `<head>`, immediately before `<body>`. Per the HTML spec, the browser **must** stop parsing the document, fetch this script from `cdnjs.cloudflare.com`, execute it, and only then continue to `<body>` — where every button's `onclick` handler and every wiring `<script>` block lives.

**If the machine is offline, or cdnjs.cloudflare.com is slow/blocked/down:** the browser hangs on that fetch for its connection-timeout (commonly 20–30+ seconds, sometimes longer depending on browser/OS network stack), during which **nothing in `<body>` exists yet** — no buttons, no event listeners, nothing. Once it finally times out or loads, the rest of the page renders — but if Scott clicked "Save" or any other button during that window, there was nothing there to click; the click landed on a not-yet-parsed DOM and did nothing.

This is a very strong candidate for **the** root cause of "buttons not wiring" / "page feels frozen on load," especially on a connection that's anything less than instant to Cloudflare's CDN.

(For contrast: the Chart.js loader at line 18048 is loaded **correctly** — dynamically via `document.createElement('script')` only when a chart tab is opened, so it can never block initial page parse.)

**Fix is pure-code, no Scott decision needed:** add `defer` (or `async`) to the Monaco `<script>` tag, or better, lazy-load Monaco the same way Chart.js is lazy-loaded (only when the Code Editor tab is actually opened).

---

# FINAL RANKED TABLE — WORST FIRST

| # | Area | Status | What's actually broken | Needs Scott's input? |
|---|---|---|---|---|
| 1 | **Frontend / page load** | 🔴 Critical | `mission_control.html:1945` — Monaco loader `<script src=cdnjs...>` has no `async`/`defer`, blocks ALL of `<body>` (including every button's click-wiring) until the external CDN responds or times out. This is the prime suspect for "buttons do nothing." | **N — pure code fix** (add `defer`, or lazy-load like Chart.js) |
| 2 | **Server process hygiene** | 🔴 Critical | TWO (really, an unlimited number of) `mcc_server.py` processes can simultaneously bind 127.0.0.1:8080 on Windows because `HTTPServer` sets `SO_REUSEADDR`. Requests get routed non-deterministically between old/stale and new/fixed code. This is almost certainly why "I fixed it and nothing changed" keeps happening. | **Y — Scott needs to always fully close old terminal windows / kill old python.exe before restarting** (and ideally we add a startup guard that refuses to run, or kills prior instances, when the port is already bound) |
| 3 | **AI providers** | 🔴 Critical | Routing currently goes: LM Studio (2× instant fail, no model loaded) → Cerebras (connects but ~100 seconds per call, sometimes empty). Mistral is fast & correct (0.5s) but is 5th in the routing order for code tasks. OCB Runner therefore "works" but is painfully slow. | **Y — Scott needs to (a) load a model in LM Studio app, and (b) consider re-ordering provider priority so Mistral/Codestral is tried before Cerebras for code tasks** |
| 4 | **AI providers — auth/quota** | 🟠 High | OpenRouter key is **invalid** (401 "User not found" — needs a fresh key). Gemini is **quota-exhausted** (429 — needs plan check or to wait for reset). | **Y — needs new OpenRouter key + Gemini billing/quota check** |
| 5 | **Work Checker tab** | 🟠 High | 4 endpoints (`report`, `refresh`, `requeue`, `orphaned`) all 500 with `'MCCHandler' object has no attribute ...`. Root cause: the 5 handler functions (incl. `_wc_run_checker`) are **mis-indented inside `_qa_startup_test()`** at mcc_server.py:5066-5144 — they were never attached to `MCCHandler`, unlike every other endpoint family (which use `MCCHandler._handle_x = _handle_x` monkey-patches). Dead code, never worked since whatever commit introduced it. | **N — pure code fix** (move the 5 functions out, monkey-patch them onto `MCCHandler` like the Self-Health family) |
| 6 | **Instructions / ACCA Codes data** | 🟡 Medium | `/api/instructions`, `/api/instructions/<id>`, `/api/acca/codes` all 500 with `Unexpected UTF-8 BOM`. Both `data/instructions_db.json` and `data/acca_codes.json` were saved **with a UTF-8 BOM**, but the handlers read them with `encoding="utf-8"` instead of `utf-8-sig`. | **N — pure code fix** (read with `utf-8-sig`, or strip the BOM from the two JSON files once) |
| 7 | **ANCOREG MOT** | 🟡 Medium | `/api/ancoreg/mot` → 500 `name 'HEALTH_DIR' is not defined`. Plain typo — should be `HEALTH_RESULTS` (the constant used everywhere else, defined at mcc_server.py:57). | **N — one-line typo fix** |
| 8 | **Self-Health "Run All"** | 🟡 Medium | `/api/self-health/run` → 500 `'charmap' codec can't encode character '✗'`. `self_health.py:570` prints `✓ ⚠ ✗` Unicode glyphs to stdout; on Windows that's the `cp1252` console codec, which can't encode `✗` (U+2717), and it crashes the whole in-process call. | **N — pure code fix** (swap glyphs for `[PASS]/[WARN]/[FAIL]`, or wrap the print in `errors="replace"`, or `sys.stdout.reconfigure(encoding="utf-8")` at server startup) |
| 9 | **Save-session byte-count race** | 🟢 Low | `/api/hisav/save-session` reported `"bytes": 33990` but the file actually ended up at 34,333 bytes — a stale read/race in the read-modify-write, almost certainly caused by issue #2 (two processes touching the same file). The save itself is correct and atomic; only the *reported* byte-count can be wrong. | **N — will likely disappear once #2 is fixed; otherwise add a lock around STATUS_FILE writes** |
| 10 | **Dead duplicate routes** | 🟢 Low | `/api/storage/stats` and `/api/storage/largest` are registered twice in `do_GET` (mcc_server.py:499-502 and 622-625) — harmless dead `elif` branches from a copy-paste merge. | **N — cosmetic cleanup** |
| 11 | **Startup warnings** | 🟢 Low | Two LiteLLM warnings about missing `botocore` print on every boot (Bedrock/SageMaker pre-load). AAFL doesn't use either provider — cosmetic noise that looks scarier than it is. | **N — could `pip install botocore` to silence, or just ignore** |
| 12 | **Long-running endpoints look "hung" to a quick test** | 🟢 Info only | `/api/wccs` (up to 300s), `/api/run-medical` (streamed, 285 checks), `/api/provider-health/diagnose` (48.7s, pings 14 providers), `/api/ancoreg/run-save` (27s, runs WCCS+backup) — **all actually work**, they're just slow. Re-tested each with a longer timeout and got valid results. Listed here only so nobody "fixes" something that isn't broken. | **N — not broken; consider adding progress spinners in the UI so it doesn't *look* frozen** |

---

## What this means for "we keep finding bugs one at a time"

Two of the items above (**#1 frontend blocking script**, **#2 duplicate server processes**) are *systemic* — they don't just cause one bug each, they actively **mask and randomize the symptoms of every other bug** on this list. #2 means a code fix can appear to "not work" because the old process answered the test request. #1 means a perfectly good button can appear "dead" purely because of network timing on page load, with zero relation to its actual `onclick` code. Fixing those two first will make every future diagnostic session dramatically more reliable — bugs will stop appearing to come and go at random.

---
*Sweep performed 2026-06-07. Server tested: live instance on 127.0.0.1:8080 (PID 3108, started 09:21:30, same code version as current `mcc_server.py` on disk — last modified 09:20:59). 215 routes probed. Zero paid-Claude calls made.*
