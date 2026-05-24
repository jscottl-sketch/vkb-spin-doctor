# FFUE Design Rules

## FFUE = Fluid, Flexible, Upgradeable, Editable

All components in this system must follow the FFUE principle.

---

## Rule: Dual-Mode Architecture

**All components must support:**

1. **Workstation mode** — local filesystem: reads/writes files directly on disk
2. **Packaged mode** — API-driven: reads/writes via HTTP API endpoints

---

## Components in Scope

| Component     | Workstation Data Layer         | Packaged Data Layer              |
|---------------|-------------------------------|----------------------------------|
| Scout         | Files in `scout_output/`      | GET/POST `/api/scout`            |
| AAFL          | `goal.txt`, `loop_output/`    | GET/POST `/api/aafl`             |
| MCC           | `STATUS.md`, `HISTORY.md`     | GET `/api/status`, `/api/history`|
| Spin Doctor   | Game binding files on disk    | GET/POST `/api/bindings`         |

---

## What This Enables

- **Develop locally** using workstation mode — full filesystem access, no server needed
- **Deploy commercially** using packaged mode — Claude Chat or external clients call API endpoints
- **No refactoring required** — same code, same logic, different data layer
- **Same code path** for Scout, AAFL, MCC, Spin Doctor regardless of environment

---

## How to Apply

When adding a new feature:
- Write it to read/write via a function parameter (path OR endpoint URL)
- Workstation default: function reads/writes the local file directly
- Packaged default: function calls the MCC server endpoint instead
- Never hardcode filesystem paths inside business logic — pass them in or resolve via config

---

*FFUE rule documented 2026-05-24 — applies to all new and refactored components*
