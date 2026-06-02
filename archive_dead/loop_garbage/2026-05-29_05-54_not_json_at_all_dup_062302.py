/v1/machine:input (GET)
  summary: Return the current synthetic input state.
  responses:
    200:
      description: Current input state.
      content:
        application/json:
          schema:
            type: object
            properties:
              keyboard:
                type: integer
                format: uint64
                description: 64‑bit bitmask of active scancodes.
              joystick:
                type: object
                properties:
                  axes:
                    type: array
                    items:
                      type: integer
                      format: uint64
                    description: Axis values (0‑65535).
                  buttons:
                    type: integer
                    format: uint64
                    description: Bitmask of pressed buttons.
            required: [keyboard, joystick]

/v1/machine:input (POST)
  summary: Inject a synthetic input state.
  requestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/InputState'
  responses:
    204: { description: Injection accepted }
    400: { description: Invalid payload }
    401: { description: Unauthorized }
