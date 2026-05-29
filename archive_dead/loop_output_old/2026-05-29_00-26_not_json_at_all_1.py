This PR introduces a versioned public REST API that allows privileged callers
to query the current keyboard/joystick state and to inject synthetic input
events into the U64 engine.

Features
--------
* `GET /v1/machine:input` – returns a snapshot of all keyboard keys and joystick
  axes/buttons.
* `POST /v1/machine:input` – accepts a validated JSON payload that describes
  keyboard presses/releases and joystick movements; events are scheduled on
  the input thread.
* OpenAPI 3.0 fragment added under `Docs/openapi.yaml`.
* Strong‑typed DTO (`InputPayloadDto`) with exhaustive validation (key range,
  axis bounds, button masks).
* CIA‑level role guard (`[Authorize(Roles = "InputInjector")]`).
* Rate‑limit (10 req/s per token) and detailed audit logging.
* Unit & integration tests covering validation, event translation and end‑to‑end
  behaviour.
* Documentation updated (README, API reference, migration guide).

This resolves issue #670 and prepares the platform for remote automation
scenarios while keeping the injection surface fully auditable.
