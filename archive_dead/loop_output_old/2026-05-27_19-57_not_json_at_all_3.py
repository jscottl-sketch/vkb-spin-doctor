# src/api/input/schema.py
from marshmallow import Schema, fields, validates_schema, ValidationError

class KeyboardEventSchema(Schema):
    key_code = fields.Integer(required=True, description="USB HID key code")
    pressed  = fields.Boolean(required=True, description="True=press, False=release")

class JoystickEventSchema(Schema):
    axis   = fields.String(required=True, description="Axis identifier e.g. 'x', 'y', 'rz'")
    value  = fields.Float(required=True, description="Normalized value in [-1.0, 1.0]")

class InputPayloadSchema(Schema):
    type      = fields.String(required=True, validate=lambda s: s in ("keyboard","joystick"))
    device_id = fields.Integer(required=True, strict=True, description="U64 device identifier")
    event     = fields.Dict(required=True)

    @validates_schema
    def check_event(self, data, **kwargs):
        if data["type"] == "keyboard":
            KeyboardEventSchema().load(data["event"])
        elif data["type"] == "joystick":
            JoystickEventSchema().load(data["event"])
        else:  # should never happen because of the validator above
            raise ValidationError("Invalid type field")
