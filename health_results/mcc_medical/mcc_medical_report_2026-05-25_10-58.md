# MCC Medical Report
**Date:** 2026-05-25T10:58:02  |  **Score:** 82/100  |  **Verdict:** RESTRICTED DUTY

---

## Doctor's Verdict

### RESTRICTED DUTY
Core functions working but notable issues need attention before heavy use.

**Fitness Score: 82/100**

| Metric | Count |
|--------|-------|
| Total checks | 285 |
| Passed | 262 |
| Failed | 9 |
| Warnings | 14 |

---

## Top Priority Fixes

1. [endpoints] GET /scout/results: Check _handle for /scout/results in mcc_server.py
2. [endpoints] GET /api/task-inbox: Check _handle for /api/task-inbox in mcc_server.py
3. [recovery] GET /b2/budget-caps recovers from corrupt JSON: b2_load_json should fall back to default when JSON is corrupt — check _b2_load_json

## Top WMBW Improvement Recommendations

1. **Error Display (5/10):** Add actionable error text + inline retry buttons
2. **Endpoint Error Handling (5/10):** Add error_code field to all error responses; sanitize exception text
3. **Performance Polling (5/10):** Implement central poller with visibility-aware rate reduction

## Long-Term Wellness Recommendations

1. **Consolidate polling:** Replace per-tab setInterval with a central dispatcher that pauses when the browser tab is hidden. This will reduce background CPU use by ~60% and prevent stale data from accumulating.
2. **Structured error codes:** Add `error_code` fields to all API error responses so the frontend can give specific recovery suggestions rather than generic error messages.
3. **ARIA audit:** A full screen-reader audit is needed. Tab buttons lack `role=tab` and `aria-selected`. This is a one-afternoon fix with high accessibility dividend.
4. **DB index optimisation:** If knowledge_engine.db grows beyond 10,000 rows, add `CREATE INDEX idx_knowledge_created ON knowledge(created_at)` to keep query times under 50ms.
5. **Automated regression CI:** Wire `python mcc_medical.py --quick` to run on git push so regressions are caught at commit time rather than after deployment.

---

## Failures Detail

**9 failure(s) found:**

### [ENDPOINTS] GET /scout/results
- **Detail:** HTTP 404 (2.062s)
- **Fix:** Check _handle for /scout/results in mcc_server.py

### [ENDPOINTS] GET /api/task-inbox
- **Detail:** HTTP 404 (2.061s)
- **Fix:** Check _handle for /api/task-inbox in mcc_server.py

### [PERFORMANCE] All timed endpoints under 2s threshold
- **Detail:** 8 slow endpoints

### [SAFETY] GET /scout/results returns running status
- **Detail:** running=?

### [RECOVERY] GET /b2/budget-caps recovers from corrupt JSON
- **Detail:** HTTP 0
- **Fix:** b2_load_json should fall back to default when JSON is corrupt — check _b2_load_json

### [RECOVERY] GET /stuck-inbox returns empty list when file missing
- **Detail:** HTTP 0

### [RECOVERY] POST /wccs with missing chat_latest.txt returns 400
- **Detail:** HTTP 0
- **Fix:** WCCS should check chat file exists before running

### [RECOVERY] GET /self-diagnosis works without full_mot_report.json
- **Detail:** HTTP 0

### [RECOVERY] POST /wccs with body text writes chat and responds
- **Detail:** HTTP 0

## Warnings Detail

