/v1/machine:input:
  get:
    summary: Return current input state
    parameters:
      - name: since
        in: query
        description: Return only events newer than this epoch‑ms timestamp
        schema:
          type: integer
          format: int64
    responses:
      '200':
        description: Current input state
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/InputState'
  post:
    summary: Inject keyboard or joystick events
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/InputEventBatch'
    responses:
      '200':
        description: Injection succeeded
      '400':
        description: Invalid payload
