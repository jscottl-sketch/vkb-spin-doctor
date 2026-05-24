# DESIGN RULES — VKB Spin Doctor / AAFL Platform
**Created:** 2026-05-24

---

## FFUE — Fluid, Flexible, Upgradeable, Editable

Every component in this platform must be:

| Property | Meaning |
|---|---|
| **Fluid** | Works without friction — no manual setup steps required per session |
| **Flexible** | No hard-coded paths or single-mode assumptions |
| **Upgradeable** | Any module can be swapped, improved, or extended without breaking others |
| **Editable** | All config, prompts, and routing are in files — never baked into code |

---

## DUAL MODE — Workstation + Packaged

All components must support two operating modes:

| Mode | Description | When Used |
|---|---|---|
| **Workstation** | Runs locally, reads from filesystem, writes directly to project files | Development, daily use on Scott's machine |
| **Packaged / API** | Runs as a service, reads from API, returns structured JSON | Future: multi-project, cloud, or shared installs |

**Rule:** The same Python file must handle both modes. Use a config flag or environment variable to switch. Never write two separate versions of the same component.

---

## COMPONENTS THIS APPLIES TO

| Component | Workstation Layer | Packaged Layer |
|---|---|---|
| Scout (chief_scout.py) | Reads filesystem, writes scout_output/ | API: POST /run-scout → GET /scout-result |
| AAFL (loop_manager.py) | Reads goal.txt, writes knowledge_engine.db | API: POST /run-aafl → GET /aafl-status |
| MCC (mission_control.html + mcc_server.py) | Serves local HTML, reads local files | API: All /api/* endpoints expose same data |
| Spin Doctor (spin_doctor.py) | Reads local game config files | API: Future — POST /fix → GET /fix-status |

---

## ADDITIONAL RULES

1. **ALP First** — Never write code that costs money without a CostGuard check.
2. **Append-only logs** — HISTORY.md and ACCA.md are never overwritten, only appended.
3. **Atomic writes** — STATUS.md is always written via atomic_write() with EOF marker check.
4. **LiteLLM routing** — All provider calls go through LiteLLM. Direct SDK calls are tech debt.
5. **Free-first** — Routing order: LM Studio local → free online (Mistral/Gemini/Cerebras) → paid fallback.
6. **One step at a time** — No stacked changes. One PR = one logical unit.

<!-- END_OF_FILE -->