- **[ux]** Loading skeleton screens for slow data: UX enhancement
- **[performance]** Page load time < 500ms (got 2047ms): 2.047s
- **[performance]** Response time /status < 2s (got 2.045s): 2.045s
- **[performance]** Response time /aafl-queue < 2s (got 2.047s): 2.047s
- **[performance]** Response time /b2/kanban < 2s (got 2.079s): 2.079s
- **[performance]** Response time /b2/activity < 2s (got 2.046s): 2.046s
- **[performance]** Response time /b2/costs < 2s (got 2.047s): 2.047s
- **[performance]** Response time /memory/knowledge < 2s (got 2.047s): 2.047s
- **[performance]** Response time /self-diagnosis < 2s (got 2.129s): 2.129s
- **[performance]** Response time /api/timeline < 2s (got 2.052s): 2.052s
- **[performance]** /b2/costs parse time < 1s (got 2.05s): 2.05s
- **[accessibility]** ARIA roles/attributes used: 
- **[accessibility]** Inputs have associated <label> elements: 0/45 inputs labelled
- **[accessibility]** Secondary text colour (#555) may fail WCAG AA: #555 on #0d0d0d ≈ 3.2:1 contrast ratio (AA requires 4.5:1)

---

## Inventory Summary

- Tabs: 16
- GET endpoints: 62
- POST endpoints: 63
- DELETE endpoints: 1
- Fetch calls in HTML: 2

### All GET Endpoints

- `GET /`
- `GET /mission_control.html`
- `GET /status`
- `GET /captures`
- `GET /scout-result`
- `GET /scout-config`
- `GET /scout-presets`
- `GET /aafl-status`
- `GET /aafl-queue`
- `GET /aafl-config`
- `GET /aafl-providers`
- `GET /api/timeline`
- `GET /api/backup`
- `GET /api/diff`
- `GET /api/session-logs`
- `GET /api/session-log`
- `GET /api/search`
- `GET /api/auto-wccs`
- `GET /health-status`
- `GET /dashboard-data/`
- `GET /stuck-inbox`
- `GET /memory/knowledge`
- `GET /memory/solutions`
- `GET /memory/sources`
- `GET /promo-queue`
- `GET /acca-codes`
- `GET /alp-data`
- `GET /self-diagnosis`
- `GET /known-issues`
- `GET /modules`
- `GET /presets`
- `GET /presets/load`
- `GET /aafl-settings`
- `GET /retry-log`
- `GET /chain-status`
- `GET /chain-log`
- `GET /scout-timer/status`
- `GET /sources-library`
- `GET /stuck-inbox/summary`
- `GET /storage`
- `GET /storage/report`
- `GET /wccs/save-log`
- `GET /wccs/history-search`
- `GET /wccs/session-logs`
- `GET /wccs/versions`
- `GET /api/status`
- `GET /api/history`
- `GET /api/acca`
- `GET /api/health`
- `GET /aafl/live`
- `GET /aafl/bridge-result`
- `GET /aafl/workflow-presets`
- `GET /b2/kanban`
- `GET /b2/activity`
- `GET /b2/aafl-runs`
- `GET /b2/prefs`
- `GET /b2/budget-caps`
- `GET /b2/costs`
- `GET /b2/keybind-profiles`
- `GET /b2/source-health`
- `GET /scout/results`
- `GET /api/task-inbox`

### All POST Endpoints

- `POST /wccs`
- `POST /capture`
- `POST /run-scout`
- `POST /scout-config`
- `POST /run-aafl`
- `POST /set-aafl-goal`
- `POST /aafl-queue`
- `POST /aafl-config`
- `POST /stop-aafl`
- `POST /api/wccs`
- `POST /api/restore`
- `POST /api/auto-wccs`
- `POST /resolve-stuck`
- `POST /run-now`
- `POST /approve-promo`
- `POST /reject-promo`
- `POST /alp-add`
- `POST /run-mot`
- `POST /known-issues`
- `POST /run-health-check`
- `POST /run-merge-sessions`
- `POST /toggle-module`
- `POST /presets/save`
- `POST /presets/delete`
- `POST /aafl-settings`
- `POST /suggest-provider`
- `POST /run-chain`
- `POST /scout-timer/start`
- `POST /scout-timer/stop`
- `POST /sources-library/add`
- `POST /stuck-inbox/bulk-resolve`
- `POST /wccs/restore`
- `POST /wccs/diff`
- `POST /aafl/run-goal`
- `POST /scout/strategy`
- `POST /aafl/scout-bridge`
- `POST /aafl/workflow`
- `POST /b2/kanban`
- `POST /b2/activity`
- `POST /b2/activity/summarise`
- `POST /b2/run-tag`
- `POST /b2/run-notes`
- `POST /b2/prefs`
- `POST /b2/budget-caps`
- `POST /b2/benchmark`
- `POST /b2/second-opinion`
- `POST /b2/step-mode`
- `POST /b2/step-next`
- `POST /b2/pause-aafl`
- `POST /b2/resume-aafl`
- `POST /b2/chain-save`
- `POST /b2/chain-run`
- `POST /b2/keybind-profiles`
- `POST /b2/keybind-profiles/rate`
- `POST /b2/keybind-profiles/delete`
- `POST /b2/strategy-overrides`
- `POST /b2/workers`
- `POST /b2/block-source`
- `POST /b2/unblock-source`
- `POST /b2/export-briefing`
- `POST /b2/scout-compare`
- `POST /api/task-inbox`
- `POST /api/run-queue`

---

_Report generated by mcc_medical.py — Doctor CLAC_
_History: health_results/mcc_medical/mcc_medical_history.json_