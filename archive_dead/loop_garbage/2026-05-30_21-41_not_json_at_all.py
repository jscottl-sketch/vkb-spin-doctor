feat(api): add keyboard/joystick input REST endpoints
- GET /v1/machine:input returns current U64 state as hex
- POST /v1/machine:input accepts hex‐encoded U64 and injects it
- Implements strict validation (length, reserved bits, key‑codes, joystick axes)
- Secured with admin‑only token auth
- Thread‑safe injection via input manager
- Adds OpenAPI spec and documentation
- Unit & integration tests, CI integration
