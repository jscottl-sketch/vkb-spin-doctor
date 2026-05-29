
The handler returns `400 Bad Request` with `{ "error":"<msg>" }` when validation fails.

### 1.4 Service Integration
* Added `src/api/input_controller.cpp/h` containing two route handlers wired into the existing Fastify‑style router (`router.cpp`).

