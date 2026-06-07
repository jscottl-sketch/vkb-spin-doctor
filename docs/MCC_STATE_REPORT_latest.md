======================================================================
MCC STATE REPORT — self-analysis of the build's own current state
Generated: 2026-06-07T21:28:04
======================================================================

── a. CURRENT STATE — verified vs claimed-but-unverified ──
VERIFIED working (8 endpoints responded live):
  [OK]  /api/status — HTTP 200, 34578 bytes
  [OK]  /api/health — HTTP 200, 68 bytes
  [OK]  /api/provider-health — HTTP 200, 4107 bytes
  [OK]  /api/detective/report — HTTP 200, 19884 bytes
  [OK]  /api/hisav/data — HTTP 200, 4144 bytes
  [OK]  /api/ocb/status — HTTP 200, 2057 bytes
  [OK]  /api/session-state — HTTP 200, 685 bytes
  [OK]  /api/project-awareness — HTTP 200, 3618 bytes
CLAIMED but UNVERIFIED (0 endpoints failed/suspect):
Key handler functions:
  _handle_provider_health_enriched() — present, ~161 lines
  _handle_detective_report_get() — present, ~11 lines
  _handle_hisav_data_get() — present, ~75 lines
  _handle_ocb_status() — present, ~31 lines
  _handle_api_wccs() — present, ~3359 lines
  _handle_mcc_state_report() — present, ~46 lines

── b. LAST 10 MCC UPDATES — interrupted-session detection ──
0 of 10 commits flagged as possibly INTERRUPTED
  [   COMPLETE] 079f5c03  2026-06-07 20:39:08 +0100  "FFUEM fix top 3: remove dead stubs, dedupe save input, single live save path"
  [   COMPLETE] fbd57222  2026-06-07 20:05:43 +0100  "FFUEM inspection - findings saved to detective DB"
  [   COMPLETE] 635e196d  2026-06-07 19:23:58 +0100  "Resize btn-save-v2, remove 4 dead save buttons, fix Copy STATUS self-contained"
  [   COMPLETE] 022136f1  2026-06-07 17:53:59 +0100  "New self-contained SAVE MY WORK button (btn-save-v2) - bypasses broken save buttons"
  [   COMPLETE] 4acb7b72  2026-06-07 13:03:23 +0100  "Fix Save button tangle: single saveSession, direct onclick, removed conflicting handlers"
  [   COMPLETE] 4bc1b88c  2026-06-07 12:32:59 +0100  "Fix /acca/version 404 (missing /api/ prefix); verify mcc_server.py encoding is clean"
  [   COMPLETE] 44e69d8e  2026-06-07 11:53:02 +0100  "Fix Monaco block + zombie server guard + 9 broken endpoints"
  [   COMPLETE] ec117688  2026-06-07 11:37:27 +0100  "WCCS auto-save 2026-06-07 (aafl_wccs.py)"
  [   COMPLETE] b296f812  2026-06-07 11:22:57 +0100  "Full diagnostic sweep 2026-06-07"
  [   COMPLETE] a10a8854  2026-06-07 10:44:37 +0100  "WCCS auto-save 2026-06-07 (aafl_wccs.py)"

── c. CORRELATION CHECK — STATUS.md/project_awareness.json vs disk ──
Claimed-but-missing (15): REALITY_REPORT.md, VKB_SpinDoctor_Handover_vXX.md, aafl_loop.py, control_panel.py, free_providers.py, full_auto_setup.py, llow_elements.json, model_router.py, module_registry.json, project_timeline.json, quick_fix.py, retry_log.json, sesum_2026-05-28_combined.md, setup_router.py, storm_feed.json
Present-but-not-logged (20): HOW_TO_INTEGRATE_DIAGNOSTIC.py, aafl_config_reader.py, ancoreg_observer.py, ancoreg_validator.py, archive_logs.py, clacr_protocol.py, config.py, cost_predictor.py, echo_test.py, health_check.py, ibr_scanner.py, mcc_medical.py, mccm_agent.py, ocb_lifeguard_test.py, ocb_patch.py, ocb_runner_tests.py, ocb_selftest.py, promo_queue.py, run_echo_test.py, scan_old_saves.py

── d. INCOMPLETE-WORK FLAGS — half-written code scan (top-level .py) ──
Syntax errors (0): none
Duplicate function defs (0): none
Empty stub functions (0): none
TODO/FIXME left mid-edit (0): none

── e. OPEN FINDINGS — detective_report.json ──
Open findings: 33  (by severity: high=9, low=9, medium=15)

======================================================================
End of report — paste into Claude.ai Project Files or download as .md