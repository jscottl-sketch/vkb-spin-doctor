syntax = "proto3";

package machine.input;

// Keyboard event (U64 code points)
message KeyboardEvent {
  uint64 key_code = 1;
  bool     pressed = 2;
}

// Joystick axis event
message JoystickAxis {
  uint32  axis_id   = 1;
  float   value     = 2;   // -1.0 … +1.0
}

// Joystick button event
message JoystickButton {
  uint32  button_id = 1;
  bool    pressed   = 2;
}

// Composite input message – used for both GET and POST endpoints
message InputMessage {
  repeated KeyboardEvent   keyboard = 1;
  repeated JoystickAxis    axes     = 2;
  repeated JoystickButton  buttons  = 3;
}
