# MCC Medical Report
**Date:** 2026-05-27T19:54:25  |  **Score:** 86/100  |  **Verdict:** RESTRICTED DUTY

---

## Doctor's Verdict

### RESTRICTED DUTY
Core functions working but notable issues need attention before heavy use.

**Fitness Score: 86/100**

| Metric | Count |
|--------|-------|
| Total checks | 236 |
| Passed | 226 |
| Failed | 5 |
| Warnings | 5 |

---

## Top Priority Fixes

1. [endpoints] GET /storage: Check _handle for /storage in mcc_server.py
2. [endpoints] GET /storage/report: Check _handle for /storage/report in mcc_server.py
3. [cross_tab] All 17 tab panes in DOM (12/17): Missing tab panes: ['alp', 'self-diagnosis', 'autolog', 'providerhealth', 'medical']

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

**5 failure(s) found:**

### [UX] All tab buttons have title tooltips
- **Detail:** 0/13

### [ENDPOINTS] GET /storage
- **Detail:** HTTP 0 (10.003s)
- **Fix:** Check _handle for /storage in mcc_server.py

### [ENDPOINTS] GET /storage/report
- **Detail:** HTTP 0 (10.002s)
- **Fix:** Check _handle for /storage/report in mcc_server.py

### [CROSS_TAB] All 17 tab panes in DOM (12/17)
- **Detail:** missing: ['alp', 'self-diagnosis', 'autolog', 'providerhealth', 'medical']
- **Fix:** Missing tab panes: ['alp', 'self-diagnosis', 'autolog', 'providerhealth', 'medical']

### [REGRESSION] MOT [C] Feature: ALP Counter
- **Detail:** MISSING
- **Fix:** Fix: Feature: ALP Counter — MISSING

## Warnings Detail

- **[endpoints]** PERF: /storage slow (10.003s): 10.003s response
- **[endpoints]** PERF: /storage/report slow (10.002s): 10.002s response
- **[performance]** HTML size < 300KB (got 507.4KB): 507.4KB
- **[accessibility]** Inputs have associated <label> elements: 0/88 inputs labelled
- **[accessibility]** Secondary text colour (#555) may fail WCAG AA: #555 on #0d0d0d ≈ 3.2:1 contrast ratio (AA requires 4.5:1)

---

## Inventory Summary

- Tabs: 17
- GET endpoints: 64
- POST endpoints: 64
- DELETE endpoints: 1
- Fetch calls in HTML: 8

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
- `GET /api/medical-report`
- `GET /api/medical-history`

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
- `POST /api/run-medical`

---

_Report generated by mcc_medical.py — Doctor CLAC_
_History: health_results/mcc_medical/mcc_medical_history.json_