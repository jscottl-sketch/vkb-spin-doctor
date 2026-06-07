# Session Log — MCC Full Medical 2026-05-25
**Tool:** mcc_medical.py (Doctor CLAC)  
**Run time:** ~6 minutes 40 seconds  
**Date:** 2026-05-25  

---

## What Was Built

`mcc_medical.py` — A comprehensive health/fitness test suite that supersedes mcc_full_mot.py.
- 285 individual checks across 14 categories
- Re-runnable: `python mcc_medical.py` (full) | `--quick` | `--category=X`
- Every test is its own function (FFUE)
- Logs to `health_results/mcc_medical/`

**Outputs written:**
- `health_results/mcc_medical/mcc_inventory.json` — full element map
- `health_results/mcc_medical/mcc_wmbw_report.md` — per-element best-practice scoring
- `health_results/mcc_medical/mcc_medical_report_2026-05-25_10-39.md` — dated report
- `health_results/mcc_medical/mcc_medical_history.json` — rolling history (1 run logged)

---

## Phase 1 — Inventory Results

| Item | Count |
|------|-------|
| Tabs | 16 |
| GET endpoints | 62 (full list in inventory) |
| POST endpoints | 63 |
| DELETE endpoints | 1 |
| Fetch calls in HTML | 2 (HTML is largely inline JS) |
| DB tables | 8 (knowledge, solution_log, source_reputation, provider_reputation, test_results, tags, etc.) |

All 16 tabs confirmed present in DOM: home, wccs, kanban, aafl-runs, scout, costs, aafl-control, memory, promo, acca, alp, storage, self-diagnosis, autolog, providerhealth, keybind-profiles.

---

## Phase 2 — WMBW Upgrade Recommendations (Top 6, score < 7)

| Element | Score | Priority Fix |
|---------|-------|--------------|
| error_display | 5/10 | Add actionable error text + inline retry buttons |
| endpoint_error_handling | 5/10 | Add error_code field; sanitize exception text |
| performance_polling | 5/10 | Central poller with visibility-aware rate reduction |
| accessibility_contrast | 5/10 | Lighten #555 -> #777 minimum on dark backgrounds |
| form_validation | 5/10 | Add maxlength + char remaining indicators |
| textarea_chat | 6/10 | Auto-resize + char counter + Ctrl+Enter label |

---

## Phase 3 — Medical Score

**SCORE: 82/100 — RESTRICTED DUTY**

| Category | Checks | Pass | Fail | Warn |
|----------|--------|------|------|------|
| functional | 21 | 21 | 0 | 0 |
| ux | 17 | 15 | 1 | 1 |
| endpoints | 72 | 70 | 2 | 0 |
| integration | 12 | 12 | 0 | 0 |
| edge | 13 | 13 | 0 | 0 |
| performance | 13 | 7 | 1 | 5 |
| error_handling | 12 | 11 | 1 | 0 |
| persistence | 7 | 7 | 0 | 0 |
| accessibility | 9 | 6 | 0 | 3 |
| cross_tab | 11 | 11 | 0 | 0 |
| safety | 9 | 5 | 4 | 0 |
| recovery | 6 | 6 | 0 | 0 |
| deps | 25 | 25 | 0 | 0 |
| regression (MOT) | 4 | 4 | 0 | 0 |
| **TOTAL** | **285** | **263** | **8** | **14** |

---

## Phase 4 — Failures Analysis

### Real Failures (need fixing):

**1. [performance] All endpoints return ~2.0s**
- Every single endpoint takes exactly ~2.0 seconds to respond
- Root cause: `log_message()` calls `self.address_string()` which does a reverse DNS lookup for every request
- Fix: Override `address_string()` in MCCHandler to return `"localhost"` directly
- Impact: HIGH — every API call in MCC takes 2x longer than it should

**2. [endpoints] GET /scout/results returns 404**
- Route IS in mcc_server.py but running server may be stale (mcc_server.py has uncommitted changes in git status)
- Fix: Restart mcc_server.py to pick up latest routing
- Note: `/api/task-inbox` GET same issue

**3. [ux] One tab button missing title tooltip (23/24)**
- The 16th tab button has no title attribute — likely keybind-profiles
- Fix: Add `title="..."` to the missing tab button

### False Positives (test expectations were wrong, server is correct):

**4. [error_handling/safety] POST /wccs empty body returns 200**
- Server correctly uses existing `chat_latest.txt` content when body is empty
- Test assumption was wrong: "empty body" is valid if chat file has content
- Verdict: Server is correct — test needs updating

**5. [safety] POST /approve-promo unknown ID returns 200 {ok: false}**
- Server returns `{"ok": false}` with 200 for unknown IDs
- Test expected 404 — server design choice to always 200 with ok:false
- Verdict: Minor design issue — acceptable but 404 would be more REST-correct

---

## Phase 5 — Doctor's Verdict

### RESTRICTED DUTY (82/100)

**Top 3 Priority Fixes:**
1. **DNS reverse lookup bug** — Add `def address_string(self): return "127.0.0.1"` to MCCHandler to kill the 2s per-request penalty
2. **Restart server** — mcc_server.py has been modified (git M status); running instance is stale; /scout/results and /api/task-inbox return 404
3. **Tab button title** — One tab button (keybind-profiles or similar) missing title tooltip; 5-second fix

**Top 3 WMBW Improvements:**
1. Visibility-aware polling — pause setInterval when window.hidden to save CPU/battery
2. Structured error codes — add `error_code` to all API errors so frontend can give smart recovery hints
3. Accessibility: lighten #555 to #777+ and add aria-selected/role=tab to tab buttons

**Long-term Wellness:**
- Wire `python mcc_medical.py --quick` to pre-commit hook or CI
- Add DB indexes when solution_log exceeds 10,000 rows
- Split large HTML (296.8KB, borderline 300KB limit) into lazy-loaded fragments

---

## Notable Healthy Findings

- All 108 existing MOT checks: 100% PASS
- All 11 core Python imports: PASS
- All 8 optional module imports: PASS
- All 6 integration flows: PASS (capture, queue, goal, activity, kanban, issues)
- All 13 edge cases: PASS (unicode, emoji, SQL injection, path traversal, concurrent requests)
- All 7 persistence tests: PASS
- All 6 recovery tests: PASS (corrupt JSON, missing files all handled gracefully)
- CORS headers: PASS
- Content-Type headers: PASS
- 404 for unknown paths: PASS
- Path traversal blocked: PASS
- Pause/resume flag: PASS
- Budget cap: £0.50/day set
- DB has all 8 expected tables
