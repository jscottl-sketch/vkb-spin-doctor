/v1/machine:input:
  get:
    summary: Retrieve the current keyboard/joystick state
    responses:
      '200':
        description: Current state as a U64‑encoded JSON object
        content:
          application/json:
            schema:
              type: object
              required: [u64]
              properties:
                u64:
                  type: string
                  format: uint64
                  example: "0xA3F1027C00000001"
                timestamp:
                  type: string
                  format: date-time
                  description: Server time of the snapshot
      '503':
        description: State unavailable (e.g., driver not loaded)

  post:
    summary: Inject a new keyboard/joystick state (U64 class)
    security:
      - bearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required: [u64]
            properties:
              u64:
                type: string
                format: uint64
                description: 64‑bit input mask
                example: "0xFFFF0000FFFFFFFF"
    responses:
      '200':
        description: Injection succeeded
      '400':
        description: Malformed payload or out‑of‑range bits
      '401':
        description: Unauthorized – missing/invalid token
