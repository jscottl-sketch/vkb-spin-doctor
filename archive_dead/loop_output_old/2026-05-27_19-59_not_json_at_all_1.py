openapi: 3.0.3
info:
  title: Machine Input API
  version: 1.0.0
servers:
  - url: /v1/machine
paths:
  /input:
    get:
      summary: Retrieve current keyboard and joystick state
      responses:
        '200':
          description: Current input snapshot
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InputState'
    post:
      summary: Inject a keyboard or joystick event (U64‑class payload)
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InputInjection'
      responses:
        '200':
          description: Injection accepted
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/InjectionResult'
        '400':
          description: Invalid payload
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'
components:
  schemas:
    InputState:
      type: object
      properties:
        device_id:
          type: integer
          format: uint64
        timestamp:
          type: integer
          format: uint64
        u64_keycode:
          type: integer
          format: uint64
        u64_joystick:
          type: integer
          format: uint64
      required: [device_id, timestamp, u64_keycode, u64_joystick]
    InputInjection:
      type: object
      properties:
        device_id:
          type: integer
          format: uint64
        timestamp:
          type: integer
          format: uint64
        u64_keycode:
          type: integer
          format: uint64
        u64_joystick:
          type: integer
          format: uint64
      required: [device_id, timestamp]
    InjectionResult:
      type: object
      properties:
        status:
          type: string
          enum: [accepted, rejected]
        detail:
          type: string
    Error:
      type: object
      properties:
        code:
          type: integer
        message:
          type: string
