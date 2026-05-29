GET /v1/machine:input
  Summary:   Retrieve the current state of all injected keyboards and joysticks.
  Security:  ApiKeyAuth
  Responses:
    200:
      Description:  Current input snapshot.
      Content:
        application/json:
          Schema:
            type: object
            properties:
              timestamp:
                type: integer
                format: int64
                description: Epoch‑ms when snapshot was taken.
              devices:
                type: array
                items:
                  $ref: '#/components/schemas/DeviceState'

POST /v1/machine:input
  Summary:   Inject a new keyboard/joystick event batch.
  Security:  ApiKeyAuth
  RequestBody:
    required: true
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/InjectPayload'
  Responses:
    202:
      Description:  Payload accepted and queued for injection.
    400:
      Description:  Validation error – see error body.
    401:
      Description:  Invalid or missing API key.
